import boto3
import os
import subprocess
import pathlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# aws info for development environment
AWS_REGION = 'us-west-2'
AWS_PROFILE = 'localstack'
ENDPOINT_URL = os.environ.get('S3_URL')

# aws s3 client
boto3.setup_default_session(profile_name=AWS_PROFILE)
s3_client = boto3.client("s3", region_name=AWS_REGION,
                         endpoint_url=ENDPOINT_URL)

# home route
@app.route('/')
def home():
    return "Story distiller app is live."

# route for starting new job
@app.route("/new_job", methods=["POST"])
def send_uid_and_signal_run():
    if request.method == "POST":
        try:
            print('NEW JOB FOR UUID: ' + request.get_json()["uid"])
            uid = request.get_json()["uid"]
        except:
            return 'Invalid uuid data', 500

        _service_execute(uid)

        return jsonify( {"result": "SUCCESS"} ), 200


    return "No HTTP POST method received", 500


def _service_execute(uuid):
    print('Beginning new job for %s' % uuid)
    apk_name = _get_apk_name(uuid)
    dl_name = _get_dl_name(uuid)

    # backup original source code
    subprocess.run(["cp", "-r", "/home/ui-checker", "/home/tmp/ui-checker"])

    _get_data(uuid, apk_name, dl_name)
    print('APK name for %s is %s' % (uuid, apk_name))

    print('Running ui-checker')
    _process_result()
    print('Successfully ran')
    print('Uploading results')
    _upload_result(uuid, apk_name)
    print('Successfully uploaded')

    # restore original source code
    subprocess.run(["rm", "-r", "/home/ui-checker"])
    subprocess.run(["cp", "-r", "/home/tmp/ui-checker", "/home/ui-checker"])
    subprocess.run(["rm", "-r", "/home/tmp/ui-checker"])
    print('Job for %s complete' % uuid)

# get name of file stored where key==uuid in s3
def _get_apk_name(uuid):
    response = s3_client.list_objects_v2(Bucket='apk-bucket', Prefix=uuid)
    contents = response['Contents']
    apk_name = contents[0]['Key'].replace(uuid+'/', '').replace('.apk', '')
    return apk_name

# get name of file stored where key==uuid in s3
def _get_dl_name(uuid):
    response = s3_client.list_objects_v2(Bucket='dl-bucket', Prefix=uuid)
    contents = response['Contents']
    dl_name = contents[0]['Key'].replace(uuid+'/', '').replace('.dl', '')
    return dl_name

# get the required inputs from s3
def _get_data(uuid, apk_name, dl_name):
    filepath = '/home/ui-checker/%s.apk' % apk_name
    s3_client.download_file('apk-bucket', '%s/%s.apk' % (uuid, apk_name), filepath)
    filepath = '/home/ui-checker/%s.dl' % dl_name
    s3_client.download_file('dl-bucket', '%s/%s.dl' % (uuid, dl_name), filepath)

# run the algorithm
def _process_result(apk_name, dl_name):
    os.chdir("/home/ui-checker")
    subprocess.run(["./uicheck", "%s.apk" %apk_name, "%s.dl" %dl_name])
    os.chdir("/home/ui-checker/output_markii/%s.apk/" %apk_name)

# upload results to s3
def _upload_result(uuid, apk_name):

    bucket = 'ui-checker-bucket'
    output_root_path = '/home/ui-checker/output_markii/%s.apk/' %apk_name

    # upload output folder zip
    output_filename = 'ui-checker_output_%s.zip' % apk_name
    os.chdir(output_root_path)
    os.system('zip -r %s %s' % (output_filename, apk_name))

    output_folder_path = output_root_path + output_filename
    s3_output_path = 'output-full/%s/%s' % (uuid, output_filename)
    s3_client.upload_file(output_folder_path, bucket, s3_output_path)
    os.system('rm -r %s' % (output_filename))
    os.chdir("/home")

    # upload issues (image and text description file)
    issues_root_path = output_root_path + apk_name
    s3_issues_path = 'markii/%s' % uuid

    for (root, _, filenames) in os.walk(issues_root_path):
        for file in filenames:
            issue_name = file[:-4]
            if (pathlib.Path(file).suffix == '.csv'):
                s3_client.upload_file(os.path.join(root,file), bucket, s3_issues_path+'/%s' %file)

if __name__=='__main__':
    app.run(debug=True, host="0.0.0.0", port=3003)
    
    # test run
    #_service_execute('a2dp.Vol_133')
