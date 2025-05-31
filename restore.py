import argparse
import os, re, time, sys, random
import logging
from tqdm.std import tqdm as std_tqdm
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib
from typing import Union
from nbt import nbt
import nbtlib
from anvil import Region, Chunk, EmptyRegion # type: ignore
import anvil.chunk
from anvil.versions import *
from anvil.errors import ChunkNotFound

# see args at bottom of script
def restore_dimension() -> int:
    if not os.path.exists(parsed_args.original) or not os.path.exists(parsed_args.active):
        logger.error('One or both of the given world directories does not exist. Aborting.')
        return -1
    
    try:
        # prep
        start_time = time.perf_counter()
        logger.debug(f'restore_world started at {start_time}.')

        original_region_dir = os.path.join(parsed_args.original, 'region')
        active_region_dir = os.path.join(parsed_args.active, 'region')
        original_entities_dir = os.path.join(parsed_args.original, 'entities')
        active_entities_dir = os.path.join(parsed_args.active, 'entities')

        claimed_chunks = None
        dimension = None
        if 'claims' in parsed_args.exclude: # find player-claims folder and load all player claim chunks into a set for later cross-referencing in restoration
            claims_dir = os.path.join(parsed_args.active, 'data', 'openpartiesandclaims', 'player-claims')
            if os.path.exists(claims_dir):
                dimension = 'minecraft:overworld'
            else: # one folder depth backwards for nether/end
                claims_dir = os.path.join(os.path.dirname(parsed_args.active), 'data', 'openpartiesandclaims', 'player-claims')
                if os.path.exists(claims_dir): 
                    dimension_name = os.path.basename(os.path.normpath(parsed_args.active))
                    if dimension_name == 'DIM-1':
                        dimension = 'minecraft:the_nether'
                    elif dimension_name == 'DIM1':
                        dimension = 'minecraft:the_end'
                else: # three folder depth backwards for custom dimensions
                    claims_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(parsed_args.active))), 'data', 'openpartiesandclaims', 'player-claims')
                    if os.path.exists(claims_dir):
                        dimension = f"minecraft:{os.path.basename(os.path.normpath(parsed_args.active))}"
                    else:
                        logger.error("Argument '-claims' was indicated, but the player-claims folder was not found! Is your directory structure strange? Aborting...")
                        return -1
            claimed_chunks = claims_lookup(claims_dir, dimension)

        # end prep

        if parsed_args.preview:
            logger.warning(f'Running under PREVIEW mode. No changes will be committed to the files.')
        logger.info(f"Beginning restoration of {len(os.listdir(active_region_dir))} regions...")

        # iterate through region directories for regions, parse chunks in regions for both entities/blocks, swap out changed chunks
        tasks = []
        for idx, region_file in enumerate(os.listdir(active_region_dir), start=1):
            if not region_file.endswith('.mca'):
                logger.info(f"Skipping non-anvil file {region_file}")
                continue
            tasks.append(
                delayed(restore_region)(
                    original_region_dir,
                    active_region_dir,
                    original_entities_dir,
                    active_entities_dir,
                    claimed_chunks,
                    idx,
                    region_file
                )
            )

        with tqdm_joblib(
            desc="Restoration progress",
            total=len(tasks),
            unit='reg',
            dynamic_ncols=True,
            colour=f'#{random.randint(0, 16777215):06x}'
        ) as _:
            n_jobs = os.cpu_count()
            Parallel(n_jobs=n_jobs, backend='loky', prefer='processes')(tasks)

    except KeyboardInterrupt:
        logger.exception(f"World restoration cancelled by keyboard interrupt! Elapsed time: {time.perf_counter() - start_time:.3f} seconds. Exiting...")
        return 1
    logger.info(f"Restored {dimension} at {parsed_args.active} to its original state at {parsed_args.original} in {time.perf_counter() - start_time:.3f} seconds")
    return 0

