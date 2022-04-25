# -*- coding: utf-8 -*-
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
from datetime import datetime, timedelta
from glob import glob

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
from matplotlib.offsetbox import AnchoredText

# %%
begining = datetime(2022, 2, 14)
today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

# %%
timings = []


def read_validate_thread(file):
    data = pd.read_csv(file, lineterminator="\n", usecols=["created_utc"], dtype={"gildings": object})
    if data["created_utc"].isna().sum():
        raise ValueError("There should be no null `created_utc`")
    if data["created_utc"].dtype != np.float64:
        raise ValueError("`created_utc` should always be a float")
    return data


for file in glob("data/comments/*.csv"):
    try:
        data = read_validate_thread(file)
        timings.extend(data["created_utc"].values.tolist())
    except:
        print(f"Error reading {file}")

timings = np.array(timings)

# %%
# Helper date functions
bucket_size = 3600


def lower_bound(ts):
    return ts - (ts % bucket_size)


def upper_bound(ts):
    return ts + (bucket_size - ((ts) % bucket_size) if (ts) % bucket_size != 0 else 0)


def pts(ts):
    print(datetime.fromtimestamp(ts).strftime("%m/%d/%Y, %H:%M:%S"))


# %%
def get_bin_edges(mn, mx):
    selected_bins = list(range(int(lower_bound(mn)), int(upper_bound(mx)), bucket_size)) + [int(upper_bound(mx))]
    return np.array(selected_bins)


def hist(times):
    min_time, max_time = lower_bound(min(times)), upper_bound(max(times))
    return np.histogram(times, get_bin_edges(min_time, max_time))


# %%
moscow = pytz.timezone("Europe/Moscow")
kyiv = pytz.timezone("Europe/Kiev")

major_events = [
    (
        moscow.localize(datetime(2022, 2, 21, 22, 35)),
        "Russia recognizes the\nindependence of\nbreakaway regions",
    ),
    (
        moscow.localize(datetime(2022, 2, 24, 6, 0)),
        'Putin announces the\n"special military operation"\nin Ukraine',
    ),
    (
        kyiv.localize(datetime(2022, 3, 16, 18, 0)),
        "Chernihiv breadline massacre\n and Mariupol theatre airstrike",
    ),
    (kyiv.localize(datetime(2022, 4, 3, 20, 42)), "Discovery of the\nBucha massacre"),
    (kyiv.localize(datetime(2022, 4, 13, 20, 42)), "Sinking of the Moskva"),
]

# %%
values, edges = hist(timings)
comments_histogram = pd.Series(data=values, index=pd.to_datetime(edges[:-1], unit="s"))

# %%
window = (begining, today)

# %%
comments_histogram = comments_histogram[(comments_histogram.index > window[0]) & (comments_histogram.index < window[1])]

# %%
params = {
    "axes.titlesize": 20,
    "axes.labelsize": 15,
    "lines.linewidth": 1.5,
    "lines.markersize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 12,
}

mpl.rcParams.update(params)

# %%
fig = plt.figure(figsize=(25, 7), dpi=120)

ax = fig.gca()

ax.plot(comments_histogram.index, comments_histogram, color="#005BBB")


def add_ticks(figure, axes):
    minor_locator = mdates.DayLocator(interval=1)
    minor_formatter = mdates.DateFormatter("%d")
    major_locator = mdates.MonthLocator(interval=1)
    major_formatter = mdates.DateFormatter("%b")
    axes.xaxis.set_minor_locator(minor_locator)
    axes.xaxis.set_minor_formatter(minor_formatter)
    axes.xaxis.set_major_locator(major_locator)
    axes.xaxis.set_major_formatter(major_formatter)

    ax.tick_params(axis="x", labelrotation=0, which="major", length=20)
    ax.tick_params(which="major", labelsize=15)

    figure.autofmt_xdate(rotation=0, ha="center")

    ylabels = [f"{int(y_val)}K" for y_val in axes.get_yticks() / 1000]
    axes.set_yticklabels(ylabels)


def add_legends(axes):
    axes.set_xlim(window)
    axes.set_title("r/WorldNews interest over the Russian Invasion of Ukraine")
    axes.set_xlabel("Day")
    axes.set_ylabel("Hourly comments")
    tag = f"u/fferegrino - comments from r/worldnews live threads"

    text = AnchoredText(tag, loc=1, frameon=True)
    axes.add_artist(text)


def add_highlighted_events(axes, events):
    for date, title in events:
        utc_date = datetime.fromtimestamp(lower_bound(date.astimezone(pytz.utc).timestamp()))
        try:
            arrow_tip_location = comments_histogram[utc_date]
            xy = (utc_date, arrow_tip_location)
            xy_text = (utc_date - timedelta(days=0.7), arrow_tip_location + 3_000)

            axes.annotate(
                title,
                xy=xy,
                xytext=xy_text,
                ha="right",
                arrowprops=dict(arrowstyle="-|>", facecolor="black"),
                fontsize=12,
            )
        except:
            pass


# Add clarification on the data drop on 26
ax.annotate(
    "Mod-deleted post",
    xy=(datetime(2022, 2, 26, 6, 45), 0),
    xytext=(datetime(2022, 2, 26, 6, 45) + timedelta(hours=24), 0),
    ha="left",
    arrowprops=dict(arrowstyle="-|>", facecolor="black", alpha=0.5),
    fontsize=12,
    alpha=0.5,
)

ax.grid(axis="x", which="both", color="#FFEE99")

add_highlighted_events(ax, major_events)

add_ticks(fig, ax)

add_legends(ax)

ax.set_facecolor("#FFF7CC")
fig.tight_layout()
fig.patch.set_facecolor("white")

fig.savefig("worldnews.png")

# %% [markdown]
# ## Missing data on the 26 of february
#
# The latest comment on the [Day 3, Part 6 (Thread #35)](https://reddit.com/r/worldnews/comments/t1oqrc/rworldnews_live_thread_russian_invasion_of/) thread was posted at 06:54:34 AM, while the earliest comment on the replacement thread, [Day 3, Part 7 (Thread #36)](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/?sort=old) is 07:57:52 AM.
#
# This makes it seem like there were absolutely no comments for around one hour. However, upon further investigation, it seems that there was an error on the mods team where one of them created a thread with the wrong name, left it around for around 1 hour and then deleted it, as evidenced by these comments:
#
#  > What happened to the last thread? – [*permalink*](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/hyhpo2p/)
#  >> Had the dates wrong, said it was day 4 thread 1.
#
# And
#
#  > New thread already? – [*permalink*](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/hyhpn5g/?utm_source=reddit&utm_medium=web2x&context=3)
#  >> Wrong day on the last one
#

# %%
