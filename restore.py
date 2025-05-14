import argparse, os, re, time, sys
from nbt import nbt
import nbtlib
from anvil import Region, Chunk, EmptyRegion
import anvil.chunk
from anvil.errors import ChunkNotFound
from anvil.versions import *

# see args at bottom of script
def restore_world(args):
    try:
        # prep
        start_time = time.perf_counter()

        original_region_dir = os.path.join(args.original, 'region')
        active_region_dir = os.path.join(args.active, 'region')
        original_entities_dir = os.path.join(args.original, 'entities')
        active_entities_dir = os.path.join(args.active, 'entities')

        claimed_chunks = None
        dimension = None
        if 'claims' in args.exclude: # find player-claims folder and load all player claim chunks into a set for later cross-referencing in restoration
            claims_dir = os.path.join(args.active, 'data', 'openpartiesandclaims', 'player-claims')
            if os.path.exists(claims_dir):
                dimension = 'minecraft:overworld'
            else: # one folder depth backwards for nether/end
                claims_dir = os.path.join(os.path.dirname(args.active), 'data', 'openpartiesandclaims', 'player-claims')
                if os.path.exists(claims_dir): 
                    dimension_name = os.path.basename(os.path.normpath(args.active))
                    if dimension_name == 'DIM-1':
                        dimension = 'minecraft:the_nether'
                    elif dimension_name == 'DIM1':
                        dimension = 'minecraft:the_end'
                else: # three folder depth backwards for custom dimensions
                    claims_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(args.active))), 'data', 'openpartiesandclaims', 'player-claims')
                    if os.path.exists(claims_dir):
                        dimension = f"minecraft:{os.path.basename(os.path.normpath(args.active))}"
                    else:
                        print("Argument '-claims' was indicated, but the player-claims folder was not found! Is your directory structure strange? Aborting...")
                        return
            claimed_chunks = claims_lookup(claims_dir, dimension)

        # end prep

        # main loop - iterate through region directories for regions, parse chunks in regions for both entities/blocks, swap out changed chunks

        print(f"Beginning restoration of {len(os.listdir(active_region_dir))} regions...")
        for idx, region_file in enumerate(os.listdir(active_region_dir), start=1):

            if not region_file.endswith('.mca'):
                print(f"({idx}/{len(os.listdir(active_region_dir))}) File {region_file} not an anvil file, skipping.")
                continue

            original_region_path = os.path.join(original_region_dir, region_file)
            active_region_path = os.path.join(active_region_dir, region_file)
            original_entities_path = os.path.join(original_entities_dir, region_file)
            active_entities_path = os.path.join(active_entities_dir, region_file)

            restore_entities = True
            if not os.path.exists(original_region_path) or os.path.getsize(original_region_path) == 0:
                print(f"({idx}/{len(os.listdir(active_region_dir))}) Region {region_file} does not exist in original world, skipping.")
                continue
            if not os.path.exists(original_entities_path) or os.path.getsize(original_entities_path) == 0:
                if args.verbose:
                    print(f"Entity region {region_file} does not exist in original world, skipping.")
                restore_entities = False
            if not is_region_diff(original_region_path, active_region_path):
                print(f"({idx}/{len(os.listdir(active_region_dir))}) Region {region_file} has unchanged modified timestamp, skipping.")
                continue

            regional_x, regional_z = get_region_coords(region_file)

            if args.boundary:
                min_x, min_z, max_x, max_z = map(int, args.boundary)
                if not (min_x <= regional_x <= max_x and min_z <= regional_z <= max_z):
                    print(f"({idx}/{len(os.listdir(active_region_dir))}) Region ({regional_x}, {regional_z}) not within allowed boundary ({min_x}, {min_z}) - ({max_x}, {max_z}), skipping.")
                    continue

            original_region = Region.from_file(original_region_path)
            active_region = Region.from_file(active_region_path)
            restored_region = EmptyRegion(regional_x, regional_z)
            if restore_entities:
                original_entities = Region.from_file(original_entities_path)
                active_entities = Region.from_file(active_entities_path)
                restored_entities = EmptyRegion(regional_x, regional_z)

            # region > chunk granularity starts here. 32x32 chunks per region
            region_start_time = time.perf_counter()
            for chunk_x in range(32):
                for chunk_z in range(32):
                    # check for active vs. original chunk. If only one exists, default to that one. Region/Entity check decoupled for sanity
                    try:
                        active_region_chunk = active_region.get_chunk(chunk_x, chunk_z)
                    except ChunkNotFound as e:
                        if args.verbose:
                            print(f"({chunk_x + chunk_z}/64) No active chunk at ({chunk_x}, {chunk_z}) found.")
                        active_region_chunk = None

                    try:
                        original_region_chunk = original_region.get_chunk(chunk_x, chunk_z)
                        if not active_region_chunk:
                            restored_region.add_chunk(original_region_chunk)
                    except ChunkNotFound as e:
                        if args.verbose:
                            print(f"({chunk_x + chunk_z}/64) No original chunk at ({chunk_x}, {chunk_z}) found.")
                        if active_region_chunk:
                            restored_region.add_chunk(active_region_chunk)
                            if args.verbose:
                                print(f"Keeping active chunk by default.")
                        else:
                            if args.verbose:
                                print(f"No active or original chunk, skipping.")
                            continue
                        original_region_chunk = None

                    if restore_entities:
                        try:
                            active_entities_chunk = active_entities.get_chunk(chunk_x, chunk_z)
                        except ChunkNotFound as e:
                            if args.verbose:
                                print(f"({chunk_x + chunk_z}/64) No active entities at ({chunk_x}, {chunk_z}) found.")
                            active_entities_chunk = None

                        try:
                            original_entities_chunk = original_entities.get_chunk(chunk_x, chunk_z)
                            if not active_entities_chunk:
                                restored_entities.add_chunk(original_entities_chunk)
                        except ChunkNotFound as e:
                            if args.verbose:
                                print(f"({chunk_x + chunk_z}/64) No original entities at ({chunk_x}, {chunk_z}) found.")
                            if active_entities_chunk:
                                restored_entities.add_chunk(active_entities_chunk)
                                if args.verbose:
                                    print(f"Keeping active entities by default.")
                            original_entities_chunk = None

                    # if both active & original exist, pass to process_chunk for additional logic to choose. Usually original is chosen.

                    if active_region_chunk and original_region_chunk:
                        process_chunk(restored_region, active_region_chunk, original_region_chunk, args, claimed_chunks=claimed_chunks)
                    if restore_entities and active_entities_chunk and original_entities_chunk:
                        process_chunk(restored_entities, active_entities_chunk, original_entities_chunk, args, claimed_chunks=claimed_chunks)
                    if args.verbose:
                        print(f"Updated chunk ({chunk_x}, {chunk_z}) in {region_file}")

            # end region > chunk loop

            print(
                f"({idx}/{len(os.listdir(active_region_dir))}) Updated region ({regional_x}, {regional_z}) in {region_file} in {time.perf_counter() - region_start_time:.3f} seconds"
            )

            if not args.preview:
                restored_region.save(active_region_path)
                original_mtime = os.path.getmtime(original_region_path)
                os.utime(active_region_path, (original_mtime, original_mtime))
                if restore_entities:
                    restored_entities.save(active_entities_path)
                    original_mtime = os.path.getmtime(original_entities_path)
                    os.utime(active_entities_path, (original_mtime, original_mtime))
            
        # end main loop

    except KeyboardInterrupt:
        print(
            f"\nWorld restoration cancelled by keyboard interrupt! Elapsed time: {time.perf_counter() - start_time:.3f} seconds."
            "Exiting..."
        )
        sys.exit(1)

    print(f"Restored the world in {args.active} to its original state in {args.original} in {time.perf_counter() - start_time:.3f} seconds")

