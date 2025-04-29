import argparse, os, re, time, sys
from nbt import nbt
import nbtlib
from anvil import Region, Chunk, EmptyRegion
import anvil.chunk
from anvil.errors import ChunkNotFound
from anvil.versions import *

def restore_world(args):
    try:
        start_time = time.perf_counter()

        original_region_dir = os.path.join(args.original, 'region')
        active_region_dir = os.path.join(args.active, 'region')
        original_entities_dir = os.path.join(args.original, 'entities')
        active_entities_dir = os.path.join(args.active, 'entities')

        claims_data = None
        dimension = None
        if 'claims' in args.exclude:
            try: # find claim.dat for any dimension
                claims_data = nbtlib.load(os.path.join(os.path.dirname(os.path.dirname(args.active)), 'factions', 'claim.dat')).get('CORE')
                dimension = 'minecraft:overworld'
            except FileNotFoundError:
                try: 
                    claims_data = nbtlib.load(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(args.active)))), 'factions', 'claim.dat')).get('CORE')
                    dimension_name = os.path.basename(os.path.normpath(args.active))
                    if dimension_name == 'DIM-1':
                        dimension = 'minecraft:the_nether'
                    elif dimension_name == 'DIM1':
                        dimension = 'minecraft:the_end'
                except FileNotFoundError:
                    try:
                        claims_data = nbtlib.load(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(args.active))))), 'factions', 'claim.dat')).get('CORE')
                        dimension = f"minecraft:{os.path.basename(os.path.normpath(args.active))}"
                    except FileNotFoundError:
                        print("No valid claim.dat file found for active world. Verify that there is a factions folder in at the game directory level. Aborting...")
                        return
            if claims_data is None:
                print("File at claim.dat does not have a CORE list of chunks. Verify NBT file structure and try again. Aborting...")
                return
            claims_data = claims_lookup(claims_data, dimension)

        print(f"Beginning restoration of {len(os.listdir(active_region_dir))} regions...")
        for idx, region_file in enumerate(os.listdir(active_region_dir), start=1):

            if not region_file.endswith('.mca'):
                print(f"({idx}/{len(os.listdir(active_region_dir))}) File {region_file} not an anvil file, skipping.")
                continue

            original_region_path = os.path.join(original_region_dir, region_file)
            active_region_path = os.path.join(active_region_dir, region_file)
            original_entities_path = os.path.join(original_entities_dir, region_file)
            active_entities_path = os.path.join(active_entities_dir, region_file)
            
            if not os.path.exists(original_region_path):
                print(f"({idx}/{len(os.listdir(active_region_dir))}) Region {region_file} does not exist in original world, skipping.")
                continue
            elif not is_region_diff(original_region_path, active_region_path):
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
            original_entities = Region.from_file(original_entities_path)
            active_entities = Region.from_file(active_entities_path)
            restored_entities = EmptyRegion(regional_x, regional_z)

            region_start_time = time.perf_counter()
            for chunk_x in range(32):
                for chunk_z in range(32):
                    try:
                        original_region_chunk = original_region.get_chunk(chunk_x, chunk_z)
                        original_entities_chunk = original_entities.get_chunk(chunk_x, chunk_z)
                    except ChunkNotFound as e:
                        if args.verbose:
                            print(f"({chunk_x + chunk_z}/64) No original chunk at ({chunk_x}, {chunk_z}) found, skipping.")
                        continue

                    try:
                        active_region_chunk = active_region.get_chunk(chunk_x, chunk_z)
                        active_entities_chunk = active_entities.get_chunk(chunk_x, chunk_z)
                    except ChunkNotFound as e:
                        restored_region.add_chunk(original_region_chunk)
                        restored_entities.add_chunk(original_entities_chunk)
                        if args.verbose:
                            print(f"({chunk_x + chunk_z}/64) No active chunk at ({chunk_x}, {chunk_z}) found, replacing with original region.")
                        continue

                    process_chunk(restored_region, active_region_chunk, original_region_chunk, args, claims_data=claims_data)
                    process_chunk(restored_entities, active_entities_chunk, original_entities_chunk, args, claims_data=claims_data)
                    if args.verbose:
                        print(f"Updated chunk ({chunk_x}, {chunk_z}) in {region_file}")
            print(
                f"({idx}/{len(os.listdir(active_region_dir))}) Updated region ({regional_x}, {regional_z}) in {region_file} in {time.perf_counter() - region_start_time:.3f} seconds"
            )

            if not args.preview:
                restored_region.save(active_region_path)
                original_mtime = os.path.getmtime(original_region_path)
                os.utime(active_region_path, (original_mtime, original_mtime))
                restored_entities.save(active_entities_path)
                original_mtime = os.path.getmtime(original_entities_path)
                os.utime(active_entities_path, (original_mtime, original_mtime))

    except KeyboardInterrupt:
        print(
            f"\nWorld restoration cancelled by keyboard interrupt! Elapsed time: {time.perf_counter() - start_time:.3f} seconds."
            "Exiting..."
        )
        sys.exit(1)

    print(f"Restored the world in {args.active} to its original state in {args.original} in {time.perf_counter() - start_time:.3f} seconds")

