import json

SECRET_PATH = "/home/aerotract/NAS/main/pix4d_server/share/secrets.json"

def load_secrets(path):
    with open(path, "r") as fp:
        contents = fp.read()
    return json.loads(contents)

def get_urls(path=SECRET_PATH):
    return load_secrets(path)["IPS"]

def get_license(path=SECRET_PATH):
    return load_secrets(path)["PIX4D_LICENSE"]