def restore_region(
        original_region_dir: str,
        active_region_dir: str,
        original_entities_dir: str,
        active_entities_dir: str,
        claimed_chunks: set,
        idx: int,
        region_file: nbt.NBTFile
) -> int:
    logger = logger_init(f'restore.region.{idx}')
    original_region_path = os.path.join(original_region_dir, region_file)
    active_region_path = os.path.join(active_region_dir, region_file)
    original_entities_path = os.path.join(original_entities_dir, region_file)
    active_entities_path = os.path.join(active_entities_dir, region_file)

    if not os.path.exists(original_region_path):
        logger.info(f"Region {region_file} does not exist in original world, skipping.")
        return 1
    elif os.path.getsize(original_region_path) == 0:
        logger.info(f"Skipping empty region file {region_file}.")
        return 1
    elif not region_modified(original_region_path, active_region_path):
        logger.info(f"Skipping unmodified region file {region_file}.")
        return 1

    if not os.path.exists(original_entities_path) or os.path.getsize(original_entities_path) == 0:
        logger.info(f"Entity region {region_file} does not exist in original world, skipping.")
        restore_entities = False
    else:
        restore_entities = True

    regional_x, regional_z = get_region_coords(region_file)

    if parsed_args.boundary:
        min_x, min_z, max_x, max_z = map(int, parsed_args.boundary)
        if not (min_x <= regional_x <= max_x and min_z <= regional_z <= max_z):
            logger.info(f"Region ({regional_x}, {regional_z}) not within allowed boundary ({min_x}, {min_z}) - ({max_x}, {max_z}), skipping.")
            return 1

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
                active_region_chunk = Chunk.from_region(active_region, chunk_x, chunk_z)
            except ChunkNotFound as e:
                logger.debug(f"({chunk_x + chunk_z}/64) No active chunk at ({chunk_x}, {chunk_z}) found.")
                active_region_chunk = None

            try:
                original_region_chunk = Chunk.from_region(original_region, chunk_x, chunk_z)
                if not active_region_chunk:
                    restored_region.add_chunk(original_region_chunk)
            except ChunkNotFound as e:
                logger.debug(f"({chunk_x + chunk_z}/64) No original chunk at ({chunk_x}, {chunk_z}) found.")
                if active_region_chunk:
                    restored_region.add_chunk(active_region_chunk)
                    logger.debug(f"Keeping active chunk by default.")
                else:
                    logger.debug(f"No active or original chunk, skipping.")
                    continue
                original_region_chunk = None

            if restore_entities:
                try:
                    active_entities_chunk = Chunk.from_region(active_entities, chunk_x, chunk_z)
                except ChunkNotFound:
                    logger.debug(f"({chunk_x + chunk_z}/64) No active entities at ({chunk_x}, {chunk_z}) found.")
                    active_entities_chunk = None

                try:
                    original_entities_chunk = Chunk.from_region(original_entities, chunk_x, chunk_z)
                    if not active_entities_chunk:
                        restored_entities.add_chunk(original_entities_chunk)
                except ChunkNotFound:
                    logger.debug(f"({chunk_x + chunk_z}/64) No original entities at ({chunk_x}, {chunk_z}) found.")
                    if active_entities_chunk:
                        restored_entities.add_chunk(active_entities_chunk)
                        logger.debug(f"Keeping active entities by default.")
                    original_entities_chunk = None

            # if both active & original exist, pass to process_chunk for additional logic to choose. Usually original is chosen.
            if active_region_chunk and original_region_chunk:
                add_chunk_if_not_excluded(restored_region, active_region_chunk, original_region_chunk, claimed_chunks=claimed_chunks)
            if restore_entities and active_entities_chunk and original_entities_chunk:
                add_chunk_if_not_excluded(restored_entities, active_entities_chunk, original_entities_chunk, claimed_chunks=claimed_chunks)
            logger.debug(f"Updated chunk ({chunk_x}, {chunk_z}) in {region_file}")

    # end region > chunk loop

    if not parsed_args.preview:
        restored_region.save(active_region_path)
        original_mtime = os.path.getmtime(original_region_path)
        os.utime(active_region_path, (original_mtime, original_mtime))
        if restore_entities:
            restored_entities.save(active_entities_path)
            original_mtime = os.path.getmtime(original_entities_path)
            os.utime(active_entities_path, (original_mtime, original_mtime))

    logger.info(f"Updated region ({regional_x}, {regional_z}) in {region_file} in {time.perf_counter() - region_start_time:.3f} seconds")
    return 0

# Terrible name :/ refactored ~Cynthia
# chunk restoration logic, currently only used for -exclude claims, but intended for more logic/exclusion cases.
def add_chunk_if_not_excluded(restored_region: EmptyRegion, active_chunk: Chunk, original_chunk: Chunk, claimed_chunks: set = set()):
    if 'claims' in parsed_args.exclude and is_claimed(active_chunk, claimed_chunks):
        logger.debug(f"{active_chunk} is claimed. Skipping...")
        restored_region.add_chunk(active_chunk)
        return
    else:
        restored_region.add_chunk(original_chunk)
        return

