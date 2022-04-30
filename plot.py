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

# %% _uuid="8f2839f25d086af736a60e9eeb907d3b93b6e0e5" _cell_guid="b1076dfc-b9ad-4769-8c92-a6c4dae69d19"
from datetime import datetime, timedelta

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import pytz
from matplotlib.offsetbox import AnchoredText

# %% [markdown]
# ## Reading the thread files
#
# The files are divided into two main groups:
#
#  - The *threads.csv* file and,
#  - The *comments/comments_[THREAD_ID].csv* files
#
# The first group is a single file that contains some high-level information that acts as an aggregator for the rest of the files. In this file one can find the name, author, title, creation date, score and number of comments of each one of the *live threads* related to the invasion.

# %%
threads = pd.read_csv("data/threads.csv")
threads.head(2)

# %% [markdown]
# The second group contains as many files as threads exists in the *threads.csv* file, each one of them has a name like *comments/comments_[THREAD_ID].csv*.
#
# Each row in these *csv* files represents a comment made in the parent thread, the information available for each comment is: author, identifier, body, created date/time, whether it has been edited, score, and the parent comment (if it is a reply).
#
# One thing to note though, is that one can not simply use `pd.read_csv`, since sometimes the comments may contain line breaks that make it so that sometimes a single comment uses more than one row in the file. To succesfully read all these files, one needs to pass the `lineterminator` argument:

# %%
file = "data/comments/comments__st8lq0.csv"
comments = pd.read_csv(file, lineterminator="\n")
comments.head(2)

# %% [markdown]
# ## Plotting the frequency of comments
#
# Now that we learned what the files contain and how to read them, let's do something cool with them. Let's see how the interest over the thread has changed over time by counting the number of comments per hour.
#
# The overall process is as follows:
#
#  1. Read all the comment's dates
#  2. Bin the dates by 1 hour intervals
#  3. Plot!
#

# %% [markdown]
# ### 1. Read all the comment's dates
#
# We can keep using pandas, but being more clever about how to use it. Did you know that you can specify that you only want a subset of columns with the `usecols` argument?

# %%
created_dates = []
for thread_id in threads["id"]:
    comments_file = f"data/comments/comments__{thread_id}.csv"
    data = pd.read_csv(comments_file, lineterminator="\n", usecols=["created_utc"])
    created_dates.append(data["created_utc"].values)

created_dates = np.concatenate(created_dates)

# %% [markdown]
# This leaves us with the numpy array `created_dates` that contains $2,083,085$ numbers representing the creation date of each comment. The next step is binning these times into 1 hour intervals.

# %% [markdown]
# ### 2. Binning the creation times
#
# We will make use of a couple of helper functions to round date times up or down to the nearest step in the interval we define, (and one more to visualise timestamps).

# %%
# Helper date functions
INTERVAL = 3600  # 1 hour in seconds


def lower_bound(ts):
    return ts - (ts % INTERVAL)


def upper_bound(ts):
    return ts + (INTERVAL - ((ts) % INTERVAL) if (ts) % INTERVAL != 0 else 0)


def humanise(ts):
    return datetime.fromtimestamp(ts).strftime("%m/%d/%Y, %H:%M:%S")


# %% [markdown]
# Por ejemplo, toma la fecha *04/29/2022, 20:20:58* cuyo timestamp es `1651263658`:

# %%
example_ts = 1651263658
actual_date = humanise(1651263658)
upper = humanise(upper_bound(example_ts))
lower = humanise(lower_bound(example_ts))

print(f"{lower} is the lower bound of {actual_date} and its upper bound is {upper}")

# %% [markdown]
# Now that we have a way to calculate the upper and lower bounds of a specific date, we can move on to calculate the bin edges. This is easy once we know what are the minimum and maximum dates in our `created_dates`. In fact, getting the bin edges is a one-liner with NumPy:

# %%
bin_edges = np.arange(
    start=lower_bound(min(created_dates)),
    stop=upper_bound(max(created_dates)) + 1,
    step=INTERVAL,
    dtype=int,
)

