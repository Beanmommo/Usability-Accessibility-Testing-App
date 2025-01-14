from converter.functions.artifact_img_converter import file_order_sorter
from converter.run import convert_droidbot_to_gifdroid_utg
from flask import Flask, request, jsonify
from os import path
import subprocess
import requests
import tempfile
import boto3
import json
import os


app = Flask(__name__)
###############################################################################
#        Load user config file gifdroid algorithm running configuration       #
###############################################################################

with open("config.json", "r") as f:
    config = json.load(f)

endpoint_url = os.environ.get("S3_URL")

if endpoint_url == None:
    endpoint_url = config['ENDPOINT_URL']

status_api = str( os.environ.get("STATUS_API") )

file_api = str( os.environ.get("FILE_API") )

if file_api == None:
    endpoint_url = config['FILE_API']


EMULATOR = os.environ.get( "EMULATOR" )

flask_backend = os.environ.get( "FLASK_BACKEND" )

###############################################################################
#                                Set up AWS S3                                #
###############################################################################

boto3.setup_default_session(profile_name=config[ 'AWS_PROFILE' ])
s3_client = boto3.client(
    "s3",
    region_name=config['AWS_REGION'],
    endpoint_url=endpoint_url,
)

result_bucket_folder = "report"
apk_bucket_folder = "apk"

@app.route("/new_job", methods=["POST"])
def send_uid_and_signal_run():
    """
    This function creates a new job for gifdroid and droidbot to run together.

    POST req input:
    uid - The unique ID for tracking all the current task.
    """
    if request.method == "POST":
        print('NEW JOB FOR UUID: ' + request.get_json()["uid"])

        # Get the UUID from the request in json #######################################
        uid = request.get_json()["uid"]

        # Execute droidbot ############################################################
        _service_execute_droidbot(uid)

        # Execute gifdroid ############################################################
        _service_execute_gifdroid(uid)

        return jsonify( {"result": "SUCCESS"} ), 200

    return "No HTTP POST method received", 400


def _service_execute_droidbot(uuid):
    """
    This function execute droidbot algorithm responsible for getting the utg.js file.

    Parameters:
        uuid - The unique id for the current task.
    """

    print('Beginning new job for %s' % uuid)

    ###############################################################################
    #                      GET the APK file name from mongodb                     #
    ###############################################################################
    print("[1] Getting session information")

    OUTPUT_DIR = os.path.join( tempfile.gettempdir(), uuid )
    get_file_url = os.path.join(file_api,  uuid)

    data = requests.get(get_file_url, headers={'Content-Type': 'application/json'}).json()

    # Apk has an Array/List of apk files ##########################################
    apk_filename = data['apk']['name']

    ############################################################################
    #                    Download file into temporary folder                   #
    ############################################################################
    temp_dir = tempfile.gettempdir()

    print("[2] Getting file from bucket using UUID " + uuid + " and apk file " + apk_filename + ".")

    target_apk = path.join(temp_dir, apk_filename)

    s3_client.download_file(
        Bucket='apk-bucket',
        Key=path.join(uuid, apk_bucket_folder, apk_filename),
        Filename = target_apk
    )


    ############################################################################
    #                      Run program with downloaded apk                     #
    ############################################################################
    print("[3] Running Droidbot app")
    os.chdir("/home/droidbot")

    subprocess.run([ "adb", "connect", EMULATOR])

    subprocess.run([ "droidbot", "-count", config[ "NUM_OF_EVENT" ], "-a", target_apk, "-o", OUTPUT_DIR])

    ###############################################################################
    #                                Save utg file                                #
    ###############################################################################
    print("[4] Saving utg.js file to bucket.")
    enforce_bucket_existance([config[ "BUCKET_NAME" ], "storydistiller-bucket", "xbot-bucket"])


