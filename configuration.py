import tomllib
import praw

data = {}
with open("configuration.toml", "rb") as f:
    data = tomllib.load(f)

def get_default_arguments():
    return data["DEFAULT"]

def use_custom_path():
    return data["custom_path"]["use_custom_path"]

def get_custom_path():
    return data["custom_path"]["custom_path"]

def authenticate():
	return praw.Reddit(data["PRAW"]["application"], user_agent="reddio test bot")