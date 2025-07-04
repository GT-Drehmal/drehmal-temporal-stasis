import argparse
import os, glob, re, time, sys, random, json
import logging
from typing import Sequence
from tqdm.auto import tqdm as auto_tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from joblib import Parallel, delayed
from nbt import nbt
import nbtlib
from anvil import Region, Chunk, EmptyRegion  # type: ignore
import anvil.chunk
from anvil.versions import *
from anvil.errors import ChunkNotFound

LOG_FMT = "%(levelname)s %(name)s:%(lineno)d %(message)s"

def main(args=None):
    global logger, log_path  # ugly; artifacts from isolating main code from if __name__ section
    
    # Set up argument parser
    description = '''\
Another strike of the clock, another iteration of the world, Drehmal rewinds, under the whims of the Mythoclast...

example:
    python restore.py --exclude claims -b -12 -11 14 15 -v -p ".minecraft/saves/ogDrehmal" ".minecraft/saves/actDrehmal"\
'''
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "original", help='path to original state/world directory. Must contain a "region" and an "entities" folder.'
    )
    parser.add_argument("active", help='path to active world directory. Must contain a "region" and an "entities" folder.')
    parser.add_argument(
        "-e",
        "--exclude",
        nargs="*",
        type=str,
        choices=["claims"],
        default=[],
        help="indicate what features to exclude from restoration. Currently only supports claims.",
    )
    parser.add_argument(
        "-b",
        "--boundary",
        nargs=4,
        type=int,
        metavar=("minX", "minY", "maxX", "maxY"),
        help="a drawn boundary box. Regions outside the box are not restored, only those within. Expects REGIONAL coordinates.",
    )
    parser.add_argument("-p", "--preview", action="store_true", help="preview changes without saving.")

    display_g = parser.add_argument_group("display options")
    display_g.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="add some extra print messages to see active progress. Will affect file output (i.e. --log/--logf).",
    )
    display_g.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="mute all log output and only display a progress bar. Error messages will still be shown. Does not affect file output (i.e. --log/--logf).",
    )
    display_g.add_argument(
        "--no-pbar",
        dest="nopbar",
        action="store_true",
        help="disable the progress bar. Can be helpful when piping output into a log file.",
    )

    log_options_g = parser.add_argument_group("log options")
    log_options_mutx_g = log_options_g.add_mutually_exclusive_group()
    log_options_mutx_g.add_argument(
        "--log",
        type=str,
        default="",
        help="also create a copy of the log (excluding the progress bar) in the specified log file.",
    )
    log_options_mutx_g.add_argument(
        "--logf", type=str, default="", help="same as --log, but automatically creates missing directories."
    )

    parsed_args = parser.parse_args(args)

    log_path = parsed_args.log if parsed_args.log else parsed_args.logf
    if log_path:
        if not os.path.exists(os.path.dirname(log_path)):
            if parsed_args.logf or input("One or more log file directories missing. Create missing dirs? (y/N)").lower() != "y":
                print("Aborting.")
                sys.exit(1)
            os.makedirs(os.path.dirname(log_path))

    # Set up root logger & global logger ('restore')
    # Functions may override this with their own logger instance.
    logger = logger_init(quiet=parsed_args.quiet, verbose=parsed_args.verbose)
    Chunk.logger_init(quiet=parsed_args.quiet, verbose=parsed_args.verbose)

    logger.debug(f"""Arguments: {parsed_args}""")

    # Call main function
    ret_code = restore_dimension(
        parsed_args.original,
        parsed_args.active,
        parsed_args.exclude,
        parsed_args.boundary,
        parsed_args.preview,
        parsed_args.nopbar,
        parsed_args.quiet,
        parsed_args.verbose
    )
    # Cleanup
    sys.exit(ret_code)