def _service_execute_gifdroid(uuid):
    # retrieve utg file name from mongodb

    OUTPUT_DIR = os.path.join( tempfile.gettempdir(), uuid )

    ###############################################################################
    #                        Convert utg to correct format                        #
    ###############################################################################
    utg = os.path.join(OUTPUT_DIR, config['DEFAULT_UTG_FILENAME'])
    events = os.path.join(OUTPUT_DIR, "events" )
    states = os.path.join(OUTPUT_DIR, "states")

    convert_droidbot_to_gifdroid_utg(utg, events, states)

    ###############################################################################
    #                          Get gif file from frontend                         #
    ###############################################################################
    os.chdir("/home/gifdroid")

    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    get_file_url = os.path.join(file_api, uuid)

    response = requests.get(get_file_url, headers=headers)

    lookup = response.json()

    for item in lookup['additional_files']:
        if item['algorithm'] == 'gifdroid':
            gif_file = item['name']

    ###############################################################################
    #                          Upload image result files                          #
    ###############################################################################
    result_img_file_type = "png"
    image_output = "../droidbot/output"
    result_img_files = file_order_sorter(image_output, result_img_file_type)

    upload_directory(image_output, config["BUCKET_NAME"], uuid)

    download_links = [ os.path.join( "http://localhost:5005", "download_result", uuid, result_bucket_folder) + "/" + file for file in result_img_files ]

    insert_result(uuid, download_links, 'images', result_img_files)

    s3_client.download_file(
        Bucket=config["BUCKET_NAME"],
        Key=path.join(uuid, "additional_upload", gif_file),
        Filename = gif_file
    )

    ###############################################################################
    #                               Run GIFDROID app                              #
    ###############################################################################
    print("[3] Running GIFDROID app")

    subprocess.run([ "python3", "main.py", "--video=./" + gif_file, "--utg=" + "../droidbot/utg.json", "--artifact=../droidbot/output", "--out=" + config["OUTPUT_FILE"]])

    enforce_bucket_existance([config[ "BUCKET_NAME" ], "storydistiller-bucket", "xbot-bucket"])

    ###############################################################################
    #                          Save result onto s3 bucket                         #
    ###############################################################################

    print("[4] Uploading json file to bucket")
    s3_client.upload_file(
        config[ "OUTPUT_FILE" ],
        config[ 'BUCKET_NAME' ],
        os.path.join(uuid, result_bucket_folder, config[ "OUTPUT_FILE" ] )
    )

    ###############################################################################
    #                            mongo: Update mongodb                            #
    ###############################################################################
    print("[5] Updating mongodb for traceability")

    # Download images doesn't need to know the type of file. Just need to identify the file
    download_link = os.path.join( "http://localhost:5005", "download_result", uuid, "report") + "/" + config['OUTPUT_FILE']

    insert_result(uuid, [download_link], 'json', [config['OUTPUT_FILE']])

    return 200


@app.route("/", methods=["GET"])
def check_health():
    """
    Check that gifdroid is in good health.
    """

    return "Gifdroid is live!"

###############################################################################
#                              Utility Functions                              #
###############################################################################

def bytes_to_json(byte_str: bytes):
    data = byte_str.decode('utf8').replace("'", '"')
    data = json.loads(data)

    return data

def upload_directory(path, bucketname, uuid):
    for root, _, files in os.walk(path):
        for file in files:
            key = os.path.join(uuid, result_bucket_folder, file)

            s3_client.upload_file(os.path.join(root, file), bucketname, key)


def enforce_bucket_existance(buckets):
    for bucket in buckets:
        try:
            s3_client.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
        except:
            print("Bucket already exists %s".format( bucket ))


def update_status(uuid: str, status: str):
    flask_backend = os.environ["FLASK_BACKEND"]
    request_url = os.path.join(flask_backend, 'result', uuid) + "/" + 'gifdroid'

    data =  {
        "files": result_files,
        "type": type
    }

    res = requests.post(request_url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))

    return res


def insert_result(uuid, result_files: list, type: str, file_names: list):
    # NOTE the request link MUST NOT have an additional /
    flask_backend = os.environ["FLASK_BACKEND"]
    request_url = os.path.join(flask_backend, 'result/add', uuid) + "/" + 'gifdroid'

    data =  {
        "files": result_files,
        "type": type,
        "names": file_names
    }

    res = requests.post(request_url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))

    return res


if __name__ == "__main__":
    # No point doing debug mode True because can't debug on docker
    app.run(host="0.0.0.0", port=3005)



