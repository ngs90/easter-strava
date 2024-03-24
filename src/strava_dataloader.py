from config import Config
from utils.auth import create_session

conf = Config()
session = create_session(conf, verify_token=True)
