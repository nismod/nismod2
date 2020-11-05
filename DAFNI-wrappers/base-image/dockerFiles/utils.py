import os
import subprocess
from pathlib import Path
from settings import NISMOD_DATA_PATH


def run_process(command: str, shell: bool = True, check_error: bool = True):
    try:
        print(subprocess.run(command, shell=shell, check=check_error,))
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr)
        raise


def is_truthy(val) -> bool:
    return val == "True" or val == "true" or val == 1 or val == True


def get_all_files(walk_dir: Path):
    files = []
    for path in walk_dir.iterdir():
        if path.is_dir():
            files.extend(get_all_files(path))
            continue
        files.append(path)
    return files


def link_files(src_path: Path, dest_path: Path):
    for src_file in get_all_files(src_path):
        dest_file = dest_path.joinpath(src_file.relative_to(src_path))
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        os.link(src_file, dest_file)

def copy_lads():
    print("Copying LADS")
    lads_input = Path("/data/lads/")
    lads_output = NISMOD_DATA_PATH.joinpath("dimensions/")
    run_process("cp -ru " + str(lads_input) + "/* " + str(lads_output))
    print("Finished Copying LADS")