# chunk restoration logic, currently only used for -exclude claims, but intended for more logic/exclusion cases.

def process_chunk(restored_region: EmptyRegion, active_chunk: Chunk, original_chunk: Chunk, args, claimed_chunks: set = None):
    if not args.exclude:
        restored_region.add_chunk(original_chunk)
        return
    if 'claims' in args.exclude:
        if is_claimed(active_chunk, claimed_chunks, verbose=args.verbose):
            restored_region.add_chunk(active_chunk)
            return
        else:
            restored_region.add_chunk(original_chunk)
            return
        
# helper functions

def is_claimed(chunk: Chunk, claimed_chunks: set, verbose: bool = False) -> bool:
    claimed = (chunk.x, chunk.z) in claimed_chunks
    if claimed and verbose:
        print(f"Chunk ({chunk.x}, {chunk.z}) is claimed. Skipping...")
    return claimed

def get_region_coords(filename: str):
    match = re.fullmatch(r"r\.(-?\d+)\.(-?\d+)\.mca", filename)
    if not match:
        raise ValueError(
            f"Filename '{filename}' does not match expected format. " 
            "Expected format is 'r.<region_x>.<region_z>.mca' (e.g., 'r.0.0.mca' or 'r.-1.5.mca')."
        )
    region_x, region_z = map(int, match.groups())
    return region_x, region_z

def is_region_diff(original_region_path: str, active_region_path: str) -> bool:
    original_mtime = os.path.getmtime(original_region_path)
    active_mtime = os.path.getmtime(active_region_path)

    return original_mtime != active_mtime

# exclude 'claims' helper functions

excluded_players = [ # specify static player ids to exclude from restore protection
    '00000000-0000-0000-0000-000000000000', # 'Server' player
    '00000000-0000-0000-0000-000000000001', # 'Expiration' player
]

