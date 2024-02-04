
from log import *
from pathlib import Path
from project_files import load_project_config, load_project_lock_file





if __name__ == "__main__":

    config = load_project_config(Path("gsm.toml"))
    # locks = load_project_lock_file(Path("gsm.lock"))
    print(config)