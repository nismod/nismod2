"""Migrate a configuration folder for a release of smif<1 to smif>=1

"""
import os

def _archive_old_config_folder():
    pass

def _rename_modelrunfolder():
    os.rename('config/sos_model_runs', 'config/model_runs')


def main():
    _archive_old_config_folder()
    _rename_modelrunfolder()

if __name__ == '__main__':

    main()