# %% [markdown]
# Did I say one-liner? 😅 – well, I wanted it to be more understandable. The clever part comes when we add 1 to the upper bound, since `np.arange` is exclusive on the right-hand side, which means our valid upper bound would not be returned, however we circumvent this limitation by making it seem like our upper bound is not the last number. Lastly, the `step` argument has to be equal to 1 hour.
#
# Now that we have the bin edges, we are ready to calculate the histogram, this is yet another one liner thanks to NumPy's `np.histogram`!

# %%
values, bin_edges = np.histogram(created_dates, bins=bin_edges)

# %% [markdown]
# The values returned by this function are: the count for the specified interval and the intervals themselves. Keep in mind that there will always be one more item in the intervals than in the values!
#
# #### A window?
#
# Something that we can (and will do) is specify a determined window of time we want to show just in case we want to "zoom in" in our plot. For now, since the live threads started on the 14th of february 2022 we will take that as the beginning of our window and as for the end let's take the maximum date available + 1 day.

# %%
begining = datetime(2022, 2, 14)
end = datetime.fromtimestamp(bin_edges[-1]).replace(hour=0, minute=0) + timedelta(days=1)
window = (begining, end)

# %% [markdown]
# #### Converting into a Series
#
# To make our task easy, let's turn our values and edges into a pandas Series:

# %%
comments_histogram = pd.Series(data=values, index=pd.to_datetime(bin_edges[:-1], unit="s"))

# %% [markdown]
# #### Important events
#
# The plot on its own is informative, however, we can make it even more insightful with some important events about the invasion – this will help our users in assesing how a particular event in real life translates into a spike (or not) in the comments online.
#
# We need to create an array of tuples, where each tuple is the date of when the event happened and a short description of it:

# %%
major_events = [
    (datetime(2022, 2, 21, 19, 35), "Russia recognizes the\nindependence of\nbreakaway regions"),
    (datetime(2022, 2, 24, 3, 0), 'Putin announces the\n"special military operation"\nin Ukraine'),
    (datetime(2022, 3, 16, 16, 0), "Chernihiv breadline massacre\n and Mariupol theatre airstrike"),
    (datetime(2022, 4, 3, 17, 42), "Discovery of the\nBucha massacre"),
    (datetime(2022, 4, 13, 17, 42, 42), "Sinking of the Moskva"),
    (datetime(2022, 4, 28, 6, 49), "US Government approves\nLend-lease for Ukraine"),
]

# %% [markdown]
# ## 3. Plot!
#
# Finally! the part everyone was waiting for. Let's start by configuring a few options for *matplotlib*:

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


# %% [markdown]
# #### Basic plot
#
# Let's try an initial basic plot – created with a function so that we can reuse it later!:

# %%
def line_plot():
    fig = plt.figure(figsize=(25, 7), dpi=120)
    ax = fig.gca()
    ax.plot(comments_histogram.index, comments_histogram, color="#005BBB")

    return fig, ax


line_plot()


# %% [markdown]
# Not bad, but can be improved further!

# %% [markdown]
# #### Improving our ticks with locators and formatters
#
# The first thing I'd like to address is the fact that the visual references in terms of days and comment count look very sparse. Given that these are daily observations, I find it may be helpful to show this information on the graph.
#
# Turns out, *matplotlib* has some great utilities we can employ when working with dates within the `matplotlib.dates` package.
#
# The function `add_ticks` is divided in 4 blocks:
#
#  1. Set the minor ticks in the X-axis, using `DayLocator` and `DateFormatter` to set a minor marker every day
#  2. Set the major ticks in the X-axis, using a `MonthLocator` and `DateForamtter` to set a major marker every month
#  3. Set the formatting in the Y-axis, this one is a bit more convoluted since we need to "manually" set the ticks reading the original ones with `FixedLocator`, then use a `FuncFormatter` (and a lambda function) to specify the new formatting.
#  4. Set some additional styles to make the major ticks stand out from the minor ones.

