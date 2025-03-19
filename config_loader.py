import json
import os

def load_config():

  config_path = os.path.join(os.path.dirname(__file__), "config.json")
  with open(config_path, "r") as file:
    config_dict = json.load(file)

  return config_dict

CONFIG = load_config()