# see args at bottom of script
def restore_dimension(
    original_path: str, 
    active_path: str, 
    excludes: Sequence[str],
    boundaries: Sequence, 
    preview: bool, 
    nopbar: bool,
    quiet: bool,
    verbose: bool
) -> int:
    """Performs restoration on the world directory passed in through argparse.
    The world directory can be either the overworld or one of the dimensions.
    The dimension is detected automatically and the corresponding claims data will be used, if applicable.

    Arguments:
        

    Returns:
        int: Return status. If not 0, an error has occurred.
    """
    if not os.path.exists(original_path) or not os.path.exists(active_path):
        logger.error("One or both of the given world directories does not exist. Aborting.")
        return -1

    try:
        # prep
        start_time = time.perf_counter()
        logger.debug(f"restore_world started at {start_time}.")

        original_region_dir = os.path.join(original_path, "region")
        active_region_dir = os.path.join(active_path, "region")
        original_entities_dir = os.path.join(original_path, "entities")
        active_entities_dir = os.path.join(active_path, "entities")

        # Sanity check to prevent accidentally modifying original world
        if not os.path.exists(os.path.join(active_path, ".restore.override")):
            latest_original = max(glob.glob(os.path.join(original_region_dir, "*.mca")), key=os.path.getmtime)
            latest_active = max(glob.glob(os.path.join(active_region_dir, "*.mca")), key=os.path.getmtime)
            if latest_original > latest_active:
                logger.error(
                    "HEADS UP! The original world was modified more recently than the active world. Are you sure you provided the positional arguments in the correct order?"
                )
                logger.error(
                    'To ignore this check, create a file named ".restore.override" in the active world and rerun the command.'
                )
                return -1

        claimed_chunks = None
        dimension = None
        if "claims" in excludes:
            if not os.path.exists('uuid_mapping.json'):
                logger.error(
                    'Cannot find mapping file uuid_mapping.json in current directory. ' \
                    'This file is required when using the -e claims option.'
                )
                return -1
            mapping = load_mapping('uuid_mapping.json')

            # find player-claims folder and load all player claim chunks into a set for later cross-referencing in restoration
            claims_dir, dimension = infer_dimension(active_path)
            if dimension is None:
                logger.error(
                    "Argument '-e claims' was indicated, but the player-claims folder was not found! Is your directory structure strange? Aborting..."
                )
                return -1
            claimed_chunks = claims_lookup(claims_dir, dimension, mapping)

        # end prep

        if preview:
            logger.warning(f"Running under PREVIEW mode. No changes will be committed to the files.")
        logger.info(f"Beginning restoration of {len(os.listdir(active_region_dir))} regions...")

        logger_init("restore.region", quiet=quiet, verbose=verbose)

        # iterate through region directories for regions, parse chunks in regions for both entities/blocks, swap out changed chunks
        tasks = []
        for idx, region_file in enumerate(os.listdir(active_region_dir), start=1):
            if not region_file.endswith(".mca"):
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
                    region_file,
                    boundaries=boundaries,
                    excludes=excludes,
                    preview=preview,
                    quiet=quiet,
                    verbose=verbose
                )
            )

        n_jobs = os.cpu_count()
        if nopbar:
            Parallel(n_jobs=n_jobs, backend="loky", prefer="processes")(tasks)
        else:
            ProgressParallel(
                desc="Restoration progress", total=len(tasks), unit="reg", n_jobs=n_jobs, backend="loky", prefer="processes"
            )(tasks)

    except KeyboardInterrupt:
        logger.exception(
            f"World restoration cancelled by keyboard interrupt! Elapsed time: {time.perf_counter() - start_time:.3f} seconds. Exiting..."
        )
        return 1
    logger.info(
        f"Restored {dimension} at {active_path} to its original state at {original_path} in {time.perf_counter() - start_time:.3f} seconds"
    )
    return 0


