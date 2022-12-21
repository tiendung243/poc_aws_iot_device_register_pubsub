import requests
import json
import zipfile
import uuid
from awsiot import mqtt_connection_builder, mqtt
import time
import os
from io import BytesIO
 
ROOT_DIR = os.getcwd()
 
def publish_one_message_per_second(mqtt_connection, topic_name):
    current_number = 0
    while 1:
        current_number += 1
        future, _ = mqtt_connection.publish(
            topic=topic_name,
            payload=f"just a testing message {current_number}",
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        time.sleep(1)

def on_receive_message(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))

def get_cert_pubsub_iot_core():
    thing_name = "SWIRE-SDK-finaltest8"
    payload = {
        "ThingName": thing_name,
        "ThingId": "5489851245",
        "ThingSerialNumb": "SN20"
    }
    url = " https://fb60-27-72-96-161.ap.ngrok.io/api/register_bulk_things_iot_core"
    response_data = requests.post(url, data=json.dumps(payload), stream=True)
    file_content = response_data.content
    path_file = os.path.join(os.getcwd(), "thing_pubsub", "cert_file", f"data_{thing_name}")
    with zipfile.ZipFile(BytesIO(file_content)) as zip_file:
        zip_file.extractall(path_file)
    cert_data = json.load(open(path_file + "/data.json", "r"))
    
    private_key = cert_data.get("key_private")
    certificate = cert_data.get("certificate")
    endpoint = cert_data.get("endpoint")
    root_CA = cert_data.get("root_CA")
    client_id = str(uuid.uuid4())
    
    path_to_connection_files =  f"{ROOT_DIR}/cert_file/connection_credential"
    isExist = os.path.exists(path_to_connection_files)
    if not isExist:
        # Create a new directory because it does not exist 
        os.makedirs(path_to_connection_files)
    cert_filepath=f"{path_to_connection_files}/certificate_{thing_name}.pem"
    pri_key_filepath=f"{path_to_connection_files}/private_key_{thing_name}.pem.key"
    ca_filepath=f"{path_to_connection_files}/root_CA_{thing_name}.pem"
    # write cert, root cert, private key 
    with open(cert_filepath, "w+") as file:
        file.write(certificate)
    with open(pri_key_filepath, "w+") as file:
        file.write(private_key)
    with open(f"{path_to_connection_files}/endpoint_{thing_name}.txt", "w+") as file:
        file.write(endpoint)
    with open(f"{path_to_connection_files}/client_id_{thing_name}.txt", "w+") as file:
        file.write(client_id)
    with open(ca_filepath, "w+") as file:
        file.write(root_CA)
    print(endpoint)
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
    mqtt_connection.subscribe(
        topic=topic_name,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_receive_message
    )
    print(f"publishing message to topic name {topic_name}")
    publish_one_message_per_second(mqtt_connection, topic_name)


if __name__ == '__main__':
    get_cert_pubsub_iot_core()