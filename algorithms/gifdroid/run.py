import os
import sys
import shutil
import re
import tempfile
from PIL import Image
import subprocess

from functions.event_to_screen_matcher import *
from functions.artifact_img_converter import *
from functions.artifact_target_creator import *
from functions.timeconverter import main as time_converter

import json

def convert_droidbot_to_gifdroid_utg(utg_file=None, events_folder=None, states_folder=None, **kwargs):
    if utg_file == None:
        utg_file = sys.argv[1]

    if events_folder == None:

        events_folder = sys.argv[2]

    if states_folder == None:
        states_folder = sys.argv[3]

    output_folder = kwargs['output_dir']

    _init_dirs(output_folder)

    ###############################################################################
    #                                 Rename file                                 #
    ###############################################################################
    droidbot_img_file_type = "jpg"
    gifdroid_img_file_type = "png"
    img_files = file_order_sorter(states_folder, droidbot_img_file_type)

    # Gifdroid file format: web-build-[\d.*-\d.\d.]T00/w.*[Android emulator]_\d.*.png
    # Replace first part of filename with web-build which is accepted by gifdroid
    target_files = [re.sub("^\w*-.*-.*\d", "artifacts_", each_img_file) for each_img_file in img_files]

    # rm .jpg
    target_files = [re.sub("." + droidbot_img_file_type + "\Z", "", each_img_file) for each_img_file in target_files]

    with tempfile.TemporaryDirectory() as temporary_directory_name:

        target_files = [
            shutil.copyfile(
                os.path.join(states_folder, img_files[i]),
                os.path.join(temporary_directory_name, each_target_file + str(i) + "." + droidbot_img_file_type)
            ) for i, each_target_file in enumerate(target_files)
        ]

        ###############################################################################
        #                      convert all files from jpg to png                      #
        ###############################################################################
        original_img_file_name = file_order_sorter(temporary_directory_name, droidbot_img_file_type )

        im1 = [ Image.open(os.path.join(temporary_directory_name, file)) for file in file_order_sorter(temporary_directory_name, droidbot_img_file_type )];


        screenshot_output_dir = os.path.join(output_folder, 'screenshots')
        _init_dirs(screenshot_output_dir)
        im1 = [ file.save(os.path.join(screenshot_output_dir, re.sub(".jpg\Z", ".png", original_img_file_name[i]))) for i, file in enumerate( im1 )];

    #############################################################################
    #                             Generate json file                            #
    #############################################################################
    json_output = {"events": []}

    ###############################################################################
    #                                 Extract time                                #
    ###############################################################################
    time = time_converter(utg_file, events_folder)
    time_events = time['events']

    ###############################################################################
    #                                Extract object                               #
    ###############################################################################
    focused_object = find_focused_object_classname(events_folder)

    ###############################################################################
    #                               Extract Sequence                              #
    ###############################################################################
    sequence = match_state_to_event(events_folder=events_folder)

    sequence_of_events = sequence['events']

    ###############################################################################
    #                          Combine data into sequence                          #
    ###############################################################################

    for i in range(len(sequence_of_events)):
        if 'ignore' in focused_object[i] and focused_object[i]['ignore'] == True:
            pass
        else:
            d = sequence_of_events[i].copy()
            d.update(time_events[i])
            d.update(focused_object[i])

            json_output['events'].append(d)

    output_dir = kwargs['output_dir']

    output_file_path = os.path.join(output_dir, 'utg.json')

    with open(output_file_path, 'w') as f:
        json.dump(json_output, f, indent=4)

    return output_file_path


# def enforce_output_directory(output_dir: str) -> None:
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#         screenshots = os.path.join(output_dir, 'screenshots')
#         os.makedirs(screenshots)
#         if not os.path.exists(screenshots):
#             os.makedirs(screenshots)


def _init_dirs(output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

if __name__=="__main__":
    convert_droidbot_to_gifdroid_utg()
