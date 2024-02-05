
# ----------------------------------- local ---------------------------------- #
from log import *
from project_files.config_file import load_config_file



if __name__ == "__main__":
    
    config_file = load_config_file()
    print(config_file)

    pass