# helper functions
def is_claimed(chunk: Chunk, claimed_chunks: set) -> bool:
    return (chunk.x, chunk.z) in claimed_chunks

def get_region_coords(filename: str):
    match = re.fullmatch(r"r\.(-?\d+)\.(-?\d+)\.mca", filename)
    if not match:
        logger.exception(f"Filename '{filename}' does not match expected format 'r.<region_x>.<region_z>.mca' (e.g., 'r.0.0.mca' or 'r.-1.5.mca').")
        sys.exit(-1)
    region_x, region_z = map(int, match.groups())
    return region_x, region_z

def region_modified(original_region_path: str, active_region_path: str) -> bool:
    original_mtime = os.path.getmtime(original_region_path)
    active_mtime = os.path.getmtime(active_region_path)

    return original_mtime != active_mtime

# exclude 'claims' helper functions

excluded_players = [ # specify static player ids to exclude from restore protection
    '00000000-0000-0000-0000-000000000000', # 'Server' player
    '00000000-0000-0000-0000-000000000001', # 'Expiration' player
] + [f"00000000-0000-0000-0000-{i:012d}" for i in range(2, 96)] # overworld + lo'dahr claims generated from csv
# TODO: Make not hard coded?

def claims_lookup(claims_dir: str, dimension: str) -> set:
    claimed_chunks = set()

    if not os.path.exists(claims_dir):
        logger.exception(f'Claim path {claims_dir} does not exist.')
        sys.exit(-1)
    
    for filename in os.listdir(claims_dir):
        if not filename.endswith('.nbt'):
            continue
        if any(excluded_id in filename for excluded_id in excluded_players):
            continue

        claim_path = os.path.join(claims_dir, filename)
        try:
            claim_data = nbtlib.load(claim_path)
        except Exception as e:
            logger.warning(f"Error reading claim data '{filename}': {e}")
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
                            logger.warning(f"Invalid chunk state position data in file '{filename}': {e}")
                            continue               
    return claimed_chunks

def logger_init(name: str = 'restore'):
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        fmt = logging.Formatter("%(levelname)s %(name)s:%(lineno)d %(message)s")
        tqdm_handler = TqdmLoggingHandler()
        tqdm_handler.setFormatter(fmt)
        tqdm_handler.stream = sys.stderr
        logger.handlers = [tqdm_handler]
        logger.setLevel(LOG_LEVEL)
    return logger

class TqdmLoggingHandler(logging.StreamHandler):
    def __init__(
        self,
        tqdm_class=std_tqdm  # type: Type[std_tqdm]
    ):
        super().__init__()
        self.tqdm_class = tqdm_class

    def emit(self, record):
        try:
            msg = self.format(record)
            self.tqdm_class.write(msg, file=self.stream)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # noqa pylint: disable=bare-except
            self.handleError(record)

