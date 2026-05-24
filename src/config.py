# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

PASSPHRASE = os.getenv("PASSPHRASE", "default_pass")
PROFILE_FILE = os.getenv("PROFILE_FILE", "user_profile.kda")
MIN_TRAIN = int(os.getenv("MIN_TRAIN", 20))
MAX_TRAIN = int(os.getenv("MAX_TRAIN", 30))