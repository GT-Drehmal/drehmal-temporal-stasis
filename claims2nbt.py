import argparse, csv, os, json, sys
from typing import Literal
from nbtlib import File, Compound, List, Int, Long, String


def main(args):
    parser = argparse.ArgumentParser(
        description="Convert per-chunk claims data into OPaC-compatible .nbt files."
    )
    parser.add_argument('claims', type=str, help='A CSV file that contains the following headers: Location, Chunk X, Chunk Z, and Dimensions.')
    parser.add_argument('--mapfiledir', type=str, default='./', help='Path to store the UUID mapping file. Defaults to CWD')
    parsed_args = parser.parse_args(args)

    ret_code = claims2nbt(parsed_args.csv_path, parsed_args.mapfiledir)
    exit(ret_code)

def get_locations(csv_path: str) -> dict[str, list[tuple[int, int, str]]] | Literal[-1]:
    if not os.path.exists(csv_path):
        print(f'{csv_path} does not exist.')
        return -1
    if not csv_path.endswith('.csv'):
        print(f'{csv_path} is not a CSV file.')
        return -1
    print(f'Using {csv_path}.')

    locations: dict[str, list[tuple[int, int, str]]] = {}
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not all(h in row.keys() for h in ("Location", "Chunk X", "Chunk Z", "Dimension")):
                print(f'The supplied CSV file {csv_path} is malformed.')
                return -1
            loc: str = row["Location"]
            x = int(row["Chunk X"])
            z = int(row["Chunk Z"])
            dimension: str = row["Dimension"]
            locations.setdefault(loc, []).append((x, z, dimension))

        if reader.line_num == 0:
            print('Empty CSV file.')
            return -1
        
    return locations


def parse_dimensions(csv_path: str):
    """Given a well-formed CSV file, generates a dictionary of chunks claimed in each dimension.

    Args:
        csv_path (str): A CSV file that contains non-empty columns "Location", "Chunk X", "Chunk Z", and "Dimension".

    Returns:
        dimensions (dict): Chunks claimed in each dimension. Looks like `{dimension: [(location, x, z), ...], ...}`
    """
    if not os.path.exists(csv_path):
        print(f'{csv_path} does not exist.')
        return -1
    if not csv_path.endswith('.csv'):
        print(f'{csv_path} is not a CSV file.')
        return -1
    print(f'Using {csv_path}.')

    dimensions: dict[str, list[tuple[str, int, int]]] = {}
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not all(h in row.keys() for h in ("Location", "Chunk X", "Chunk Z", "Dimension")):
                print(f'The supplied CSV file {csv_path} is malformed.')
                return -1
            loc: str = row["Location"]
            x = int(row["Chunk X"])
            z = int(row["Chunk Z"])
            dimension: str = row["Dimension"]
            dimensions.setdefault(dimension, []).append((loc, x, z))

        if reader.line_num == 0:
            print('Empty CSV file.')
            return -1
        
    return dimensions


def legalize_name(name: str) -> str:
    """Convert a location name to one that can be used as a sub-config's ID. Spaces are changed into '-' and any non-alphanumerical characters are changed into '_'. If longer than 16 chars, truncates down to 16.

    > The sub-config ID must be unique, at most 16 characters long and consist of English letters (A-Z), numbers (0-9) or the '-' and '_' characters.

    Args:
        name (str): Name of a location.

    Returns:
        legalized_name (str): Converted name that follows sub-config ID requirements.
    """
    legalized_name = ''
    for l in name[:16]:
        if l.isalnum():
            legalized_name += l
        elif l == ' ':
            legalized_name += '-'
        else:
            legalized_name += '_'
    return legalized_name


def claims2nbt(csv_path: str, mapfiledir: str) -> int:
    claims_dir = "player-claims"
    os.makedirs(claims_dir, exist_ok=True)
    subconfigs_dir = os.path.join('player-configs', 'sub-configs', '00000000-0000-0000-0000-000000000000/')
    os.makedirs(subconfigs_dir, exist_ok=True)
    
    # parse csv
    # locations = get_locations(csv_path)
    # if locations == -1:
    #     return -1
    dimensions = parse_dimensions(csv_path)
    if dimensions == -1:
        return -1

    # load and write default config for server claims
    with open('protection-disabled.toml', 'r', encoding='utf-8') as f:
        config_content = f.read()
    with open(os.path.join("player-configs", '00000000-0000-0000-0000-000000000000.toml'), 'w', encoding='utf-8') as f:
        f.write(config_content)

    # Generate location name to subconfig mapping on-the-fly, and create the corresponding subconfig file.
    loc_to_index: dict[str, int] = {}
    subconfig_id = 1  # Sub-configs start counting at 1

    # Generate server claim NBT file by dimension
    dimension_compounds = Compound({})
    for dimension, chunks in dimensions.items():
        loc_chunks: dict[str, List] = {}
        # Group claims by location
        # Not entirely necessary - per-chunk claims work just as well
        # This just makes the NBT structure cleaner for debugging
        for (loc, x, z) in chunks:
            if loc not in loc_to_index.keys():
                # Generate location name to subconfig mapping on-the-fly, and create the corresponding subconfig file.
                subconfig_filename = f'{legalize_name(loc)}${subconfig_id}.toml'
                with open(os.path.join(subconfigs_dir, subconfig_filename), 'w', encoding='utf-8') as f:
                    f.write(f'\n[playerConfig]\n\n	[playerConfig.claims]\n		name = "{loc}"\n\n')
                loc_to_index[loc] = subconfig_id
                subconfig_id += 1
            
            loc_chunks.setdefault(loc, List([])).append(
                Compound({
                    "x": Int(x),
                    "z": Int(z)
                })
            )
        # We do two passes for simplicity's sake
        claims = List([])
        for loc in loc_chunks:
            claims.append(Compound({
                "state": Compound({
                    "forceloaded": Int(0),
                    "subConfigIndex": Int(loc_to_index[loc])
                }),
                "positions": loc_chunks[loc],
            }))
        dimension_compounds[dimension] = Compound({
            "claims": claims
        })
    
    nbt_data = Compound({
        "confirmedActivity": Long(10200546),  # NOTE: See 'c)' at bottom.
        "username": "Server",
        "dimensions": dimension_compounds,
    })
    # write nbt file
    nbt_file = File(nbt_data)
    nbt_file.save(os.path.join(claims_dir, "00000000-0000-0000-0000-000000000000.nbt"))

    print(f"Claims written to 00000000-0000-0000-0000-000000000000.nbt")

    return 0


if __name__ == "__main__":
    main(sys.argv)

    # NOTE:
    # c) 'confirmedActivity: Long(10200546)'
    #   confiremdActivity is hardcoded set to 10200546.
    #   Untested. I have no idea how confirmedActivity works or is defined for OPaC.
    #   This value is what my user file was set to, so I am reusing it assuming it won't affect anything.
    #   The value *could* be a timestamp of sorts, but it doesn't track with epoch, gametime (ticks since world creation), or any variation of these two. 

    # d) 'state: Compound({forceloaded: Int(0), subConfigIndex: Int(-1)})'
    #   State compound is hardcoded to these for now.
    #   Will need to update later when we configure the correct configs for server-factions.

    # TODO:
    # Write to-do section lol
    # Add correct error throws/behaviors if csv parse doesn't find correct headers
    # Consider adding optional arg for player-claims filepath to write directly to world directory
