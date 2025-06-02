import argparse, csv, os
from nbtlib import File, Compound, List, Int, Long, String


def claims2nbt(args):
    # find csv in current directory
    csv_files = [f for f in os.listdir(".") if f.lower().endswith(".csv")]
    if not csv_files:
        raise FileNotFoundError("No .csv file found in the current directory.")
    csv_path = csv_files[0]

    claims_dir = "player-claims"
    os.makedirs(claims_dir, exist_ok=True)

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

    # write nbt files
    counter = 2  # NOTE: See 'a)' at bottom.
    for loc, coords in locations.items():
        uuid_suffix = f"{counter:012d}"
        filename = f"00000000-0000-0000-0000-{uuid_suffix}.nbt"  # NOTE: See 'b)' at bottom.
        output_path = os.path.join(claims_dir, filename)

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

        nbt_file = File(nbt_data)
        nbt_file.save(output_path)
        print(f"Wrote NBT for location '{loc}' to {output_path}")
        counter += 1


# cli org

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run in same folder as .csv with headers Location, Chunk X, Chunk Z, and Dimensions. Generates folder of OPaC-compatible .nbt files."
    )
    args = parser.parse_args()

    claims2nbt(args)

    # NOTE:
    # a) 'counter = 2'
    #   Counter starts at 2 when naming .nbt files because 0 and 1 are reserved.
    #   `00000000-0000-0000-0000-000000000000.nbt` is Server claims.
    #   `00000000-0000-0000-0000-000000000001.nbt` is Expiration claims.

    # b) 'uuid-suffix'
    #   .nbt files are named only using the final 12-digit suffix.
    #   This is because starting at such a low number reduces the chances a random player
    #   coincidentally matches the uuid of a file we're using for server claims.
    #   We only use the suffix because 12 digits is insanely more than we need.
    #   We effectively won't run out of digits/filenames unless we name >1 trillion locations in the .csv

    # c) 'confirmedActivity: Long(10200546)'
    #   confiremdActivity is hardcoded set to 10200546.
    #   Untested. I have no idea how confirmedActivity works or is defined for OPaC.
    #   This value is what my user file was set to, so I am reusing it assuming it won't affect anything.

    # d) 'state: Compound({forceloaded: Int(0), subConfigIndex: Int(-1)})'
    #   State compound is hardcoded to these for now.
    #   Will need to update later when we configure the correct configs for server-factions.

    # TODO:
    # Write to-do section lol
    # Change csv check to abort on multiple .csv
    # Add correct error throws/behaviors if csv parse doesn't find correct headers
    # Consider adding optional arg for player-claims filepath to write directly to world directory