def restore_region(
    original_region_dir: str,
    active_region_dir: str,
    original_entities_dir: str,
    active_entities_dir: str,
    claimed_chunks: set,
    idx: int,
    region_file: str,
    boundaries: Sequence,
    excludes: Sequence[str],
    preview: bool,
    quiet: bool,
    verbose: bool
) -> int:
    """Performs a restoration on the given .mca file.
    Chunks (as well as entities) in the active region are overwritten with the corresponding chunks in the original region,
    unless:
    - The original region does not exist
    - The original region is identical with the active region
    - If boundary is enabled and the chunk is outside of set boundary,
    - The chunk is in claimed_chunks, or
    - The original chunk/entities does not exist

    Args:
        original_region_dir (str): Directory containing region file to restore back to.
        active_region_dir (str): Directory containing region file to be modified.
        original_entities_dir (str): Directory containing entity data to restore back to.
        active_entities_dir (str): Directory containing entity data to be modified.
        claimed_chunks (set): Set of claimed chunks' x and z generated by claims_lookup
        idx (int): Index of this job for logging purposes.
        region_file (str): Name of the region file to parse. This will be used to find the file across original and active region and entities directories.

    Returns:
        int: Status code. If 0, region has been restored successfully. If 1, region has been skipped (not restored). If <0, an error has occurred.
    """
    logger = logger_init(f"restore.region.{idx}", quiet=quiet, verbose=verbose)
    with logging_redirect_tqdm(loggers=[logger], tqdm_class=auto_tqdm): # type: ignore
        original_region_path = os.path.join(original_region_dir, region_file)
        active_region_path = os.path.join(active_region_dir, region_file)
        original_entities_path = os.path.join(original_entities_dir, region_file)
        active_entities_path = os.path.join(active_entities_dir, region_file)

        if not os.path.exists(original_region_path):
            logger.debug(f"Region {region_file} does not exist in original world, skipping.")
            return 1
        elif os.path.getsize(original_region_path) == 0:
            logger.debug(f"Skipping empty region file {region_file}.")
            return 1
        elif not region_modified(original_region_path, active_region_path):
            logger.debug(f"Skipping unmodified region file {region_file}.")
            return 1

        if not os.path.exists(original_entities_path) or os.path.getsize(original_entities_path) == 0:
            logger.debug(f"Entity region {region_file} does not exist in original world, skipping.")
            restore_entities = False
        else:
            restore_entities = True

        regional_x, regional_z = get_region_coords(region_file)

        if boundaries:
            min_x, min_z, max_x, max_z = map(int, boundaries)
            if not (min_x <= regional_x <= max_x and min_z <= regional_z <= max_z):
                logger.debug(
                    f"Region ({regional_x}, {regional_z}) not within allowed boundary ({min_x}, {min_z}) - ({max_x}, {max_z}), skipping."
                )
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
                        restored_region.add_chunk(original_region_chunk) # type: ignore
                except ChunkNotFound as e:
                    logger.debug(f"({chunk_x + chunk_z}/64) No original chunk at ({chunk_x}, {chunk_z}) found.")
                    if active_region_chunk:
                        restored_region.add_chunk(active_region_chunk) # type: ignore
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
                            restored_entities.add_chunk(original_entities_chunk) # type: ignore
                    except ChunkNotFound:
                        logger.debug(f"({chunk_x + chunk_z}/64) No original entities at ({chunk_x}, {chunk_z}) found.")
                        if active_entities_chunk:
                            restored_entities.add_chunk(active_entities_chunk) # type: ignore
                            logger.debug(f"Keeping active entities by default.")
                        original_entities_chunk = None

                # if both active & original exist, pass to process_chunk for additional logic to choose. Usually original is chosen.
                if active_region_chunk and original_region_chunk:
                    add_chunk_if_not_excluded(
                        restored_region,
                        active_region_chunk,
                        original_region_chunk,
                        claimed_chunks=claimed_chunks,
                        excludes=excludes
                    )
                if restore_entities and active_entities_chunk and original_entities_chunk:
                    add_chunk_if_not_excluded(
                        restored_entities,
                        active_entities_chunk,
                        original_entities_chunk,
                        claimed_chunks=claimed_chunks,
                        excludes=excludes
                    )
                logger.debug(f"Updated chunk ({chunk_x}, {chunk_z}) in {region_file}")

        # end region > chunk loop

        if not preview:
            restored_region.save(active_region_path)
            original_mtime = os.path.getmtime(original_region_path)
            os.utime(active_region_path, (original_mtime, original_mtime))
            if restore_entities:
                restored_entities.save(active_entities_path)
                original_mtime = os.path.getmtime(original_entities_path)
                os.utime(active_entities_path, (original_mtime, original_mtime))

        logger.info(
            f"Updated region ({regional_x}, {regional_z}) in {region_file} in {time.perf_counter() - region_start_time:.3f} seconds"
        )
    return 0


