import argparse, csv, os, json
from nbtlib import File, Compound, List, Int, Long, String


def claims2nbt(args):
    # find csv in current directory
    csv_path: str = args.claims
    if not os.path.exists(csv_path):
        print(f'{csv_path} does not exist. Aborting.')
        exit(-1)
    if not csv_path.endswith('.csv'):
        print(f'{csv_path} is not a CSV file. Aborting.')
        exit(-1)

    print(f'Using {csv_path}.')

    claims_dir = "player-claims"
    os.makedirs(claims_dir, exist_ok=True)
    configs_dir = "player-configs"
    os.makedirs(configs_dir, exist_ok=True)

    # parse csv and write dict
    locations = {}
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            loc = row["Location"]
            x = int(row["Chunk X"])
            z = int(row["Chunk Z"])
            dimension = row["Dimension"]
            locations.setdefault(loc, []).append((x, z, dimension))

    # load default config for server claims
    with open('protection-disabled.toml', 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # UUID -> Location name mapping for restore.py to read
    mapping: dict[str, str] = {
        '00000000-0000-0000-0000-000000000000': 'Server',
        '00000000-0000-0000-0000-000000000001': 'Expired'
    }

    # loop through all locations
    for idx, (loc, coords) in enumerate(locations.items()):
        # (a)
        #   Counter starts at 2 when naming .nbt files because 0 and 1 are reserved.
        #   `00000000-0000-0000-0000-000000000000.nbt` is Server claims.
        #   `00000000-0000-0000-0000-000000000001.nbt` is Expiration claims.
        counter = 2 + idx
        # (b)
        #   .nbt files are named only using the final 12-digit suffix.
        #   This is because starting at such a low number reduces the chances a random player
        #   coincidentally matches the uuid of a file we're using for server claims.
        #   We only use the suffix because 12 digits is insanely more than we need.
        #   We effectively won't run out of digits/filenames unless we name >1 trillion locations in the .csv
        uuid = f"00000000-0000-0000-0000-{counter:012d}"

        # construct claim NBT
        dimensions = {}
        for x, z, dimension in coords:
            dimensions.setdefault(dimension, []).append((x, z))
        dimension_compounds = {
            dimension: Compound(
                {
                    "claims": List(
                        [
                            Compound(
                                {
                                    "state": Compound(
                                        {"forceloaded": Int(0), "subConfigIndex": Int(-1)}
                                    ),  # NOTE: see 'd)' at bottom.
                                    "positions": List([Compound({"x": Int(x), "z": Int(z)}) for (x, z) in coords]),
                                }
                            )
                        ]
                    )
                }
            )
            for dimension, coords in dimensions.items()
        }
        nbt_data = Compound(
            {
                "confirmedActivity": Long(10200546),  # NOTE: See 'c)' at bottom.
                "username": String(loc),
                "dimensions": Compound(dimension_compounds),
            }
        )

        # write nbt file
        nbt_file = File(nbt_data)
        nbt_file.save(os.path.join(claims_dir, f"{uuid}.nbt"))

        # write config file
        with open(os.path.join(configs_dir, f"{uuid}.toml"), 'w', encoding='utf-8') as f:
            f.write(config_content)

        print(f"Claims for location '{loc}' written to {uuid}.nbt")

        mapping[uuid] = loc
    
    with open(os.path.join(args.mapfiledir, 'uuid_mapping.json'), 'w', encoding='utf-8') as f:
        json.dump(mapping, f)
        print(f"UUID map saved to {os.path.join(args.mapfiledir, 'uuid_mapping.json')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert per-chunk claims data into OPaC-compatible .nbt files."
    )
    parser.add_argument('claims', type=str, help='A CSV file that contains the following headers: Location, Chunk X, Chunk Z, and Dimensions.')
    parser.add_argument('--mapfiledir', type=str, default='./', help='Path to store the UUID mapping file. Defaults to CWD')
    args = parser.parse_args()

    claims2nbt(args)

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
    # Change csv check to abort on multiple .csv
    # Add correct error throws/behaviors if csv parse doesn't find correct headers
    # Consider adding optional arg for player-claims filepath to write directly to world directory
