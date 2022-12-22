from dotenv import load_dotenv
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
THING_PUBSUB_DIR = os.getcwd()

load_dotenv(os.path.join(ROOT_DIR, ".env"))

ENVIRONTMENT = os.environ.get("ENVIRONTMENT")
AWS_REGION = os.environ.get("AWS_REGION")
THING_NAME = os.environ.get("THING_NAME")
BASE_URL = os.environ.get("BASE_URL")
API_URL = os.environ.get("API_URL")
ENDPOINT = os.environ.get("ENDPOINT")
CLIENT_ID = os.environ.get("CLIENT_ID")