# %%
def add_ticks(axes):

    minor_locator = mdates.DayLocator(interval=1)
    minor_formatter = mdates.DateFormatter("%d")
    axes.xaxis.set_minor_locator(minor_locator)
    axes.xaxis.set_minor_formatter(minor_formatter)

    major_locator = mdates.MonthLocator(interval=1)
    major_formatter = mdates.DateFormatter("%b")
    axes.xaxis.set_major_locator(major_locator)
    axes.xaxis.set_major_formatter(major_formatter)

    ticks_loc = axes.get_yticks()
    axes.yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
    axes.yaxis.set_major_formatter(mticker.FuncFormatter(lambda val, pos: f"{int(val / 1000)}K"))

    ax.tick_params(axis="x", which="major", length=20)
    ax.tick_params(which="major", labelsize=15)


fig, ax = line_plot()
add_ticks(ax)


# %% [markdown]
# Minor improvement, if you ask me!

# %% [markdown]
# #### Where are my labels??
#
# An unlabeled plot is a crappy plot, guided by this principle let's add the `add_legends` function divided in two blocks:
#
#  - It sets the limits of what the plot shows, here is were we use the `window` defined above, and also set the starting point in the Y-axis to 0.
#  - It sets all the labels and credit to the plot

# %%
def add_legends(axes, window):

    axes.set_ylim(ymin=0)
    axes.set_xlim(window)

    axes.set_title("r/WorldNews interest over the Russian Invasion of Ukraine")
    axes.set_xlabel("Day")
    axes.set_ylabel("Hourly comments")
    credit = f"u/fferegrino - comments from r/worldnews live threads"
    axes.add_artist(AnchoredText(credit, loc=1, frameon=True))


fig, ax = line_plot()
add_ticks(ax)
add_legends(ax, window)


# %% [markdown]
# Now people know what the plot is about! we are still not there, but we are getting close.

# %% [markdown]
# #### Major events
#
# Remember we created an array of tuples called `major_events`? it is its time to shine. The function `add_highlighted_events` takes the axis and the major events array and iterates over them marking their locations with the `.annotate` method.

# %%
def add_highlighted_events(axes, events):
    for date, title in events:
        event_utc_date = datetime.fromtimestamp(lower_bound(date.astimezone(pytz.utc).timestamp()))
        arrow_tip_location = comments_histogram[event_utc_date]
        xy = (event_utc_date, arrow_tip_location)
        xy_text = (event_utc_date - timedelta(days=0.6), arrow_tip_location + 4_000)
        arrow_props = dict(arrowstyle="-|>", facecolor="black")

        axes.annotate(
            title,
            xy=xy,
            xytext=xy_text,
            ha="right",
            arrowprops=arrow_props,
            fontsize=15,
        )


fig, ax = line_plot()
add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)


# %% [markdown]
# #### More colors
#
# In the `add_final_touches` you will find that I am adding a `grid` so that there is a subtle distinction across days. Set the background color of the plot to a light yellow and the overall background of our graphic to white.

# %%
def add_final_touches(figure, axes):

    axes.grid(axis="x", which="both", color="#FFEE99")
    axes.set_facecolor("#FFF7CC")
    figure.patch.set_facecolor("white")
    figure.tight_layout()


fig, ax = line_plot()
add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)
add_final_touches(fig, ax)

# %% [markdown]
# Then we can save the figure

# %%
fig.savefig("worldnews.png")

# %% [markdown]
# #### Appendix: Missing data on the 26 of february
#
# Do you see the drop between february 26 and 27? let's see what happened:
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
# Let's add another note to our plot so that people does not get confused:
#

# %%
fig, ax = line_plot()

add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)
add_final_touches(fig, ax)

ax.annotate(
    "Mod-deleted post",
    xy=(datetime(2022, 2, 26, 6, 45), 0),
    xytext=(datetime(2022, 2, 26, 6, 45) + timedelta(hours=24), 500),
    ha="left",
    arrowprops=dict(arrowstyle="-|>", facecolor="black", alpha=0.5),
    fontsize=15,
    alpha=0.5,
)

fig.savefig("worldnews.png")

# %% [markdown]
# ## Conclusion
#
# And there we are, we have a plot that is even more interesting to look at (and it was fun to make too).
#
# In the previous post we had a look into how to create a dataset using Reddit data and in this one we saw how to use this dataset to create something interesting, I hopw you learned something new or at least that you liked it. As always, code is available here and I am available to answer any question on [Twitter at @io_exception](https://twitter.com/io_exception).

# %%
