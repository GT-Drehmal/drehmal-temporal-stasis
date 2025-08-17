import argparse
import glob
import logging
import os
import random
import re
import sys
import time
import tomllib
from typing import Literal, Sequence

import anvil.chunk
import nbtlib
from anvil import Chunk, EmptyRegion, Region  # type: ignore
from anvil.errors import ChunkNotFound
from anvil.versions import *
from joblib import Parallel, delayed
from nbt import nbt
from tqdm.auto import tqdm as auto_tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

LOG_FMT = "%(levelname)s %(name)s:%(lineno)d %(message)s"

# The value of the playerConfig.claims.name field.
# Any subconfig belonging to one of the RESTORE_OVERRIDE_UUIDS,
# that DOES NOT have an area name matching the following,
# WILL be restored (i.e. not excluded from restoration).
NO_RESTORE_LOCATIONS: tuple = (
    'The Terminus', 'Palisades Heath Tower'
)
# By default, claimed chunks are excluded from restoration.
# load_claims adds excluded chunks to a set which is checked against upon the restoration process.
# Claims that are owned by any of the following UUIDs, however,
# WILL be restored (i.e. not excluded from restoration),
# UNLESS they use a subconfig that specifies a claimed area name that matches one in NO_RESTORE_LOCATIONS.
RESTORE_OVERRIDE_UUIDS: tuple = (
    '00000000-0000-0000-0000-000000000000',
)

DEFAULT_LEVEL = logging.INFO
TRACE_LVL_NUM = 5
LOG_PATH = f"./restore_logs/log_{time.time()}.txt"

def main(args: Sequence[str] | None = None):
    """Sets up `argparse` and calls the main function `restore_dimension`.

    Args:
        args (Sequence[str], optional):
            Custom arguments to use when parsing.
            Defaults to `sys.argv[1:]` (fallback of `parse_args`).
    """
    global logger  # ugly; artifacts from isolating main code from if __name__ section

    
    # Set up argument parser
    description = '''Example:
    python restore.py --exclude claims -b -12 -11 14 15 -v -p ".minecraft/saves/ogDrehmal" ".minecraft/saves/actDrehmal"'''
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "original", 
        help='path to original state/world directory. Must contain a "region" and an "entities" folder.'
    )
    parser.add_argument(
        "active", 
        help='path to active world directory. Must contain a "region" and an "entities" folder.'
    )
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
    parser.add_argument(
        "-p", 
        "--preview", 
        action="store_true", 
        help="preview changes without saving."
    )

    display_g = parser.add_argument_group(
        "display options"
    )
    display_g.add_argument(
        "--no-pbar",
        dest="nopbar",
        action="store_true",
        help="disable the progress bar. Can be helpful when piping output into a log file.",
    )

    debug_options_g = parser.add_argument_group(
        "debug options"
    )
    debug_options_g.add_argument(
        '--sequential', 
        action='store_true', 
        help='use sequential processing instead of parallel for a more readable log.'
    )

    parsed_args = parser.parse_args(args)

    if not os.path.exists(os.path.dirname(LOG_PATH)):
        os.makedirs(os.path.dirname(LOG_PATH))

    # Set up root logger & global logger ('restore')
    # Functions may override this with their own logger instance.
    logger = logger_init()
    Chunk.logger_init()

    if any(len(x) > 100 for x in NO_RESTORE_LOCATIONS): # type: ignore
        logger.error('Some of the no-restore location names are longer than 100 characters.')
        exit(-1)

    # Call main function
    ret_code = restore_dimension(
        parsed_args.original,
        parsed_args.active,
        parsed_args.exclude,
        parsed_args.boundary,
        parsed_args.preview,
        parsed_args.nopbar,
        parsed_args.sequential
    )
    # Cleanup
    exit(ret_code)

