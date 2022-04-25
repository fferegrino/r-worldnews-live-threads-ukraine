# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import hashlib
import os
import time
from datetime import datetime

import pandas as pd
import praw
from praw.models import MoreComments

# %%
LIMIT = None
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    password=os.environ["PASSWORD"],
    user_agent="Live Thread Scraper by UkraineNewsBot",
    username="UkraineNewsBot",
)

# %%
threads = pd.read_csv("data/threads.csv")
threads.head()

# %%
comment_props = [
    "id",
    "body",
    "edited",
    "created_utc",
    "link_id",
    "parent_id",
    "distinguished",
    "depth",
    "ups",
    "downs",
    "score",
    "total_awards_received",
    "gilded",
]


def hash_string(content):
    return hashlib.md5(content.encode()).hexdigest()


def extract_comment(comment, submission_id):
    if comment.author:
        cmmt = [hash_string(comment.author.name), submission_id]
    else:
        cmmt = [None, submission_id]

    cmmt.extend([getattr(comment, prop) for prop in comment_props])

    if comment.gildings:
        gildings = str(comment.gildings)
    else:
        gildings = None

    cmmt.append(gildings)

    return cmmt


# %%
# raw_cmt = []
for idx, row in threads.iterrows():
    comments = []
    submission_id = row["id"]
    file_name = f"data/comments/comments__{submission_id}.csv"
    if os.path.exists(file_name):
        # print(f"Skipping {submission_id}")
        continue

    t0 = time.time()

    dt_object = datetime.fromtimestamp(t0)
    date_date = dt_object.strftime("%m/%d/%Y, %H:%M:%S")

    print(f"Processing {submission_id} – {date_date}")

    submission = reddit.submission(id=submission_id)
    submission.comments.replace_more(limit=LIMIT)
    comment_queue = submission.comments[:]
    while comment_queue:
        comment = comment_queue.pop(0)
        comments.append(extract_comment(comment, submission_id))
        comment_queue.extend(comment.replies)

    frame = pd.DataFrame(comments, columns=["author", "submission_id"] + comment_props + ["gildings"])
    frame.to_csv(file_name, index=False)

    t1 = time.time()
    print(f"Done processing {len(comments)} comments from {submission_id}: {t1-t0}")

# %%
