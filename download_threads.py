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

# %% gist="imports.py" gist_id="a3a36415e9546e2a9d4258d98aec5b7d" tags=[]
import hashlib
import os
from datetime import datetime, timedelta

import pandas as pd
import praw

# %% [markdown]
# ## Motivation
#
# Ever since Russia's "special military operation" in Ukraine started, I have been doomscrolling the comments in the [r/worldnews subreddit](https://www.reddit.com/r/worldnews) live threads. I saw with amazement how the frequency of comments increased with each major event but also noticed how each day there were fewer and fewer comments showing a sustained decrease of interest (at least when measured by Reddit comments) on the topic of the invasion.
#
# This prompted me to find all the live threads in an attempt to figure out whether my feeling was true or not. The following two posts are a result of this curiosity; in the first one (the one you are reading now) I'll show you how I created the dataset, whereas in the second one, you will find how to use the data.

# %% [markdown]
# ## The Reddit API
#
# There are a couple of ways to download data from the internet web scraping or APIs (when available): web scraping is my favourite, but at the same time, the most time consuming and fragile to maintain since any change to the layout makes your scraping go wild.
#
# Luckily for us, Reddit offers an API one can use to consume data from the site.
#
# As with most major websites APIs, to start using this api, one needs to [register an application](https://www.reddit.com/prefs/apps/) - my recommendation is that you create an entirely different Reddit account since you will also have to use the password of said account to authenticate.
#
# When your app has been created, make a note of the following values as we will use them too:
#
# ![Reddit secrets to keep track of](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/created.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651313287355)

# %% [markdown]
# ### PRAW to use the Reddit API
#
# To consume the API via Python, we will be using the PRAW package. Installable using Python with `pip install praw`.
#
# Once we have got our client id and secret we can move on to create a `praw.Reddit` instance passing the information we just got from Reddit; to avoid hardcoding our password and secrets let's use environment variables to set these values:

# %% gist="client_creation.py" gist_id="fb0a912c5375693f142ab552f1a10aea" tags=[]
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    password=os.environ["PASSWORD"],
    user_agent="Live Thread Scraper by UkraineNewsBot",
    username="UkraineNewsBot",
)


# %% [markdown]
# ### Hashing function
#
# We will use a function that takes a string and messes with it in a deterministic manner, this is to "mask" some values that I do not think should be made public, or at least, not so easily.

# %% gist="hashing_function.py" gist_id="f19c5d077e4e21698b3defaf9d906f3d" tags=[]
def hash_string(content):
    return hashlib.md5(content.encode()).hexdigest()


# %% [markdown]
# ## Finding all the threads
#
# We need to find all the live threads related to the invasion, as such I will limit my search to begin from the 1st of February 2022 (there were no threads previous to February) and end one day prior to running the search:

# %% gist="times.py" gist_id="8c08314f22f46eb3e2a1c4c4655ee6e6" tags=[]
begin_point = datetime(2022, 2, 1)
today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=12)

# %% [markdown]
# Next I define a list of *r/worldnews* moderators, since they are the only ones who are able to create live threads. The list of mods can be obtained using the API itself

# %% gist="all_world_news_mods.py" gist_id="7af8624f90f91cd3f63dee0dff220370" tags=[]
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

# %% [markdown]
# ### Iterating over each user
#
# The only way I found to find all the threads is to comb all submissions made by mods and then figure out which ones belong to what we care about here. The following fragment of code does that, fetching up to 200 submissions per user and storing them in a list:

# %% gist="iterate_over_users.py" gist_id="a96aa006e29efbaf3f3a82ad23e22ee3" tags=[]
subs = []
for username in mods:
    try:
        user = reddit.redditor(name=username)
        for post in user.submissions.new(limit=200):
            subs.append(post)
    except:
        pass

# %% [markdown]
# ### Iterating over all submisions
#
# Once we have all submissions made by mods, we can iterate over them in search of the ones we want. In this case, the ones we want start with either: *"/r/worldnews live thread"*, *"r/worldnews live thread"* or *"worldnews live thread"* and were made between the 1st of february and yesterday.
#
# Lastly, to extract all the properties, I am using the `getattr` function in combination with a list of properties.

# %% gist="iterate_submissions.py" gist_id="39020dc915a893577c6d2b8ae2277ba6" tags=[]
# fmt: off
properties = [
    "id", "created_utc", "name", "num_comments",
    "permalink", "score", "title", "upvote_ratio"
]
# fmt: on


def extract_submission_props(post):
    post_props = [post.author.name]
    post_props.extend([getattr(post, pr) for pr in properties])
    return post_props


submissions = []
for post in subs:
    title_low = post.title.lower()
    if (
        title_low.startswith("/r/worldnews live thread")
        or title_low.startswith("r/worldnews live thread")
        or title_low.startswith("worldnews live thread")
    ) and begin_point.timestamp() < post.created_utc < today.timestamp():
        submissions.append(extract_submission_props(post))

# %% [markdown]
# ### Converting to a DataFrame
#
# Once we have all the submissions in a list, we should convert it to a *pandas* DataFrame to make it easy to work with and to save. Then we can:
#
#  - Use `pd.to_datetime` to convert the unix timestamp to an actual date
#  - Hash the author's name with the previously declared `hash_string` function
#  
# After all the transformations, we can save the thread's data with an specified order in the columns, sorted by creation date and without index:

# %% gist="save_sorted.py" gist_id="0df2f2aae27fd2818e7cbd01322525ba" tags=[]
live_threads = pd.DataFrame(submissions, columns=["author"] + properties)

live_threads["created_at"] = pd.to_datetime(live_threads["created_utc"], unit="s", origin="unix")
live_threads['updated_on'] = pd.to_datetime(datetime.utcnow())
live_threads["author"] = live_threads["author"].apply(hash_string)

# %% [markdown]
# ### Load old information from disk and merge

# %%
old_information = pd.read_csv('data/threads.csv', parse_dates=['created_at', 'updated_on'])

# %%
merged_data = live_threads.set_index('id').combine_first(old_information.set_index('id')).reset_index()

# %%
ordered_columns = [
    "id", "name", "author", 
    "title", "created_utc", "created_at", 
    "num_comments", "score", 
    "upvote_ratio", "permalink",
    "updated_on"
]

merged_data['updated_on'] = merged_data['updated_on'].dt.round(freq='S')
merged_data[ordered_columns].sort_values("created_utc", ascending=True).to_csv("data/threads.csv", index=False)

# %% [markdown]
# ## Downloading ALL the comments for a ALL threads
#
# The next step is pretty straightforward. We need to iterate over the file we just created and use the PRAW package to download all the comments made to a submission.
#
# To begin, let's create a function that takes in a comment and a submission and returns a list of its properties, this function is a bit more complex given that comments differ from one another. Once again, I am using the getattr function to make our lives easy.

# %% gist="process_comments.py" gist_id="09ab4560c5d8407544b7cf3989a256c9" tags=[]
comment_props = [
    "id", "body", "edited",
    "created_utc", "link_id",
    "parent_id", "distinguished",
    "depth", "ups", "downs", "score",
    "total_awards_received", "gilded",
]


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


# %% [markdown]
# We are all set to iterate over the threads downloading all those we do not have yet. [There is a tutorial](https://praw.readthedocs.io/en/stable/tutorials/comments.html) on the PRAW website itself that details how to download comments to a thread - there is some customisation going on in terms of converting everything to a DataFrame, but the code itself is pretty much self-explanatory:

# %% gist="download_all.py" gist_id="dd12fb39c1435172dd1db61b1c8eba8d" tags=[]
for submission_id in live_threads["id"]:
    file_name = f"data/comments/comments__{submission_id}.csv"
    if os.path.exists(file_name):
        continue

    submission = reddit.submission(id=submission_id)
    submission.comments.replace_more(limit=None)

    comments = []
    for comment in submission.comments.list():
        comments.append(extract_comment(comment, submission_id))

    frame = pd.DataFrame(comments, columns=["author", "submission_id"] + comment_props + ["gildings"])
    frame.to_csv(file_name, index=False)

# %% [markdown]
# ## Automating everything through GitHub
#
# New threads are created every day, which means that if we want to keep our dataset updated, we must run this script every day as well. If you keep your code in GitHub, it sounds like the perfect candidate for automation with GitHub Actions.
#
# First off, we will need to save our environment variables with secrets (*CLIENT_ID*, *CLIENT_SECRET*, *PASSWORD*) as repository secrets. To do this, go to *Settings ➡ Secrets (Actions) ➡ New repository secret*:
#
# ![GitHub secrets](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/secrets-gh.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651614686032)
#
# Once all three secrets are available, create a *.yml* file in the *.github/workflows* folder with the following content:
#
# ```yaml
# name: Download dataset
#
# on:
#   schedule:
#   - cron: "0 10 * * *"
#
# jobs:
#   process:
#     runs-on: ubuntu-latest
#     steps:
#     - name: Checkout
#       uses: actions/checkout@v2
#     - name: Set up Python 3.8
#       uses: actions/setup-python@v2
#       with:
#         python-version: "3.8"
#     - name: Install dependencies
#       run: |
#         python -m pip install --upgrade pip
#         pip install pipenv
#         pipenv install --system --dev
#     - name: Download dataset from Reddit
#       env:
#         CLIENT_ID: ${{ secrets.CLIENT_ID }}
#         CLIENT_SECRET: ${{ secrets.CLIENT_SECRET }}
#         PASSWORD: ${{ secrets.PASSWORD }}
#       run: python download_threads.py
#     - name: Commit changes
#       run: |
#         git config --global user.email "antonio.feregrino@gmail.com"
#         git config --global user.name "Antonio Feregrino"
#         git add data/
#         git diff --quiet && git diff --staged --quiet || git commit -m "Updated: `date +'%Y-%m-%d %H:%M'`"
#         git push
# ```
#
# In short, every day at 10 AM:
#
#  1. It checkouts the code
#  2. Sets up Python 3.8
#  3. Installs the dependencies, in this case I was using pipenv to handle them locally - you could use something entirely different
#  4. Executes all the previous Python code that downloads the threads and their comments
#  5. Commits all the changes to the repository, saving our *csv* files.

# %% [markdown]
# ## Conclusion
#
# And that is it, now we have downloaded all the relevant threads, and we are ready to use them.
#
# In this post, we had a look into how to create a dataset using Reddit data, and in the next one, I'll show you how to use this dataset to create something interesting; I hope you learned something new or at least that you liked it. As always, [code is available here](https://github.com/fferegrino/r-worldnews-live-threads-ukraine/blob/main/download_threads.ipynb), and I am open to answering any question on [Twitter at @io_exception](https://twitter.com/io_exception).