class Chunk(anvil.chunk.Chunk): # type: ignore
    """
    Represents a chunk from a `.mca` file.

    Overrides `anvil-parser2`'s `Chunk` to allow parsing chunks in the `entities` folder,
    which use `Position` instead of `xPos`/`zPos`.

    Do *not* use any block-related functions on entity chunks.
    This is very much a bandaid fix that happens to work.

    Attributes
    ----------
    x: :class:`int`
        Chunk's X position
    z: :class:`int`
        Chunk's Z position
    version: :class:`int`
        Version of the chunk NBT structure
    data: :class:`nbt.TAG_Compound`
        Raw NBT data of the chunk
    tile_entities: :class:`nbt.TAG_Compound`
        ``self.data['TileEntities']`` as an attribute for easier use
    """

    __slots__ = ("version", "data", "x", "z", "tile_entities", "_logger")

    def __init__(self, nbt_data: nbt.NBTFile):
        self._logger = logger_init('restore.Chunk')
        self._logger.debug(f'Instantiating Chunk for NBT file {nbt_data.filename}')
        try:
            self.version = nbt_data["DataVersion"].value
            self._logger.debug(f'Chunk data version is {self.version}')
        except KeyError:
            self.version = VERSION_PRE_15w32a
            self._logger.debug(f'Assuming pre-1.9 snapshot 15w32a due to missing Data Version')

        if self.version >= VERSION_21w43a:
            self.data = nbt_data
            if "block_entities" in self.data:
                self._logger.debug('Using block_entities as tile_entities')
                self.tile_entities = self.data["block_entities"]
            elif "Entities" in self.data:
                self._logger.debug('Using Entities as tile_entities')
                self.tile_entities = self.data["Entities"]
            else:
                self._logger.debug('Leaving tile_entities blank')
                self.tile_entities = [] 
        else:
            try:
                self.data = nbt_data["Level"]
                if "TileEntities" in self.data:
                    self._logger.debug('Using TileEntities as tile_entities')
                    self.tile_entities = self.data["TileEntities"]
            except KeyError:
                self.data = nbt_data
                if "TileEntities" in self.data:
                    self._logger.debug('Using TileEntities as tile_entities')
                    self.tile_entities = self.data["TileEntities"]
                else:
                    self._logger.debug('Using Entities as tile_entities')
                    self.tile_entities = self.data.get("Entities", [])

        if (("xPos" not in nbt_data) or ("zPos" not in nbt_data)):
            try: # entity files use position
                self._logger.debug('Looking for Position in entity file')
                self.x = self.data["Position"].value[0]
                self.z = self.data["Position"].value[1]
            except KeyError: # sometimes some entity files are magically dataversion 2730 and mystically have an extra layer compound with no key.
                self._logger.debug('Looking for Position in data version 2730 entity file')
                self.x = self.data[""]["Position"].value[0]
                self.z = self.data[""]["Position"].value[1]
        else: # region files use xpos zpos
            self._logger.debug('Extracting positions data from region file')
            self.x = self.data["xPos"].value
            self.z = self.data["zPos"].value
        self._logger.debug(f'Generated Chunk instance for NBT file {nbt_data.filename}')

    def __repr__(self):
        return f'Chunk({self.x},{self.z})'
anvil.Chunk = Chunk
anvil.chunk.Chunk = Chunk

# cli org

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='''Another strike of the clock, another iteration of the world, Drehmal rewinds, under the whims of the Mythoclast...

example:
    python restore.py --exclude claims -b -12 -11 14 15 -v -p ".minecraft/saves/ogDrehmal" ".minecraft/saves/actDrehmal"''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('original', help='path to original state/world directory. Must contain a "region" and an "entities" folder.')
    parser.add_argument('active', help='path to active world directory. Must contain a "region" and an "entities" folder.')
    parser.add_argument('-e', '--exclude', nargs='*', type=str, choices=['claims'], default=[], help='indicate what features to exclude from restoration. Currently only supports claims.')
    parser.add_argument('-b', '--boundary', nargs=4, type=int, metavar=('minX', 'minY', 'maxX', 'maxY'), help='a drawn boundary box. Regions outside the box are not restored, only those within. Expects REGIONAL coordinates.')
    parser.add_argument('-p', '--preview', action='store_true', help='preview changes without saving.')
    loud_or_not_group = parser.add_mutually_exclusive_group()
    loud_or_not_group.add_argument('-v', '--verbose', action='store_true', help='add some extra print messages to see active progress. Cannot be used with -m.')
    loud_or_not_group.add_argument('-m', '--mute', action='store_true', help='mute all log output and only display a progress bar. Error messages will still be shown. Cannot be used with -v.')
    parsed_args = parser.parse_args()

    # Set up logger
    logging.basicConfig()
    # Logging format
    fmt = logging.Formatter("%(levelname)s %(name)s:%(lineno)d %(message)s")
    tqdm_handler = TqdmLoggingHandler()
    tqdm_handler.setFormatter(fmt)
    tqdm_handler.stream = sys.stderr
    logging.getLogger().handlers = [tqdm_handler]
    # Verbose / logging level
    if parsed_args.verbose:
        LOG_LEVEL = logging.DEBUG
    elif parsed_args.mute:
        LOG_LEVEL = logging.ERROR
    else:
        LOG_LEVEL = logging.INFO
    logging.getLogger().setLevel(LOG_LEVEL)
    # Global logger. Functions may override this with their own logger instance.
    logger = logger_init()

    logger.debug(f'''Arguments: {parsed_args}''')

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

    # Call main function
    sys.exit(restore_dimension())