# see args at bottom of script
def restore_dimension(
    original_path: str, 
    active_path: str, 
    excludes: Sequence[str],
    boundaries: Sequence, 
    preview: bool, 
    nopbar: bool,
    sequential: bool
) -> int:
    """Performs restoration on the world directory passed in through argparse.
    The world directory can be either the overworld or one of the dimensions.
    The dimension is detected automatically via `infer_dimension` and the corresponding claims data will be used, if applicable.

    For more details about the arguments, consult the `argparse` help string in `main`.

    Arguments:
        original_path (str): Path to the 'original' state of the world folder
        actvive_path (str): Path to the 'active' state of the world folder
        excludes (Sequence[str]): Restoration exclusion option. Currently only supports empty or `Sequence[Literal['Claims']]`
        boundaries (Sequence): Maximum and minimum **region** coordinates to perform restore in
        preview (bool): Whether to run in "preview" mode. If `True`, no changes will be written to the files.
        nopbar (bool): If `True`, disables the progress bar.
        sequential (bool): If `true`, uses sequential processing instead of joblib's parallel.

    Returns:
        int: Return status. If not 0, an error has occurred.
    """
    logger.debug(f"""Arguments: {locals()}""")

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

        if preview:
            logger.warning(f"Running under PREVIEW mode. No changes will be committed to the files.")
            
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
            # find player-claims folder and load all player claim chunks into a set for later cross-referencing in restoration
            claims_dir, configs_dir, dimension = infer_dimension(active_path)
            if dimension is None:
                logger.error(
                    "Argument '-e claims' was indicated, but the player-claims folder was not found! Is your directory structure strange? Aborting..."
                )
                return -1
            configs_mapping = load_subconfigs(configs_dir, '00000000-0000-0000-0000-000000000000')
            if configs_mapping == -1:
                return -1
            claimed_chunks = load_claims(claims_dir, dimension, configs_mapping)
            if claimed_chunks == -1:
                return -1

        # end prep

        logger.info(f"Beginning restoration of {len(os.listdir(active_region_dir))} regions...")

        logger_init(name="restore.region")

        # iterate through region directories for regions, parse chunks in regions for both entities/blocks, swap out changed chunks
        tasks = []
        for idx, region_file in enumerate(os.listdir(active_region_dir), start=1):
            if not region_file.endswith(".mca"):
                logger.info(f"Skipping non-anvil file {region_file}")
                continue
            if sequential:
                ## Sequential restoration for debugging
                restore_region(
                    original_region_dir,
                    active_region_dir,
                    original_entities_dir,
                    active_entities_dir,
                    claimed_chunks,
                    idx,
                    region_file,
                    excludes,
                    boundaries,
                    preview
                )
            else:
                tasks.append(
                    delayed(restore_region)(
                        original_region_dir,
                        active_region_dir,
                        original_entities_dir,
                        active_entities_dir,
                        claimed_chunks,
                        idx,
                        region_file,
                        excludes=excludes,
                        boundaries=boundaries,
                        preview=preview
                    )
                )

        if not sequential:
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
    claimed_chunks: set | None,
    idx: int,
    region_file: str,
    excludes: Sequence[str],
    boundaries: Sequence,
    preview: bool
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
        claimed_chunks (set | None): Set of claimed chunks' x and z generated by `load_claims`.
            If not excluding claims, can be None.
        idx (int): Index of this job for logging purposes.
        region_file (str): Name of the region file to parse. This will be used to find the file across original and active region and entities directories.
        excludes (Sequence[str]): Restoration exclusion option. Currently only supports empty or `Sequence[Literal['Claims']]`
        boundaries (Sequence): Maximum and minimum **region** coordinates to perform restore in
        preview (bool): Whether to run in "preview" mode. If `True`, no changes will be written to the files.

    Returns:
        int: Status code. If 0, region has been restored successfully. If 1, region has been skipped (not restored). If <0, an error has occurred.
    """
    logger = logger_init(name=f"restore.region.{idx}")
    with logging_redirect_tqdm(loggers=[logger], tqdm_class=auto_tqdm): # type: ignore
        original_region_path = os.path.join(original_region_dir, region_file)
        active_region_path = os.path.join(active_region_dir, region_file)
        original_entities_path = os.path.join(original_entities_dir, region_file)
        active_entities_path = os.path.join(active_entities_dir, region_file)

        regional_x, regional_z = get_region_coords(region_file)

        if boundaries:
            min_x, min_z, max_x, max_z = map(int, boundaries)
            if not (min_x <= regional_x <= max_x and min_z <= regional_z <= max_z):
                logger.debug(
                    f"Region ({regional_x}, {regional_z}) not within allowed boundary ({min_x}, {min_z}) - ({max_x}, {max_z}), skipping."
                )
                return 1
        
        if not os.path.exists(original_region_path):
            logger.debug(f"Region {region_file} does not exist in original world.")
            skip_region_blocks = True
        elif os.path.getsize(original_region_path) == 0:
            logger.debug(f"Region file {region_file} is empty.")
            skip_region_blocks = True
        elif not region_modified(original_region_path, active_region_path):
            logger.debug(f"Region file {region_file} is unmodified.")
            skip_region_blocks = True
        else:
            skip_region_blocks = False

        if not os.path.exists(original_entities_path) or os.path.getsize(original_entities_path) == 0:
            logger.debug(f"Entity region {region_file} does not exist in original world.")
            skip_entities = True
        elif not region_modified(original_entities_path, active_entities_path):
            logger.debug(f"Entity region {region_file} is unmodified.")
            skip_entities = True
        else:
            skip_entities = False
        
        if skip_entities and skip_region_blocks:
            logger.debug(f'Neither entities nor chunk are modified, skipping {region_file} without making any changes.')
            return 1

        if not skip_region_blocks:
            original_region = Region.from_file(original_region_path)
            active_region = Region.from_file(active_region_path)
            restored_region = EmptyRegion(regional_x, regional_z)
        else:
            original_region = None
            active_region = None
            restored_region = None
        if not skip_entities:
            original_entities = Region.from_file(original_entities_path)
            active_entities = Region.from_file(active_entities_path)
            restored_entities = EmptyRegion(regional_x, regional_z)
        else:
            original_entities= None
            active_entities = None
            restored_entities = None

        # region > chunk granularity starts here. 32x32 chunks per region
        logger.debug(f'Beginning restoration of region {region_file}...')
        region_start_time = time.perf_counter()
        for chunk_x in range(32):
            for chunk_z in range(32):
                if not skip_region_blocks:
                    # check for active vs. original chunk. If only one exists, default to that one. Region/Entity check decoupled for sanity
                    try:
                        active_region_chunk = Chunk.from_region(active_region, chunk_x, chunk_z) # type: ignore - if active_region is None, it indicates an issue in the logic. Same for below.
                    except ChunkNotFound as e:
                        logger.trace(f"[{region_file}|{chunk_x},{chunk_z}] No active chunk found.")
                        active_region_chunk = None

                    try:
                        original_region_chunk = Chunk.from_region(original_region, chunk_x, chunk_z) # type: ignore
                        if not active_region_chunk:
                            restored_region.add_chunk(original_region_chunk) # type: ignore
                    except ChunkNotFound as e:
                        original_region_chunk = None
                        if active_region_chunk:
                            restored_region.add_chunk(active_region_chunk) # type: ignore
                            logger.debug(f"[{region_file}|{chunk_x},{chunk_z}] No original chunk found, keeping active chunk by default.") # type: ignore
                        else:
                            logger.trace(f"[{region_file}|{chunk_x},{chunk_z}] No active or original chunk.")
                else:
                    # Reset variable since they might have been set in last loop
                    original_region_chunk = None
                    active_region_chunk = None

                if not skip_entities:
                    try:
                        active_entities_chunk = Chunk.from_region(active_entities, chunk_x, chunk_z) # type: ignore
                    except ChunkNotFound:
                        logger.trace(f"[{region_file}|{chunk_x},{chunk_z}] No active entities found.")
                        active_entities_chunk = None

                    try:
                        original_entities_chunk = Chunk.from_region(original_entities, chunk_x, chunk_z) # type: ignore
                        if not active_entities_chunk:
                            restored_entities.add_chunk(original_entities_chunk) # type: ignore
                    except ChunkNotFound:
                        original_entities_chunk = None
                        if active_entities_chunk:
                            # restored_entities.add_chunk(active_entities_chunk) # type: ignore
                            logger.trace(f'[{region_file}|{chunk_x},{chunk_z}] {excludes=} {active_entities_chunk=} {claimed_chunks=} {is_claimed(active_entities_chunk, claimed_chunks)=}')
                            if 'claims' in excludes and is_claimed(active_entities_chunk, claimed_chunks):
                                logger.debug(f"[{region_file}|{chunk_x},{chunk_z}] No original entities found in claimed chunk, keeping active entities.") # type: ignore
                                restored_entities.add_chunk(active_entities_chunk) # type: ignore
                            else:
                                logger.warning(f"[{region_file}|{chunk_x},{chunk_z}] No original entities found, deleting active entities for unclaimed chunk.") # type: ignore
                                active_entities_chunk = None 
                                # The chunk is deleted by not adding it via add_chunk. 
                        else:
                            logger.trace(f"[{region_file}|{chunk_x},{chunk_z}] No active or original entities.")
                else:
                    # Reset variable since they might have been set in last loop
                    original_entities_chunk = None
                    active_entities_chunk = None

                # if both active & original exist, pass to process_chunk for additional logic to choose. Usually original is chosen.
                if (not skip_region_blocks) and active_region_chunk and original_region_chunk:
                    restore_chunk_if_not_excluded(
                        restored_region, # type: ignore
                        active_region_chunk,
                        original_region_chunk,
                        claimed_chunks=claimed_chunks,
                        excludes=excludes
                    )
                    logger.debug(f"[{region_file}|{chunk_x},{chunk_z}] Updated chunk") # type: ignore
                if (not skip_entities) and active_entities_chunk and original_entities_chunk:
                    restore_chunk_if_not_excluded(
                        restored_entities, # type: ignore
                        active_entities_chunk,
                        original_entities_chunk,
                        claimed_chunks=claimed_chunks,
                        excludes=excludes
                    )
                    logger.debug(f"[{region_file}|{chunk_x},{chunk_z}] Updated entities") # type: ignore

        # end region > chunk loop

        if not preview:
            if not skip_region_blocks:
                restored_region.save(active_region_path) # type: ignore
                original_mtime = os.path.getmtime(original_region_path)
                os.utime(active_region_path, (original_mtime, original_mtime))
            if not skip_entities:
                restored_entities.save(active_entities_path) # type: ignore
                original_mtime = os.path.getmtime(original_entities_path)
                os.utime(active_entities_path, (original_mtime, original_mtime))

        logger.info(
            f"Updated region ({regional_x}, {regional_z}) in {region_file} in {time.perf_counter() - region_start_time:.3f} seconds"
        )
    return 0


# chunk restoration logic, currently only used for -exclude claims, but intended for more logic/exclusion cases.
def restore_chunk_if_not_excluded(
    restored_region: EmptyRegion,
    active_chunk: Chunk,
    original_chunk: Chunk,
    claimed_chunks: set | None,
    excludes: Sequence[str]
):
    """If the current chunk should be restored, adds `original_chunk` to `restored_region`. Otherwise, adds `active_chunk`.
    
    Chunk restoration helper function currently only used for `-exclude` claims.

    Args:
        restored_region (EmptyRegion): Region we're currently working on restoring
        active_chunk (Chunk): The current state of the chunk corresponding to `original_chunk`
        original_chunk (Chunk): The initial state of the chunk corresponding to `active_chunk`
        claimed_chunks (set): Set of claimed chunks generated by `load_claims`. Empty if no `-e claims`
        excludes (Sequence[str]): Restoration exclusion option. Currently only supports empty or `Sequence[Literal['Claims']]`
    """
    if "claims" in excludes and is_claimed(active_chunk, claimed_chunks):
        logger.trace(f"{active_chunk} is claimed. Skipping...")
        restored_region.add_chunk(active_chunk) # type: ignore
        return
    else:
        restored_region.add_chunk(original_chunk) # type: ignore
        return


# helper functions

def infer_dimension(
    active_path: str
):
    """Deduces the dimension that the given folder is in by checking several depths of parent folders for the folder `openpartiesandclaims/player-claims/`.

    Args:
        active_path (str): The folder to check dimension of

    Returns:
        (claims_dir, configs_dir, dimension) (tuple[str, str, str | None]):
            Paths to the `player-claims` and `player-configs` directories under the `openpartiesandclaims` we found,
            and the name of the inferred dimension
            (for Drehmal, one of `minecraft:overworld`, `minecraft:the_nether`, `minecraft:the_end`, `minecraft:space`, `minecraft:lodahr`, `minecraft:true_end`, and `minecraft:town_reworks`).
            
            **Note:** If the `openpartiesandclaims` folder is NOT found, then the value of `dimension` will be `None`.
            When this is the case, the value of `claims_dir` and `configs_dir` is unspecified.
    """
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
    configs_dir = os.path.join(os.path.dirname(claims_dir), 'player-configs')
    logger.info(f'Using {dimension} as inferred dimension.')
    logger.debug(f'opac folder = {os.path.dirname(claims_dir)}')
    return claims_dir, configs_dir, dimension


def is_claimed(
    chunk: Chunk, 
    claimed_chunks: set | None
) -> bool:
    return claimed_chunks is None or (chunk.x, chunk.z) in claimed_chunks

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


def load_subconfigs(
    configs_dir: str,
    uuid: str
) -> dict[int, str] | Literal[-1]:
    """Parses the area name of all existing sub-configs of a given player, and generates a map from sub-config indices to their area names (location names).

    Arguments:
        configs_dir (str): Path to OPAC's `player-configs` directory.
        uuid (str): The player we will load subconfigs from.

    Returns:
        mapping (dict[int, str] | Literal[-1]):
            A dictionary with `subConfigIndex` as **key** and `playerConfig.claims.name` as **value**.
            The claim name may be truncated if it was over 100 characters long.
            
        If an error was encountered, this function returns `-1`.
    """
    mapping: dict[int, str] = {}
    # Load main config (subConfigIndex = -1)
    config_file = os.path.join(configs_dir, uuid+'.toml')
    if os.path.exists(config_file):
        with open(config_file, 'rb') as f:
            try:
                claims_name: str | None = tomllib.load(f)['playerConfig']['claims']['name']
            except KeyError:
                logger.warning(f'Cannot find field playerConfig.claims.name in main config file for {uuid}. This file will be skipped.')
                claims_name = None
        if claims_name is not None:
            mapping[-1] = claims_name
    else:
        logger.warning(f'Skipping missing config file for {uuid}')
    # Load subconfigs
    subconfig_dir = os.path.join(configs_dir, 'sub-configs', uuid+'/')
    if not os.path.exists(subconfig_dir):
        logger.error(f'Cannot find subconfig directory {subconfig_dir}')
        return -1
    for filename in os.listdir(subconfig_dir):
        if not filename.endswith('.toml'):
            logger.warning(f'Skipping non-TOML file {filename} in subconfig directory')
            continue
        try:
            idx = int(filename.split('$')[-1][:-5])
            if idx <= 0:
                raise ValueError()
        except ValueError:
            logger.warning(f'Skipping incorrect subconfig file name {filename}')
            continue
        subconfig_path = os.path.join(subconfig_dir, filename)
        with open(subconfig_path, 'rb') as f:
            try:
                location_name: str = tomllib.load(f)['playerConfig']['claims']['name']
            except KeyError:
                logger.warning(f'Cannot find field playerConfig.claims.name in subconfig file {filename} for {uuid}. Subconfigs may be corrupted or misconfigured. This file will be skipped.')
                continue
        mapping[idx] = location_name
    return mapping


def load_claims(
    claims_dir: str, 
    dimension: str,
    mapping: dict[int, str]
) -> set[tuple[int, int]] | Literal[-1]:
    """Iterates through all NBT files in the given directory and generates a set of all claimed chunks in the specified dimension.

    Args:
        claims_dir (str): Directory to find claim data in
        dimension (str): Target dimension
        mapping (dict[int, str]):
            A dictionary that maps sub-config indices to their corresponding location name (sub-config area name).
            Generated by `load_subconfigs`.

    Returns:
        claims_to_exclude_from_restoration (set[tuple[int, int]] | Literal[-1]):
            A set containing x and z coordinates of all claimed chunks in the given dimension
            that, if claimed by one of `RESTORE_OVERRIDE_UUIDS`,
            belong to a location that is *not* in `NO_RESTORE_LOCATIONS`.
            
        If an error was encountered, this function returns `-1`.
    """
    claimed_chunks: set[tuple[int, int]] = set()

    if not os.path.exists(claims_dir):
        logger.exception(f"Claim path {claims_dir} does not exist.")
        return -1

    for claim_filename in os.listdir(claims_dir):
        if not claim_filename.endswith(".nbt"):
            logger.warning(f'Skipped non-NBT file {claim_filename} in claims directory {claims_dir}')
            continue

        claim_path = os.path.join(claims_dir, claim_filename)
        try:
            claim_data = nbtlib.load(claim_path)
        except Exception as e:
            logger.warning(f"Skipping invalid claim file {claim_filename}: {e.__class__.__name__} ({e})")
            continue

        dimension_list = claim_data.get("dimensions")
        if not dimension_list:
            logger.debug(f'Skipped empty claim file {claim_filename}')
            continue

        for dimension_name, dimension_data in dimension_list.items():
            if dimension == dimension_name:
                claims = dimension_data.get("claims")
                if claims is None:
                    continue
                for clm in claims:
                    if claim_filename[:-4] in RESTORE_OVERRIDE_UUIDS:
                        # Claim might still need to be restored (i.e. we shouldn't include it in excluded claims set)
                        # Check claim subconfig to see if we should add it
                        state: nbtlib.Compound = clm.get("state")
                        sub_config_index = state.get("subConfigIndex")
                        try:
                            if mapping[int(sub_config_index)] not in NO_RESTORE_LOCATIONS: # type: ignore
                                logger.debug(f'Ignoring claims of {mapping[sub_config_index]} (${sub_config_index})') # type: ignore
                                continue
                        except KeyError:
                            # Happens when a subconfig doesn't have a name or is otherwise left unparsed
                            # If this happens, it's definitely not gonna be in NO_RESTORE_LOCATIONS.
                            logger.debug(f'Ignoring unnamed subconfig claims ${sub_config_index} of {claim_filename[:-4]}')
                            continue
                        except ValueError:
                            logger.warning(f'The claims file {claim_filename} contains malformed field (subConfigIndex = {sub_config_index}). This file will be skipped.')
                            continue
                    # Add all positions (chunks) of this claim to the set
                    positions = clm.get("positions")
                    if not positions:
                        continue
                    for position in positions:
                        try:
                            chunk_x = int(position.get("x"))
                            chunk_z = int(position.get("z"))
                            claimed_chunks.add((chunk_x, chunk_z))
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Skipping invalid chunk state position data in file '{claim_filename}': {e.__class__.__name__} ({e})")
                            continue
        logger.debug(f'Processed claim file {claim_filename}')
    return claimed_chunks


def logger_init(
    name: str = "restore"
):
    """Reconfigure the root logger in a futile effort to have working logging in every thread/subprocess.

    Args:
        quiet (bool): Whether to initialize logging in quiet mode
        verbose (bool): Whether to initialize logging in verbose mode
        name (str, optional): Name of the logger to setup. Defaults to "restore" (script-level root logger).

    Returns:
        Logger: The configured logger.
    """
    # Add a new TRACE level = 5
    def _trace(self, message, *args, **kwargs):
        if self.isEnabledFor(TRACE_LVL_NUM):
            self._log(TRACE_LVL_NUM, message, args, **kwargs)
    def _trace_module_level(message, *args, **kwargs):
        logging.log(TRACE_LVL_NUM, message, *args, **kwargs)

    logging.addLevelName(TRACE_LVL_NUM, 'TRACE')
    setattr(logging, 'TRACE', TRACE_LVL_NUM)
    setattr(logging.getLoggerClass(), 'trace', _trace)
    setattr(logging, 'trace', _trace_module_level)

    # # Handlers - format
    # fmt = logging.Formatter(LOG_FMT)
    # # File handler
    # fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    # fh.setFormatter(fmt)
    # fh.setLevel(TRACE_LVL_NUM)

    # Configure root logger
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    root_logger.setLevel(logging.FATAL + 1)
    root_logger.propagate = False

    # Configure requested logger
    logger = logging.getLogger(name)
    # has_fh = False
    if logger.hasHandlers():
        for handler in logger.handlers:
            # if handler != fh:
                logger.removeHandler(handler)
            # else:
            #     has_fh = True
    # if not has_fh:
    #     logger.addHandler(fh)
    # logger.setLevel(fh.level)
    logger.propagate = False
    return logger


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
    _logger = logging.root  # Initialized in main

    def __init__(self, nbt_data: nbt.NBTFile):
        # Chunk._logger.trace(f'Instantiating Chunk for NBT file {id(nbt_data.file)}')
        try:
            self.version = nbt_data["DataVersion"].value
            Chunk._logger.trace(f"Chunk data version is {self.version}")
        except KeyError:
            self.version = VERSION_PRE_15w32a
            Chunk._logger.debug(f"Assuming pre-1.9 snapshot 15w32a due to missing Data Version")

        if self.version >= VERSION_21w43a:
            self.data = nbt_data
            if "block_entities" in self.data:
                Chunk._logger.trace("Using block_entities as tile_entities")
                self.tile_entities = self.data["block_entities"]
            elif "Entities" in self.data:
                Chunk._logger.trace("Using Entities as tile_entities")
                self.tile_entities = self.data["Entities"]
            else:
                Chunk._logger.debug("Leaving tile_entities blank")
                self.tile_entities = []
        else:
            try:
                self.data = nbt_data["Level"]
                if "TileEntities" in self.data:
                    Chunk._logger.trace("Using TileEntities as tile_entities")
                    self.tile_entities = self.data["TileEntities"]
            except KeyError:
                self.data = nbt_data
                if "TileEntities" in self.data:
                    Chunk._logger.trace("Using TileEntities as tile_entities")
                    self.tile_entities = self.data["TileEntities"]
                else:
                    Chunk._logger.trace("Using Entities as tile_entities")
                    self.tile_entities = self.data.get("Entities", [])

        Chunk._logger.trace("Extracting positions data")
        if ("xPos" not in nbt_data) or ("zPos" not in nbt_data):
            try:  # entity files use position
                Chunk._logger.trace("Is entity file")
                self.x = self.data["Position"].value[0]
                self.z = self.data["Position"].value[1]
            except (
                KeyError
            ):  # sometimes some entity files are magically dataversion 2730 and mystically have an extra layer compound with no key.
                Chunk._logger.trace("Data version may be 2730")
                self.x = self.data[""]["Position"].value[0]
                self.z = self.data[""]["Position"].value[1]
        else:  # region files use xpos zpos
            Chunk._logger.trace("Is region file")
            self.x = self.data["xPos"].value
            self.z = self.data["zPos"].value
        Chunk._logger.trace(f"Chunk positions are {self.x},{self.z}")
        # Chunk._logger.trace(f'Generated Chunk instance for NBT file {id(nbt_data.file)}')

    @classmethod
    def logger_init(cls):
        cls._logger = logger_init(name="restore.Chunk")

    def __repr__(self):
        return f"Chunk({self.x},{self.z})"


anvil.Chunk = Chunk

if __name__ == "__main__":
    main()