# chunk restoration logic, currently only used for -exclude claims, but intended for more logic/exclusion cases.
def add_chunk_if_not_excluded(
    restored_region: EmptyRegion,
    active_chunk: Chunk,
    original_chunk: Chunk,
    claimed_chunks: set,
    excludes: Sequence[str]
):
    if "claims" in excludes and is_claimed(active_chunk, claimed_chunks):
        logger.debug(f"{active_chunk} is claimed. Skipping...")
        restored_region.add_chunk(active_chunk) # type: ignore
        return
    else:
        restored_region.add_chunk(original_chunk) # type: ignore
        return


# helper functions

def infer_dimension(
    active_path: str
):
    dimension = None
    claims_dir = os.path.join(active_path, "data", "openpartiesandclaims", "player-claims")
    if os.path.exists(claims_dir):
        dimension = "minecraft:overworld"
    else:  # one folder depth backwards for nether/end
        claims_dir = os.path.join(os.path.dirname(active_path), "data", "openpartiesandclaims", "player-claims")
        if os.path.exists(claims_dir):
            dimension_name = os.path.basename(os.path.normpath(active_path))
            if dimension_name == "DIM-1":
                dimension = "minecraft:the_nether"
            elif dimension_name == "DIM1":
                dimension = "minecraft:the_end"
        else:  # three folder depth backwards for custom dimensions
            claims_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(active_path))),
                "data",
                "openpartiesandclaims",
                "player-claims",
            )
            if os.path.exists(claims_dir):
                dimension = f"minecraft:{os.path.basename(os.path.normpath(active_path))}"
    logger.info(f'Using {dimension} as inferred dimension.')
    return claims_dir, dimension

def load_mapping(mapping_file: str) -> dict:
    logger.info(f'Loading uuid mapping from {mapping_file}')
    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_claimed(
    chunk: Chunk, 
    claimed_chunks: set
) -> bool:
    return (chunk.x, chunk.z) in claimed_chunks

def get_region_coords(filename: str):
    match = re.fullmatch(r"r\.(-?\d+)\.(-?\d+)\.mca", filename)
    if not match:
        logger.exception(
            f"Filename '{filename}' does not match expected format 'r.<region_x>.<region_z>.mca' (e.g., 'r.0.0.mca' or 'r.-1.5.mca')."
        )
        sys.exit(-1)
    region_x, region_z = map(int, match.groups())
    return region_x, region_z


def region_modified(
    original_region_path: str, 
    active_region_path: str
) -> bool:
    """Check if the region file has been modified.

    Args:
        original_region_path (str): Path to the original region file.
        active_region_path (str): Path to the active region file.

    Returns:
        bool: True if active region has the same modified time as the original region. False otherwise.
    """
    original_mtime = os.path.getmtime(original_region_path)
    active_mtime = os.path.getmtime(active_region_path)

    return original_mtime != active_mtime


# exclude 'claims' helper functions

no_restore_locations = (
    'Server', 'Expired', 'Terminus', 'Palisades Heath Tower'
)

