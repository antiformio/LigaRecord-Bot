import json
import os
import pickle

import boto3
from botocore.exceptions import NoCredentialsError, ClientError


class serialization:

    """
        Loads credentials from JSON and reads into class variables
    """

    def readCredentials(self):
        with open("//Users//filipemartins//Desktop//VScodeProjects//LigaRecord-Bot//s3.json") as f:
            data = json.load(f)
        aws_access_key_id = data["ACCESS_KEY"]
        aws_secret_access_key = data["SECRET_KEY"]
        bucket = data["bucket"]
        return aws_access_key_id, aws_secret_access_key, bucket

    def __init__(self):
        self.ACCESS_KEY, self.SECRET_KEY, self.bucket = self.readCredentials()
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=self.ACCESS_KEY,
            aws_secret_access_key=self.SECRET_KEY,
        )

    """
        Upload a specific file to s3 bucket 
    """

    def AWSupload(self, local_file, s3_file):
        try:
            self.s3.upload_file(local_file, self.bucket, s3_file)
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    """
        Download a specific file from s3 bucket
    """

    def AWSdownload(self, s3_fileName, localPath):
        try:
            # self.s3.download_file(self.bucket,s3_file, 'C:\\Users\\fhm\\Desktop\\dogs')
            self.s3.download_file(self.bucket, s3_fileName, localPath)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("The object does not exist.")
            else:
                raise

    """
        Returns a list with all the files in bucket (started by 'df')
            prefixo: 'df' for example, all files starting by 'df'
    """

    def getFilesOnBucket(self, prefixo):
        list = []
        response = self.s3.list_objects(Bucket=self.bucket, Prefix=prefixo)
        for elemento in response["Contents"]:
            list.append(elemento["Key"])
        return list
