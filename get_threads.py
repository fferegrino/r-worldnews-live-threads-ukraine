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
from datetime import datetime, timedelta

import pandas as pd
import praw

# %%
begin_point = datetime(2022, 2, 1)
today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=12)

# %%
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    password=os.environ["PASSWORD"],
    user_agent="Live Thread Scraper by UkraineNewsBot",
    username="UkraineNewsBot",
)

# %%
# fmt:off
mods = [
    "qgyh2", "maxwellhill", "BritishEnglishPolice", "anutensil", "bennjammin",
    "DoremusJessup", "emmster", "green_flash", "PraiseBeToScience", "WorldNewsMods",
    "DonTago", "istara", "Fluttershy_qtest", "Surf_Science", "imdpathway",
    "Isentrope", "PlanetGuy", "alexander1701", "wrc-wolf", "10ebbor10",
    "seewolfmdk", "mutatron", "alfix8", "dieyoufool3", "MushroomMountain123",
    "TheEarthquakeGuy", "GrumpyFinn", "BestFriendWatermelon", "NYLaw", "hasharin",
    "tinkthank", "DaisyKitty", "kwwxis", "BlatantConservative", "vikinick",
    "pussgurka", "progress18", "Morning-Chub", "hankhillforprez", "Core_Four",
    "nt337", "sunbolts", "photonmarchrhopi", "PoppinKREAM", "Last_Jedi",
    "ssnistfajen", "FreedomsPower", "Handicapreader", "maybesaydie", "_BindersFullOfWomen_",
    "doc_two_thirty", "moombai", "abrownn", "That_Cupcake", "Llim",
    "slakmehl", "MarktpLatz", "Mazon_Del", "Leerzeichen14", "MisterMysterios",
    "SirT6", "Ferelar", "Captcha_Imagination", "ThaneKyrell", "thatnameagain",
    "loljetfuel", "Tidorith", "Gunboat_DiplomaC", "Petrichordates", "Hard_on_Collider",
    "RedSquirrelFtw", "jfoobar", "ZippyDan", "Yglorba", "AftyOfTheUK",
    "Trips-Over-Tail", "Wonckay", "Turicus", "isnotmad", "Iustis",
    "IsNotACleverMan", "Randvek", "terminal_mole", "grmmrnz", "mvea",
    "Iphotoshopincats", "UGMadness", "ToadProphet", "PapaKnowsDominoes", "L_Cranston_Shadow",
    "allessandro", "MSchmahl", "indi_n0rd", "The_Majestic_", "Benocrates",
    "ThucydidesOfAthens", "Emmx2039", "valuingvulturefix", "Cicero912", "whistleridge",
    "Tetizeraz", "Duglitt", "ontrack", "SecureThruObscure", "AdClemson",
    "jman005", "muffpatty", "FLAlex111", "UrynSM", "-doughboy",
    "AutoModerator", "AkaashMaharaj",
]
# fmt:on

# %%
properties = ["id", "created_utc", "name", "num_comments", "permalink", "score", "title", "upvote_ratio"]

# %%
subs = []
for username in mods:
    user = reddit.redditor(name=username)
    for post in user.submissions.new(limit=200):
        subs.append(post)

# %%
subreddits = []
for post in subs:
    title_low = post.title.lower()
    if (
        title_low.startswith("/r/worldnews live thread")
        or title_low.startswith("r/worldnews live thread")
        or title_low.startswith("worldnews live thread")
    ) and begin_point.timestamp() < post.created_utc < today.timestamp():
        post_props = [post.author.name]
        post_props.extend([getattr(post, pr) for pr in properties])
        subreddits.append(post_props)


# %%
def hash_string(content):
    return hashlib.md5(content.encode()).hexdigest()


# %%
live_threads = pd.DataFrame(subreddits, columns=["author"] + properties)

# %%
live_threads["created_at"] = pd.to_datetime(live_threads["created_utc"], unit="s", origin="unix")
live_threads["author"] = live_threads["author"].apply(hash_string)

# %%
live_threads[["id", "name", "author", "title", "created_utc", "created_at", "num_comments", "score", "upvote_ratio", "permalink"]].sort_values(
    "created_utc", ascending=True
).to_csv("data/threads.csv", index=False)


# %%
