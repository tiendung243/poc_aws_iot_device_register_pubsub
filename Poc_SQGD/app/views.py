from django.shortcuts import render
from Poc_SQGD.settings import *
from django.http import HttpResponse
from . import utils
from django.views.decorators.csrf import csrf_exempt
import json
import zlib
import zipfile

@csrf_exempt
def aws_iot_bulk_register_things(request):
    data = json.loads(request.body)
    data["CertificateId"] = THING_CERT
    thing_name = data.get("ThingName")
    print(json.dumps(data))
    file_path = f"{BASE_DIR}/app/awsiot_cert/provision/{thing_name}.json"
    with open(file_path, "w+") as file:
        file.write(json.dumps(data))
    
    key_file = utils.aws_s3_config(file_path, thing_name)
    
    iot_client = utils.aws_iot_register_thing(key_file)
    
    response_data = utils.create_certificate(iot_client)
    certificate_arn = response_data.get("certificate_arn")
    
    # zip_response_data = zlib.compress(json.dumps(response_data).encode())
    zip_file_path = f"{BASE_DIR}/app/zhenlungho_zip/{thing_name}.zip"
    with zipfile.ZipFile(zip_file_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file: 
        # Dump JSON data
        dumped_JSON: str = json.dumps(response_data)
        # Write the JSON data into `data.json` *inside* the ZIP file
        zip_file.writestr("data.json", data=dumped_JSON)
    thing_policy_name = utils.create_thing_policy(iot_client, thing_name)
    utils.attach_certificate_to_thing(iot_client, thing_name, thing_policy_name, certificate_arn)
    return HttpResponse(open(zip_file_path, 'rb').read())
    