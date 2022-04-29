import datetime
import json
from pathlib import Path

from kaggle import api

schema_fields = [
    ("author", "A hashed version of the poster's username", "string"),
    ("submission_id", "A string identifier of the thread", "string"),
    ("id", "A string identifier of the comment", "string"),
    ("body", "The comment's content", "string"),
    ("edited", "A flag that specifies if the comment has been edited – contains a timestamp if it has", "string"),
    ("created_utc", "An epoch timestamp of when the comment was posted", "number"),
    ("link_id", "A string identifier of the thread", "string"),
    ("parent_id", "A string identifier of the parent comment", "string"),
    ("distinguished", "A flag that specifies if the comment was made by a moderator on duty", "string"),
    ("depth", "The overall depth of the comment tree", "number"),
    ("ups", "The score of a comment (ups-downs)", "number"),
    ("downs", "As of now, this column is always 0", "number"),
    ("score", "The score of a comment (ups-downs)", "number"),
    ("total_awards_received", "The number of awards received by a comment", "number"),
    ("gilded", "Whether the comment has been gilded", "boolean"),
    ("gildings", "The gildings received by a comment, if any", "string"),
]


def prepare_metadata():
    with open("dataset-metadata.json") as r:
        dataset_metadata = json.load(r)

    comments_folder = Path("data/comments")

    resources = []
    for csv_file in comments_folder.glob("*.csv"):
        _, _, thread = csv_file.stem.partition("__")
        schema = []
        for name, description, _type in schema_fields:
            schema.append({"name": name, "description": description, "type": _type})
        resource = {"path": str(csv_file)[5:], "description": f"Comments submitted to the {thread} thread", "schema": {"fields": schema}}
        resources.append(resource)

    dataset_metadata["resources"].extend(resources)

    with open("data/dataset-metadata.json", "w") as w:
        json.dump(dataset_metadata, w, indent=4)


prepare_metadata()


update_time = datetime.datetime.utcnow().strftime("%B %d %Y - %H:%M:%S")

api.dataset_create_version("data", f"Update at {update_time}", dir_mode="zip", quiet=False)
