import argparse, csv, os, json, sys
from typing import Sequence
from nbtlib import File, Compound, List, Int, Long, String


def main(args: Sequence[str] | None = None):
    """Initializes argument parser and parses arguments to then pass to `claims2nbt`.

    Args:
        args (Sequence[str], optional):
            Custom arguments to use when parsing.
            Defaults to `sys.argv[1:]` (fallback of `parse_args`).
    """
    parser = argparse.ArgumentParser(
        description="Convert per-chunk claims data into OPaC-compatible .nbt files."
    )
    parser.add_argument('claims', type=str, help='A CSV file that contains the following headers: Location, Chunk X, Chunk Z, and Dimensions.')
    parser.add_argument('--uuid', type=str, default='00000000-0000-0000-0000-000000000000', help='UUID of the user that the server claims will belong to. Defaults to Server (00000000-0000-0000-0000-000000000000)')
    parser.add_argument('-d', '--dir', target='path', type=str, default='./', help='Directory to create player-claims and player-configs data in. Defaults to CWD.')
    parsed_args = parser.parse_args(args)

    if validate_args(parsed_args) != 0:
        exit(-1)

    ret_code = claims2nbt(parsed_args.claims, parsed_args.uuid, parsed_args.path)
    exit(ret_code)


def validate_args(parsed_args: argparse.Namespace):
    """Confirm that the given command-line arguments are valid.

    - The CSV file passed for the positional argument `claims` must exist and end in `'.csv'`.
    - The UUID passed with `--uuid` option must have the format of a Minecraft UUID.

    Args:
        parsed_args (argparse.Namespace): Argument namespace produced by `argpase.parse_args()`

    Returns:
        err_code (int): If `0`, arguments are valid. Otherwise, one of the checks failed and the program should be aborted.
    """
    if not os.path.exists(parsed_args.claims):
        print(f'{parsed_args.claims} does not exist.')
        return -1
    if not parsed_args.claims.endswith('.csv'):
        print(f'{parsed_args.claims} is not a CSV file.')
        return -1
    if len(parsed_args.uuid) != 36 or parsed_args.count('-') != 4 or not all(l.isalnum() or l == '-' for l in parsed_args.uuid):
        print(f'Invalid UUID {parsed_args.uuid}.')
        return -1
    return 0


def parse_dimensions(csv_path: str):
    """Given a well-formed CSV file, generates a dictionary of chunks claimed in each dimension.

    Args:
        csv_path (str): A CSV file that contains non-empty columns "Location", "Chunk X", "Chunk Z", and "Dimension".
            Assumes that the path exists and is a .csv file.

    Returns:
        dimensions (dict): Chunks claimed in each dimension. Looks like `{dimension: [(location, x, z), ...], ...}`
    """
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


def claims2nbt(csv_path: str, uuid: str, root_dir: str) -> int:
    """Generate NBT and toml files for chunk claims specified in the CSV file.

    Two directories `player-claims` and `player-configs` will be created under `root_dir`; any missing directories in between will be created automatically.

    All chunks specified in the CSV will be claimed by the player with the `uuid`.
    Each location will be claimed using a different sub-config with the area name set to the location's name, truncated if necessary (~100).
    No other options are touched by sub-configs; common server configs are to be managed manually with the server's `main` config.
    
    Sub-configs are named using the location's name in an OPAC-compatible format. See `legalize_name`.

    Args:
        csv_path (str): Path to the CSV file.
            Must be well-formed and contain the columns "Location", "Chunk X", "Chunk Z", and "Dimension".
        uuid (str): The player or "player" that will own the claimed chunks.
        root_dir (str): Directory to store generated files in.

    Returns:
        ret_code (int): If 0, files have been created successfully. Otherwise, an error has occurred.
    """
    claims_dir = os.path.join(root_dir, "player-claims")
    os.makedirs(claims_dir, exist_ok=True)
    subconfigs_dir = os.path.join(root_dir ,'player-configs', 'sub-configs', f'{uuid}/')
    os.makedirs(subconfigs_dir, exist_ok=True)

    # parse csv
    dimensions = parse_dimensions(csv_path)
    if dimensions == -1:
        return -1

    # Generate location name to subconfig mapping on-the-fly, and create the corresponding subconfig file.
    loc_to_index: dict[str, int] = {}
    subconfig_id = 1  # Sub-configs start counting at 1

    # Generate server claim NBT file by dimension
    dimension_compounds: dict[str, Compound] = {}
    for dimension, chunks in dimensions.items():
        loc_chunks: dict[str, list[Compound]] = {}
        # Group claims by location
        # Not entirely necessary - per-chunk claims work just as well
        # This just makes the NBT structure cleaner for debugging
        for (loc, x, z) in chunks:
            if loc not in loc_to_index.keys():
                # Generate location name to subconfig mapping on-the-fly, and create the corresponding subconfig file.
                subconfig_filename = f'{legalize_name(loc)}${subconfig_id}.toml'
                with open(os.path.join(subconfigs_dir, subconfig_filename), 'w', encoding='utf-8') as f:
                    f.write(f'\n[playerConfig]\n\n	[playerConfig.claims]\n		name = "{loc[:100]}"\n\n')
                if len(loc) > 100:  # Don't think this will ever happen
                    print(f'Warning: {loc} is longer than 100 characters and will be truncated.')
                loc_to_index[loc] = subconfig_id
                subconfig_id += 1
            
            loc_chunks.setdefault(loc, []).append(
                Compound({
                    "x": Int(x),
                    "z": Int(z)
                })
            )
        # We do two passes because NBT Lists cannot append items that are not the End tag
        # thus making it impossible to add positions to the List in the pass above.
        claims = []
        for loc in loc_chunks:
            claims.append(Compound({
                "state": Compound({
                    "forceloaded": Int(0),
                    "subConfigIndex": Int(loc_to_index[loc])
                }),
                "positions": List(loc_chunks[loc]),
            }))
        dimension_compounds[dimension] = Compound({
            "claims": List(claims)
        })
    
    nbt_data = Compound({
        "confirmedActivity": Long(10200546),  # NOTE: See 'c)' at bottom.
        "username": String("Server"),
        "dimensions": Compound(dimension_compounds),
    })
    nbt_file = File(nbt_data)
    nbt_file.save(os.path.join(claims_dir, f"{uuid}.nbt"))

    print(f"Claims written to {uuid}.nbt")

    return 0


if __name__ == "__main__":
    main()

    # NOTE:
    # c) 'confirmedActivity: Long(10200546)'
    #   confiremdActivity is hardcoded set to 10200546.
    #   Untested. I have no idea how confirmedActivity works or is defined for OPaC.
    #   This value is what my user file was set to, so I am reusing it assuming it won't affect anything.
    #   The value *could* be a timestamp of sorts, but it doesn't track with epoch, gametime (ticks since world creation), or any variation of these two. 

    # TODO:
    # Write to-do section lol
    # Consider adding optional arg for player-claims filepath to write directly to world directory
