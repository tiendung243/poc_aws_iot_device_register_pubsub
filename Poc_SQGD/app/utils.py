import boto3
from Poc_SQGD.settings import *
import time
import uuid


def aws_s3_config(file_path, thing_name):
    s3_client = boto3.client("s3", AWS_REGION)
    print(f"connecting to s3 {AWS_REGION}")
    key_file = f"provisioning_data_files/{thing_name}.json"
    s3_client.put_object(Body=open(file_path, "rb"),
                         Bucket=S3_BUCKET_NAME, Key=key_file)
    return key_file
    

def aws_iot_register_thing(key_file):
    print("Starting register new thing.")
    iot_client = boto3.client("iot", AWS_REGION)
    f = open(PROVISION_TEMPLATE_FILE_PATH, "r")
    iot_client.start_thing_registration_task(templateBody=f.read(), 
                                    inputFileBucket=S3_BUCKET_NAME,
                                    inputFileKey=key_file,
                                    roleArn=ROLE_ARN)
    return iot_client

def create_certificate(iot_client):
    print("Starting create certificate.")
    response = iot_client.create_keys_and_certificate(setAsActive=True)
    # Get the certificate and key contents
    certificate = response["certificatePem"]
    certificate_arn = response["certificateArn"]
    key_public = response["keyPair"]["PublicKey"]
    key_private = response["keyPair"]["PrivateKey"]
    root_ca_file = open(CERT_FOLDER_PATH + "/rootCA.pem", "r")
    root_ca = root_ca_file.read()
    response_data = {
        "key_public": key_public,
        "key_private": key_private,
        "certificate": certificate,
        "certificate_arn":certificate_arn,
        "root_CA": root_ca,
        "endpoint": IOT_SERVER_ENDPOINT
    }
    return response_data
    
    
def create_thing_policy(iot_client, thing_name):
    print("starting create thing policy and attach to")
    f = open(PATH_TO_POLICY, "r")
    policyDoc_str = f.read()
    thing_policy_name = thing_name + str(uuid.uuid4())
    iot_client.create_policy(
        policyName=thing_policy_name, policyDocument=policyDoc_str)
    return thing_policy_name
    

def attach_certificate_to_thing(iot_client, thing_name, thing_policy_name, certificate_arn):
    print("attaching cert to thing...")
    iot_client.attach_thing_principal(
                thingName=thing_name, principal=certificate_arn)
    print("attaching policy to certificate...")
    iot_client.attach_principal_policy(
                policyName=thing_policy_name, principal=certificate_arn)
