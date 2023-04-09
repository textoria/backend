import os
import json
import yaml


def load_yml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def extract():
    # Folders with .yml files
    folders = ['locales/en', 'locales/ru']

    # Dictionary to store the merged data
    merged_data = {}

    # Iterate over the folders
    for folder in folders:
        # List .yml files in the folder
        yml_files = [file for file in os.listdir(folder) if file.endswith('.yml')]

        # Iterate over the .yml files
        for yml_file in yml_files:
            file_path = os.path.join(folder, yml_file)
            data = load_yml_file(file_path)

            # Merge the data
            for key, value in data.items():
                if key not in merged_data:
                    merged_data[key] = {}

                language = folder.split('/')[-1]
                # check if the value is a JSON object
                if isinstance(value, str) and ((value.startswith('{') and value.endswith('}')) or
                                               (value.startswith('[') and value.endswith(']'))):
                    try:
                        json_value = json.loads(value)
                    except json.decoder.JSONDecodeError:
                        merged_data[key][language] = value
                        continue

                    merged_data[key][language] = json_value
                else:
                    merged_data[key][language] = value

    return merged_data


with open("keys.json", "w", encoding="utf-8") as json_file:
    json_file.write(json.dumps(extract()))
