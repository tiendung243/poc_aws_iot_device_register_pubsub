import requests
import json
import zipfile
import uuid
from awsiot import mqtt_connection_builder, mqtt
import os
from io import BytesIO
import time
import threading
import shutil
from settings import *
 
def on_receive_message(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    
def get_cert_pubsub_iot_core():
    environment = ENVIRONTMENT
    region = AWS_REGION
    thing_name = THING_NAME
    # sit/global/VM1/#
    payload = {
        "ThingName": thing_name,
        "ThingId": "5893452",
        "ThingSerialNumb": "SN324"
    }
    url = f"{BASE_URL}/{API_URL}"
    response_data = requests.post(url, data=json.dumps(payload), stream=True)
    file_content = response_data.content
    path_file = os.path.join(os.getcwd(), "thing_pubsub", "cert_file", f"data_{thing_name}")
    with zipfile.ZipFile(BytesIO(file_content)) as zip_file:
        zip_file.extractall(path_file)
    cert_data = json.load(open(os.path.join(path_file, "data.json"), "r"))
    
    private_key = cert_data.get("key_private")
    certificate = cert_data.get("certificate")
    endpoint = cert_data.get("endpoint")
    root_CA = cert_data.get("root_CA")
    client_id = str(uuid.uuid4())
    
    path_to_connection_files = os.path.join(THING_PUBSUB_DIR, "cert_file", "connection_credential", "thing_name")
    isExist = os.path.exists(path_to_connection_files)
    if not isExist:
        # Create a new directory because it does not exist 
        os.makedirs(path_to_connection_files)
    cert_filepath=os.path.join(path_to_connection_files, f"certificate_{thing_name}.pem")
    pri_key_filepath=os.path.join(path_to_connection_files, f"private_key_{thing_name}.pem.key")
    ca_filepath=os.path.join(path_to_connection_files, f"root_CA_{thing_name}.pem")
    # write cert, root cert, private key 
    with open(cert_filepath, "w+") as file:
        file.write(certificate)
    with open(pri_key_filepath, "w+") as file:
        file.write(private_key)
    with open(os.path.join(path_to_connection_files, f"endpoint_{thing_name}.txt"), "w+") as file:
        file.write(endpoint)
    with open(os.path.join(path_to_connection_files, f"client_id_{thing_name}.txt"), "w+") as file:
        file.write(client_id)
    with open(ca_filepath, "w+") as file:
        file.write(root_CA)
    print(endpoint)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=cert_filepath,
        pri_key_filepath=pri_key_filepath,
        ca_filepath=ca_filepath,
        client_id=CLIENT_ID,
        keep_alive_secs=30
    )
    future = mqtt_connection.connect()
    future.result()
    topic_name = f"{environment}/{region}/{thing_name}/#"
    print(f"starting subcribe topic name {topic_name}")
    path_zip_file = os.path.join(path_to_connection_files, "cert.zip")
    shutil.make_archive(path_zip_file, 'zip', path_to_connection_files)
    
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topic_name,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_receive_message
    )
    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))
    if not receive_all_event.isSet():
        print("Waiting for message")
    receive_all_event.wait()


receive_all_event = threading.Event()
if __name__ == '__main__':
    import time
    get_cert_pubsub_iot_core()

    