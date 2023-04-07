import os
import glob
import yaml
import json

# Define the root folder containing the 'rus' and 'eng' folders
root_folder = "locales/"

# Initialize an empty dictionary to store the parsed keys and values
data = {}

# Define a mapping between language codes and folder names
lang_mapping = {"rus": "_ru", "eng": "_en"}


# Function to check if a string is a JSON object
def is_json(value):
    try:
        json.loads(value)
    except ValueError:
        return False
    return True


# Iterate over the 'rus' and 'eng' folders
for lang in lang_mapping:
    # Construct the folder path
    folder_path = os.path.join(root_folder, lang)

    # Iterate over the .yml files in the folder
    for file_path in glob.glob(f"{folder_path}/*.yml"):
        # Read the content of the .yml file
        with open(file_path, "r", encoding="utf-8") as file:
            content = yaml.safe_load(file)

        # Add the content to the data dictionary with the appropriate suffix
        for key, value in content.items():
            new_key = f"{key}{lang_mapping[lang]}"
            if isinstance(value, str) and is_json(value):
                json_value = json.loads(value)
                if isinstance(json_value, dict):
                    for json_key, json_value in json_value.items():
                        data[f"{new_key}_{json_key}"] = json_value
                else:
                    data[new_key] = value
            else:
                data[new_key] = value

# Save the parsed data as a JSON file
with open("parsed_data.json", "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=2)
