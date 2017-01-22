"""
This module will copy all required files into a folder deployable to Heroku.
Heroku has requirements on folder structure and files locations, so instead of changing application folder structure will
create a separate sub-folder for Heroku deployment.
"""
import os
import shutil
HEROKU_FOLDE_NAME = "s_classifieds_heroku"
APPLICATION_FOLDER = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.dirname(APPLICATION_FOLDER)
# go one level up
HEROKU_FOLDER_PATH = os.path.join(os.path.dirname(APPLICATION_FOLDER), HEROKU_FOLDE_NAME)

SUBFOLDERS_TO_COPY = ("templates", "static")
FILE_EXTENSIONS_TO_INCLUDE = (".css", ".html", ".py")
OTHER_FILES_TO_INCLUDE = ("Procfile", "requirements.txt")
HEROKU_OPTION_TAG = "DEPLOYED_TO_HEROKU"
OPTIONS_FILE_NAME = "options.py"


def update_heroku_option(option_file_name, heroku_option_tag=HEROKU_OPTION_TAG):
    input_data = [l for l in open(option_file_name, 'r')]
    with open(option_file_name, mode='wt') as output_file:
        for l in input_data:
            if HEROKU_OPTION_TAG in l:
                l = l.replace("False", "True")
            output_file.write(l)


def file_should_be_copied(file_name):
    copy_file = False
    for ext in FILE_EXTENSIONS_TO_INCLUDE:
        if file_name.endswith(ext):
            copy_file = True
            return copy_file

    if file_name in OTHER_FILES_TO_INCLUDE:
        copy_file = True
        return copy_file
    return copy_file

if not os.path.exists(HEROKU_FOLDER_PATH):
    os.makedirs(HEROKU_FOLDER_PATH)


for sub_folder in SUBFOLDERS_TO_COPY:
    source = os.path.join(APPLICATION_FOLDER, sub_folder)
    destination = os.path.join(HEROKU_FOLDER_PATH, sub_folder)
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)

application_files = \
    [os.path.join(APPLICATION_FOLDER, f) for f in os.listdir(APPLICATION_FOLDER) if os.path.isfile(os.path.join(APPLICATION_FOLDER, f))]

main_folder_files = \
    [os.path.join(MAIN_FOLDER, f) for f in os.listdir(MAIN_FOLDER) if os.path.isfile(os.path.join(MAIN_FOLDER, f))]

all_source_files = application_files + main_folder_files

dest_files = [os.path.join(HEROKU_FOLDER_PATH, f) for f in os.listdir(HEROKU_FOLDER_PATH) if os.path.isfile(os.path.join(HEROKU_FOLDER_PATH, f))]

for f in dest_files:
    os.remove(f)

for source_file in all_source_files:
    filename = os.path.basename(source_file)
    if file_should_be_copied(filename):
        shutil.copy(source_file, os.path.join(HEROKU_FOLDER_PATH, filename))

update_heroku_option(os.path.join(HEROKU_FOLDER_PATH, OPTIONS_FILE_NAME))