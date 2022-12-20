import requests
import json
import zipfile
import uuid
from awsiot import mqtt_connection_builder, mqtt
import time
import os
 
ROOT_DIR = os.getcwd()
 
def publish_one_message_per_second(mqtt_connection, topic_name):
    current_number = 0
    while 1:
        print(current_number)
        current_number += 1
        future, _ = mqtt_connection.publish(
            topic=topic_name,
            payload=f"just a testing message {current_number}",
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(current_number)
        time.sleep(1)

def on_receive_message(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))

def get_cert_pubsub_iot_core():
    thing_name = "SWIRE-SDK-95"
    # payload = {
    #     "ThingName": thing_name,
    #     "ThingId": "123456",
    #     "ThingSerialNumb": "SN03"
    # }
    # url = "http://127.0.0.1:8000/aws_iot_bulk_register_things"
    # response_data = requests.post(url, data=json.dumps(payload), stream=True)
    # file_content = response_data.content
    # path_file = os.path.join(os.getcwd(), "thing_pubsub", "cert_zip_file", f"cert_zip_file_{thing_name}.zip")
    # with open(path_file, "wb+") as file:
    #     file.write(file_content)
    # path_file_unzip = f"cert_file"
    # with zipfile.ZipFile(path_file, 'r') as zip_file:
    #     content = zip_file.extractall(path_file_unzip)
    # cert_data_file = open(path_file_unzip + "/data.json")
    # cert_data = json.load(cert_data_file)
    
    # private_key = cert_data.get("key_private")
    # certificate = cert_data.get("certificate")
    # endpoint = cert_data.get("endpoint")
    # root_CA = cert_data.get("root_CA")
    # client_id = str(uuid.uuid4())
    
    path_to_connection_files =  f"{ROOT_DIR}/cert_file/connection_credential"
    # isExist = os.path.exists(path_to_connection_files)
    # if not isExist:
    #     # Create a new directory because it does not exist 
    #     os.makedirs(path_to_connection_files)
    cert_filepath=f"{path_to_connection_files}/certificate_{thing_name}.pem"
    pri_key_filepath=f"{path_to_connection_files}/private_key_{thing_name}.pem.key"
    ca_filepath=f"{path_to_connection_files}/root_CA_{thing_name}.pem"
    # # write cert, root cert, private key 
    # with open(cert_filepath, "w+") as file:
    #     file.write(certificate)
    # with open(pri_key_filepath, "w+") as file:
    #     file.write(private_key)
    # with open(f"{path_to_connection_files}/endpoint_{thing_name}.txt", "w+") as file:
    #     file.write(endpoint)
    # with open(f"{path_to_connection_files}/client_id_{thing_name}.txt", "w+") as file:
    #     file.write(client_id)
    # with open(ca_filepath, "w+") as file:
    #     file.write(root_CA)
    # print(endpoint)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint="afqs0qlhy6qg3-ats.iot.ap-southeast-1.amazonaws.com",
        cert_filepath=cert_filepath,
        pri_key_filepath=pri_key_filepath,
        ca_filepath=ca_filepath,
        client_id="d8a94edc-179f-4d56-97d8-623e31bf1d4c",
    )
    future = mqtt_connection.connect()
    future.result()
    topic_name = "andy_testing_topic"
    print(f"starting subcribe topic name {topic_name}")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topic_name,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_receive_message
    )
    print(f"publishing message to topic name {topic_name}")
    publish_one_message_per_second(mqtt_connection, topic_name)


if __name__ == '__main__':
    get_cert_pubsub_iot_core()