# excluded_players = [  # specify static player ids to exclude from restore protection
#     "00000000-0000-0000-0000-000000000000",  # 'Server' player
#     "00000000-0000-0000-0000-000000000001",  # 'Expiration' player
# ] + [
#     f"00000000-0000-0000-0000-{i:012d}" for i in range(2, 93)
# ] + [ # 93 is 'Terminus'
#     f"00000000-0000-0000-0000-{i:012d}" for i in range(94, 250)
# ] # overworld + lo'dahr claims generated from csv
# # TODO: Make not hard coded?

def claims_lookup(
    claims_dir: str, 
    dimension: str, 
    mapping: dict
) -> set[tuple[int, int]]:
    """Iterates through all NBT files in the given directory and generates a set of all claimed chunks in the specified dimension.

    Args:
        claims_dir (str): Directory to find claim data in
        dimension (str): Target dimension
        mapping (dict): Dictionary that maps UUID to its corresponding direction name.

    Returns:
        set: All chunks in the given dimension that belong to a location that is *not* in no_restore_locations
    """
    claimed_chunks = set()

    if not os.path.exists(claims_dir):
        logger.exception(f"Claim path {claims_dir} does not exist.")
        sys.exit(-1)

    for filename in os.listdir(claims_dir):
        if not filename.endswith(".nbt"):
            logger.warning(f'Skipped non-NBT file {filename} in claims directory {claims_dir}')
            continue
        if mapping[filename[:-4]] in no_restore_locations:
            logger.info(f'Skipped excluded claim {mapping[filename[:-4]]} ({filename})')
            continue

        claim_path = os.path.join(claims_dir, filename)
        try:
            claim_data = nbtlib.load(claim_path)
        except Exception as e:
            logger.warning(f"Error reading claim data '{filename}': {e}")
            continue

        dimension_list = claim_data.get("dimensions")
        if not dimension_list:
            logger.debug(f'Skipped empty claim file {filename}')
            continue

        for dimension_name, dimension_data in dimension_list.items():
            if dimension == dimension_name:
                claims = dimension_data.get("claims")
                if claims is None:
                    continue

                for compound in claims:
                    positions = compound.get("positions")
                    if not positions:
                        continue

                    for position in positions:
                        try:
                            chunk_x = int(position.get("x"))
                            chunk_z = int(position.get("z"))
                            claimed_chunks.add((chunk_x, chunk_z))
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Invalid chunk state position data in file '{filename}': {e}")
                            continue
    return claimed_chunks


def logger_init(
    name: str = "restore",
    quiet: bool = False,
    verbose: bool = False
):
    """Reconfigure the root logger in a futile effort to have working logging in every thread/subprocess.

    Args:
        name (str, optional): Name of the logger to setup. Defaults to "restore" (script-level root logger).

    Returns:
        Logger: The configured logger.
    """
    root_logger = logging.getLogger()
    fmt = logging.Formatter(LOG_FMT)
    tqdm_handler = tqdmStreamHandler()
    tqdm_handler.setFormatter(fmt)
    tqdm_handler.stream = sys.stderr
    if quiet:
        tqdm_handler.setLevel(logging.ERROR)
    elif verbose:
        tqdm_handler.setLevel(logging.DEBUG)
    else:
        tqdm_handler.setLevel(logging.INFO)
    if (
        len(root_logger.handlers) > 0
        and root_logger.handlers[0].formatter
        and root_logger.handlers[0].formatter._fmt != LOG_FMT
    ):
        while len(root_logger.handlers) != 0:
            root_logger.removeHandler(root_logger.handlers[0])
        # tqdm stream handler
        root_logger.addHandler(tqdm_handler)
        if log_path:  # global variabling all over the place (see if __name__ for logic)
            # File handler
            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setFormatter(fmt)
            if verbose:
                fh.setLevel(logging.DEBUG)
            else:
                fh.setLevel(logging.INFO)
            root_logger.addHandler(fh)
        root_logger.setLevel(logging.DEBUG)
    logger = logging.getLogger(name)
    # # Configure new logger if it does not have any handlers
    # # because for some reason it can inherit file handler and not stream handler :///
    # # Now it suddenly decides to work again and I do not know why
    if len(logger.handlers) == 0:
        logger.addHandler(tqdm_handler)
    return logger


