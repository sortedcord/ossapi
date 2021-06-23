from ossapi import OssapiV2

import os

client_id = os.environ.get("OSU_API_CLIENT_ID")
client_secret = os.environ.get("OSU_API_CLIENT_SECRET")

if not client_id:
    client_id = input("Enter your api v2 client id: ")
if not client_secret:
    client_secret = input("Enter your api v2 client secret: ")

client_id = int(client_id)
api = OssapiV2(client_id, client_secret, strict=True)
