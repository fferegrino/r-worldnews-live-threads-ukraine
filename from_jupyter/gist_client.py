import json

import requests

URL = "https://api.github.com/gists"


class GistClient:
    def __init__(self, personal_token):
        self.headers = {"Authorization": f"token {personal_token}"}
        self.params = {"scope": "gist"}

    def update_gist(self, gist_id: str, description: str, file_name: str, content: str):
        payload = {"description": description, "public": True, "files": {file_name: {"content": content}}}
        result = requests.post(URL + f"/{gist_id}", headers=self.headers, params=self.params, data=json.dumps(payload))
        parsed = json.loads(result.text)
        return parsed["id"]

    def publish_gist(self, description: str, file_name: str, content: str):
        payload = {"description": description, "public": True, "files": {file_name: {"content": content}}}
        result = requests.post(URL, headers=self.headers, params=self.params, data=json.dumps(payload))
        parsed = json.loads(result.text)
        return parsed["id"]