class tqdmStreamHandler(logging.StreamHandler):
    """Modified from [tqdm.contrib.logging](https://tqdm.github.io/docs/contrib.logging/)"""
    def __init__(self, tqdm_class=auto_tqdm):
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


class ProgressParallel(Parallel):
    """Modified from https://stackoverflow.com/a/61900501"""
    def __init__(self, desc, total, unit, *args, **kwargs):
        self._desc = desc
        self._total = total
        self._unit = unit
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        with auto_tqdm(
            desc=self._desc,
            total=self._total,
            unit=self._unit,
            dynamic_ncols=True,
            colour=f"#{random.randint(0, 16777215):06x}",
            maxinterval=0.01,
        ) as self._pbar:
            return Parallel.__call__(self, *args, **kwargs)

    def print_progress(self):
        self._pbar.n = self.n_completed_tasks
        self._pbar.refresh()


class Chunk(anvil.chunk.Chunk):  # type: ignore
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

    __slots__ = ("version", "data", "x", "z", "tile_entities")
    _logger = logging.root  # Initialized in if __main

    def __init__(self, nbt_data: nbt.NBTFile):
        # Chunk._logger.debug(f'Instantiating Chunk for NBT file {id(nbt_data.file)}')
        try:
            self.version = nbt_data["DataVersion"].value
            Chunk._logger.debug(f"Chunk data version is {self.version}")
        except KeyError:
            self.version = VERSION_PRE_15w32a
            Chunk._logger.debug(f"Assuming pre-1.9 snapshot 15w32a due to missing Data Version")

        if self.version >= VERSION_21w43a:
            self.data = nbt_data
            if "block_entities" in self.data:
                Chunk._logger.debug("Using block_entities as tile_entities")
                self.tile_entities = self.data["block_entities"]
            elif "Entities" in self.data:
                Chunk._logger.debug("Using Entities as tile_entities")
                self.tile_entities = self.data["Entities"]
            else:
                Chunk._logger.debug("Leaving tile_entities blank")
                self.tile_entities = []
        else:
            try:
                self.data = nbt_data["Level"]
                if "TileEntities" in self.data:
                    Chunk._logger.debug("Using TileEntities as tile_entities")
                    self.tile_entities = self.data["TileEntities"]
            except KeyError:
                self.data = nbt_data
                if "TileEntities" in self.data:
                    Chunk._logger.debug("Using TileEntities as tile_entities")
                    self.tile_entities = self.data["TileEntities"]
                else:
                    Chunk._logger.debug("Using Entities as tile_entities")
                    self.tile_entities = self.data.get("Entities", [])

        if ("xPos" not in nbt_data) or ("zPos" not in nbt_data):
            try:  # entity files use position
                Chunk._logger.debug("Looking for Position in entity file")
                self.x = self.data["Position"].value[0]
                self.z = self.data["Position"].value[1]
            except (
                KeyError
            ):  # sometimes some entity files are magically dataversion 2730 and mystically have an extra layer compound with no key.
                Chunk._logger.debug("Looking for Position in data version 2730 entity file")
                self.x = self.data[""]["Position"].value[0]
                self.z = self.data[""]["Position"].value[1]
        else:  # region files use xpos zpos
            Chunk._logger.debug("Extracting positions data from region file")
            self.x = self.data["xPos"].value
            self.z = self.data["zPos"].value
        # Chunk._logger.debug(f'Generated Chunk instance for NBT file {id(nbt_data.file)}')

    @classmethod
    def logger_init(cls, quiet: bool = False, verbose: bool = False):
        cls._logger = logger_init("restore.Chunk", quiet=quiet, verbose=verbose)

    def __repr__(self):
        return f"Chunk({self.x},{self.z})"


anvil.Chunk = Chunk

if __name__ == "__main__":
    main()
