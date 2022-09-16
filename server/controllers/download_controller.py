import boto3
import os, shutil
from controllers.update_document_controller import UpdateDocumentController as UDContrl
from download_parsers.strategy import Strategy
from typing import TypeVar, Generic
import tempfile

import subprocess

from download_parsers.gifdroid_json_parser import gifdroidJsonParser

###############################################################################
#                                  Set Up AWS                                 #
###############################################################################
AWS_PROFILE = 'localstack'
AWS_REGION = 'us-west-2'
ENDPOINT_URL = os.environ['S3_URL']
print(ENDPOINT_URL)
BUCKETNAME = "apk-bucket"

boto3.setup_default_session(profile_name=AWS_PROFILE)


s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=ENDPOINT_URL
)

T = TypeVar('T')

class DownloadController(Generic[T]):

    bucket_name = 'apk-bucket'

    def __init__(self, collection_name: str, json_result_file_parser: Strategy) -> None:
        """
        This controller is responsible for download file stored from previous job into the s3 bucket.

        Parameters:
            collection_name - The collection name to refer to for database.
            json_result_file_parser - A strategy for parsing result files into a json to update file names mongodb schema.

        """

        self.cn = collection_name
        self.udc = UDContrl(collection_name, json_result_file_parser)


    def download(self, uuid: str, algorithm: str, type: str, name: str) -> str:
        """
        This controller is responsible for download file stored from previous job into the s3 bucket.

        Parameters:
            collection_name - The collection name to refer to for database.
            json_result_file_parser - A strategy for parsing result files into a json to update file names mongodb schema.

        """

        path = ""
        output = ""

        if algorithm == "gifdroid":
            output = "gifdroid.json"
            path = os.path.join(uuid, algorithm, output)
        elif algorithm == "xbot":
            if type == "issues":

                file_type=".txt"
                output = DownloadController.join_str(name, file_type)

            if type == "images":
                file_type = ".png"
                output = DownloadController.join_str(name, file_type)

            path = os.path.join(uuid, "activity", name, algorithm, type, output)

        elif algorithm == "owleye":

            file_type = ".jpg"
            output = DownloadController.join_str(name, file_type)

            path = os.path.join(uuid, "activity", name, type, output)
        elif algorithm == "activity":
            if type == "images":
                file_type = ".jpg"
                output = DownloadController.join_str(name, file_type)

            path = os.path.join(uuid, "activity", name, type, output)

        print("DOWNLOAD: Downloading file from", os.path.join( "apk-bucket", path ))

        s3_client.download_file(Bucket='apk-bucket', Key=path, Filename=output)

        return output


    def download_all_objects_in_folder(self, uuid: str) -> str:
        """
        Gets all the files out of folder on s3 bucket matching uuid for user to download

        Parameters:
            uuid - str that matches with the job uuid to get a full summary of the job

        Returns: str Path leading to stored summary location.
        """

        # TODO add threading

        # TODO figure out how to use the commented out code to not use subprocess
        # objects = s3_client.objects.filter(Prefix=uuid)
        # objects = s3_client.list_objects(Bucket='apk-bucket')
        # objects = s3_client.Bucket.objects
        # objects = s3_client.list_objects(Bucket='apk-bucket', Prefix=f"/{uuid}/",)
        # print(objects)
        # for obj in objects:
            # _, filename = os.path.split(obj.key)
            # pass
            # print(filename)
            # print(obj)
            # # print(filename)
            # # s3_client.download_file(self.bucket_name, obj.key, filename)

        uuid = "ef1e3bcb-adb7-4980-ab77-f7e094f01871"
        print(uuid)

        with tempfile.TemporaryDirectory() as sys_tmp_folder:
            cwd = os.getcwd()
            local_tmp_save_dir = tempfile.mkdtemp(dir=cwd)
            print(ENDPOINT_URL)
            subprocess.run(['aws', f'--endpoint-url={ENDPOINT_URL}', 's3', 'cp', f's3://{BUCKETNAME}/{uuid}/', local_tmp_save_dir, '--recursive'])

        return local_tmp_save_dir



    # def downloadDirectoryFroms3(self,bucketName, remoteDirectoryName):
    #     s3_resource = boto3.resource(
    #     "s3",
    #     region_name=AWS_REGION,
    #     endpoint_url=ENDPOINT_URL
    #     )

    #     bucket = s3_resource.Bucket(bucketName)
    #     for obj in bucket.objects.filter(Prefix = remoteDirectoryName):
    #         if not os.path.exists(os.path.dirname(obj.key)):
    #             os.makedirs(os.path.dirname(obj.key))
    #         bucket.download_file(obj.key, obj.key) # save to same path


    @staticmethod
    def join_str(str1: str, str2: str) -> str:
        """
        Join 2 texts together
        """

        return str1 + str2
