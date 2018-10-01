from ruamel.yaml import YAML
import os
import sys

def _read_config_file(filepath):
    yaml = YAML()
    with open(filepath, encoding='utf-8') as file:
        data = yaml.load(file)

    for key, value in data.items():
        if value == None:
            data[key] = []

    return data

def _write_config_file(filepath, data):
    yaml = YAML()
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file)

def write_dimensions(project_folder):

    project_config_path = os.path.join(project_folder, 'config', 'project.yml')
    project_config_data = _read_config_file(project_config_path)

    project_config_data = extract_data(project_config_data, 
                                       project_folder, 
                                       'dimensions') 

    project_config_data = extract_data(project_config_data, 
                                       project_folder, 
                                       'scenarios')     

    project_config_data = extract_data(project_config_data, 
                                       project_folder, 
                                       'narratives')            

    # update project file
    _write_config_file(project_config_path, project_config_data)

def extract_data(project_config_data, project_folder, field_name):
    
    config_list = None

    try:
        config_list = project_config_data[field_name]
    except KeyError:
        print("No '{}' in project.yml".format(field_name))

    if config_list:
        for config_item in config_list:
            filepath = os.path.join(project_folder, 'config', field_name, config_item['name'] + '.yml')
            _write_config_file(filepath, config_item)

        project_config_data.pop(field_name)                

    return project_config_data

def main(project_folder):
    write_dimensions(project_folder)

if __name__ == '__main__':

    if len(sys.argv)==2:
        main(sys.argv[1])
    else:
        print(
            'migrate_config.py path/to/smif/config'
        )