def claims_lookup(claims_dir: str, dimension: str) -> set:
    claimed_chunks = set()

    for filename in os.listdir(claims_dir):
        if any(excluded_id in filename for excluded_id in excluded_players):
            continue
        if not filename.endswith('.nbt'):
            continue

        claim_path = os.path.join(claims_dir, filename)
        try:
            claim_data = nbtlib.load(claim_path)
        except Exception as e:
            print(f"Error reading the following player's claim data: '{filename}': {e}")
            continue
        
        dimension_list = claim_data.get('dimensions')
        if not dimension_list:
            continue

        for dimension_name, dimension_data in dimension_list.items():
            if dimension == dimension_name:
                claims = dimension_data.get('claims')
                if claims is None:
                    continue

                for compound in claims:
                    positions = compound.get('positions')
                    if not positions:
                        continue

                    for position in positions:
                        try:
                            chunk_x = int(position.get('x'))
                            chunk_z = int(position.get('z'))
                            claimed_chunks.add((chunk_x, chunk_z))
                        except (ValueError, TypeError) as e:
                            print(f"Invalid chunk state position data in file '{filename}': {e}")
                            continue               
    return claimed_chunks

# this override is so anvil-parser2's Chunk can parse chunks in the 'entities' folder, which use Position instead of xPos/zPos in NBT.
# do *not* use block-related functions on entity chunks. Very much a bandaid fix that happens to work.
# Effectively the source of any issues that involve entities and not regions.
class Chunk(Chunk):
    __slots__ = ("version", "data", "x", "z", "tile_entities")
    def __init__(self, nbt_data: nbt.NBTFile):
        try:
            self.version = nbt_data["DataVersion"].value
        except KeyError:
            self.version = VERSION_PRE_15w32a

        if self.version >= VERSION_21w43a:
            self.data = nbt_data
            if "block_entities" in self.data:
                self.tile_entities = self.data["block_entities"]
            elif "Entities" in self.data:
                self.tile_entities = self.data["Entities"]
            else:
                self.tile_entities = [] 

        else:
            try:
                self.data = nbt_data["Level"]
                if "TileEntities" in self.data:
                    self.tile_entities = self.data["TileEntities"]
            except Exception:
                self.data = nbt_data
                if "TileEntities" in self.data:
                    self.tile_entities = self.data["TileEntities"]
                else:
                    self.tile_entities = self.data.get("Entities", [])


        if (("xPos" not in nbt_data) or ("zPos" not in nbt_data)):
            try: # entity files use position
                self.x = self.data["Position"].value[0]
                self.z = self.data["Position"].value[1]
            except KeyError: # sometimes some entity files are magically dataversion 2730 and mystically have an extra layer compound with no key.
                self.x = self.data[""]["Position"].value[0]
                self.z = self.data[""]["Position"].value[1]
        else: # region files use xpos zpos
            self.x = self.data["xPos"].value
            self.z = self.data["zPos"].value
anvil.Chunk = Chunk

# cli org

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Another strike of the clock, another iteration of the world, Drehmal rewinds, under the whims of the Mythoclast...",
        epilog=("Examples:\n",
                "  python script.py -o \".minecraft/saves/ogDrehmal\" -a \".minecraft/saves/actDrehmal\" --exclude claims -b -12 -11 14 15 -v -p \n\n",
                "Note that -original and -active arguments are required string paths to the associated world directories. Backslashes not to be included."),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-o', '--original', required=True, help='Path to original state/world directory. Contains "region" and "entities" folder.')
    parser.add_argument('-a', '--active', required=True, help='Path to active world directory. Contains "region" and "entities" folder.')
    parser.add_argument('-e', '--exclude', nargs='*', type=str, choices=['claims'], default=[], help='in form "--exclude claims *". Indicates what features to exclude from restoration.')
    parser.add_argument('-b', '--boundary', nargs=4, type=int, help='in form "--boundary minX minY maxX maxY". Indicates a drawn boundary box such that regions outside the box are not restored, only those within. Expects REGIONAL coordinates.')
    parser.add_argument('-p', '--preview', action='store_true', help='Preview changes without saving.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Add some extra print messages to see active progress. Any messages included in verbose are typically not very useful.')
    args = parser.parse_args()

    #TODO:
    # 2. Avoid restoring loot
    #   Exclusively restore blocks but not chest item data.
    #   Unsure how to do this without drastically upping complexity. 
    #   Necessary if loot-regeneration will be handled differently than block regeneration.
    # Currently restores all blocks, including chest and chest item data.

    # 3. Command blocks/Drehmal stuff
    #   How to handle command blocks/special moving structures in Drehmal?
    #   Like moving doors, animated things like Khive Rings, Lo'Dahr teleport gates, Yavh'Lix door, Water snake?
    #   Unsure if restoration will outright break things or not. No idea.
    # Currently does not even think about this. Not a thought.

    # 4. Add verbosity to a lot of functions for test casing
    #   Not super complicated and not helpful for actual large world restoration as it results in hundreds of lines,
    #   but would be helpful for small world restoration testing to identify unintended behavior later on.

    # 5. Optimizing anvil-parser2
    #   Currently anvil-parser2 is unmaintained and is really hard to use.
    #   get_chunk is only handled by thrown exceptions, which is slow and looks like a mess frankly
    #   The library as a whole isn't designed for entity chunks, which is more of our fault for use case, but can be fixed.

    restore_world(args)