# chunk restoration logic, add more accordingly to --exclude

def process_chunk(restored_region: EmptyRegion, active_chunk: Chunk, original_chunk: Chunk, args, claims_data=None):
    if not args.exclude:
        restored_region.add_chunk(original_chunk)
        return
    if 'claims' in args.exclude:
        if is_claimed(active_chunk, claims_data):
            return
        else:
            restored_region.add_chunk(original_chunk)
            return
        
# helper functions

def is_claimed(chunk: Chunk, claims_data) -> bool:
    claimed = (chunk.x, chunk.z) in claims_data
    if claimed and args.verbose:
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

def claims_lookup(claims_data, dimension):
    lookup = {}
    for claim in claims_data:
        x = claim.get('X')
        z = claim.get('Z')
        if claim.get('Level') == dimension:
            lookup[(x, z)] = claim
    return lookup

# this override is so anvil-parser2's Chunk can parse chunks in the 'entities' folder, which use Position instead of xPos/zPos.
# do *not* use block-related commands on entity chunks.
class Chunk(Chunk):
    __slots__ = ("version", "data", "x", "z", "tile_entities")
    def __init__(self, nbt_data: nbt.NBTFile):
        try:
            self.version = nbt_data["DataVersion"].value
        except KeyError:
            self.version = VERSION_PRE_15w32a

        if self.version >= VERSION_21w43a:
            self.data = nbt_data
            try:
                self.tile_entities = self.data["block_entities"]
            except KeyError:
                self.tile_entities = self.data["Entities"]
        else:
            self.data = nbt_data["Level"]
            self.tile_entities = self.data["TileEntities"]

        if (("xPos" not in nbt_data) or ("zPos" not in nbt_data)):
            self.x = self.data["Position"].value[0]
            self.z = self.data["Position"].value[1]
        else:
            self.x = self.data["xPos"].value
            self.z = self.data["zPos"].value
anvil.Chunk = Chunk

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Another strike of the clock, another iteration of the world, Drehmal rewinds, under the whims of the Mythoclast...')
    parser.add_argument('-o', '--original', required=True, help='Path to original state/world directory. Contains "region" and "entities" folder.')
    parser.add_argument('-a', '--active', required=True, help='Path to active world directory. Contains "region" and "entities" folder.')
    parser.add_argument('-e', '--exclude', nargs='*', type=str, choices=['claims'], default=[], help='in form "--exclude claims *". Indicates what features to exclude from restoration.')
    parser.add_argument('-b', '--boundary', nargs=4, type=int, help='in form "--boundary minX minY maxX maxY". Indicates a drawn boundary box such that regions outside the box are not restored, only those within. Expects REGIONAL coordinates.')
    parser.add_argument('-p', '--preview', action='store_true', help='Preview changes without saving.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Add some extra print messages to see active progress. Any messages included in verbose are typically not very useful.')
    args = parser.parse_args()

    #TODO:
    # 1. exclude specific factions from being protected in --exclude claims
    #   This allows us to exclude factions/selectively restore some faction claimed land. Useful for npc factions so we can 'claim' something to prevent players from claiming it,
    #   but still restore those places despite being claimed. Good ideas are legendary chests, important locations like towns, ruins, etc.
    #   Allows for 'permanently regenerating lands' which can't be taken out of the restoration loop if by a player claiming it.
    # Currently excludes all factions, no matter what.

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

    restore_world(args)
