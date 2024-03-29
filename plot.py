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

# %% gist="imports.py" gist_id="dc5aeff41f94f2050bf02ddafac46fbf" tags=[]
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
# The first group is a single file that contains some high-level information that acts as an aggregator for the rest of the files. In this file, one can find the name, author, title, creation date, score and number of comments of each one of the *live threads* related to the invasion.

# %% dataframe="threads.jpg" gist="read_threads_file.py" gist_id="51ea5205241e4596331f03fccb1da135" tags=[]
threads = pd.read_csv("data/threads.csv")
threads.head(2)

# %% [markdown]
# The second group contains as many files as threads exist in the *threads.csv* file; each has a name like *comments/comments_[THREAD_ID].csv*.
#
# Each row in these *csv* files represents a comment made in the parent thread. The information available for each comment is: author, identifier, body, created date/time, whether it has been edited, score, and the parent comment (if it is a reply).
#
# One thing to note is that one can not simply use `pd.read_csv`, since sometimes the comments may contain line breaks that make it so that sometimes a single comment uses more than one row in the file. To successfully read all these files, one needs to pass the `lineterminator` argument:

# %% dataframe="sample-comments.jpg" gist="read_comments_file.py" gist_id="f88ab8c9ab2e62d43a7cfddebbcec3ee" tags=[]
file = "data/comments/comments__st8lq0.csv"
comments = pd.read_csv(file, lineterminator="\n")
comments.head(2)

# %% [markdown]
# ## Plotting the frequency of comments
#
# Now that we learned what the files contain and how to read them, let's do something cool with them. Let's see how the interest in the thread has changed over time by counting the number of comments per hour.
#
# The overall process is as follows:
#
#  1. Read all the comment's dates
#  2. Bin the dates by 1-hour intervals
#  3. Plot!
#

# %% [markdown]
# ### 1. Read all the comment's dates
#
# We can keep using *pandas* but being more clever about using it. Did you know that you can specify that you only want a subset of columns with the `usecols` argument?

# %% gist="read_all_dates.py" gist_id="25ed1ea8d63a71dd5fe9adc3c8c9cdf4" tags=[]
created_dates = []
for thread_id in threads["id"]:
    comments_file = f"data/comments/comments__{thread_id}.csv"
    data = pd.read_csv(comments_file, lineterminator="\n", usecols=["created_utc"])
    created_dates.append(data["created_utc"].values)

created_dates = np.concatenate(created_dates)

# %% [markdown]
# This leaves us with the NumPy array `created_dates` containing $2,083,085$ numbers representing the creation date of each comment. The next step is binning these times into 1 hour intervals.

# %% [markdown]
# ### 2. Binning the creation times
#
# We will use a couple of helper functions to round date times up or down to the nearest step in the interval we define (and one more to visualise timestamps).

# %% gist="additional_functions.py" gist_id="2c94108f5fa630ba81760e08ea82e12f" tags=[]
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

# %% gist="functions_example.py" gist_id="75d00e3f11cc45bcfb290964a10d7bc4" keep_output=true tags=[]
example_ts = 1651263658
actual_date = humanise(1651263658)
upper = humanise(upper_bound(example_ts))
lower = humanise(lower_bound(example_ts))

print(f"{lower} is the lower bound of {actual_date} and its upper bound is {upper}")

# %% [markdown]
# Now that we have a way to calculate the upper and lower bounds of a specific date, we can move on to calculate the bin edges. This is easy once we know the minimum and maximum dates in our `created_dates`. In fact, getting the bin edges is a one-liner with NumPy:

# %% gist="bin_edges.py" gist_id="39e9934307de2526820e3e710f579fe9" tags=[]
bin_edges = np.arange(
    start=lower_bound(min(created_dates)),
    stop=upper_bound(max(created_dates)) + 1,
    step=INTERVAL,
    dtype=int,
)

# %% [markdown]
# Did I say one-liner? 😅 – well, I wanted it to be more understandable. The clever part comes when we add 1 to the upper bound; since `np.arange` is exclusive on the right-hand side, which means our valid upper bound would not be returned, however, we circumvent this limitation by making it seem like our upper bound is not the last number. Lastly, the `step` argument has to be equal to 1 hour.
#
# Now that we have the bin edges, we are ready to calculate the histogram. This is yet another one-liner, thanks to NumPy's `np.histogram`!

# %% gist="generate_histogram.py" gist_id="4bd4858f58b389cd59fa1bc8fbdaed95" tags=[]
values, bin_edges = np.histogram(created_dates, bins=bin_edges)

# %% [markdown]
# The values returned by this function are the count for the specified interval and the intervals themselves. Keep in mind that there will always be one more item in the intervals than in the values!
#
# #### A window?
#
# For further customisation purposes we can specify a determined window of time we want to show just in case we want to "zoom in" on our plot. For now, since the live threads started on the 14th of february 2022, we will take that as the beginning of our window and as for the end, let's take the maximum date available + 1 day.

# %% gist="create_window.py" gist_id="1b1f2ed0b97db1396cc7a9cbb36ac825" tags=[]
begining = datetime(2022, 2, 14)
end = datetime.fromtimestamp(bin_edges[-1]).replace(hour=0, minute=0) + timedelta(days=1)
window = (begining, end)

# %% [markdown]
# #### Converting into a Series
#
# To make our task easy, let's turn our values and edges into a pandas Series:

# %% gist="turn_histogram_into_series.py" gist_id="8218c8abbfaa51299859a5fc4ca44f5c" tags=[]
comments_histogram = pd.Series(data=values, index=pd.to_datetime(bin_edges[:-1], unit="s"))
comments_histogram = comments_histogram[(comments_histogram.index >= begining) & (comments_histogram.index <= end)]

# %% [markdown]
# #### Important events
#
# The plot is informative; however, we can make it even more insightful with some important events about the invasion – this will help our users assess how a particular event in real life translates into a spike (or not) in the comments online.
#
# We need to create an array of tuples, where each tuple is the date of when the event happened and a short description of it:

# %% gist="important_events.py" gist_id="de096aa3fc5666b74061ad5bfa35691b" tags=[]
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

# %% gist="matplotlib_config.py" gist_id="ec81eceb19a657d88dbc6ea924a910e7" tags=[]
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

# %% description="First version" gist="first_plot.py" gist_id="310579e01a296ade9477666d2e4fd663" image="first-version.png" tags=[]
def line_plot(histogram):
    fig = plt.figure(figsize=(25, 7), dpi=120)
    ax = fig.gca()
    ax.plot(histogram.index, histogram, color="#005BBB")
    ax.fill_between(histogram.index, histogram, color="#cce5ff", alpha=0.5)
    return fig, ax


line_plot(comments_histogram)


# %% [markdown]
# ![First version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/first-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651354449381)
#
# Not bad, but it can be improved further!

# %% [markdown]
# #### Improving our ticks with locators and formatters
#
# The first thing I'd like to address is the fact that the visual references in terms of days and comment count look very sparse. Given that these are daily observations, I find it may be helpful to show this information on the graph.
#
# It turns out, that *matplotlib* has some great utilities we can employ when working with dates within the `matplotlib.dates` package.
#
# The function `add_ticks` is divided into 4 blocks:
#
#  1. Set the minor ticks in the X-axis, using `DayLocator` and `DateFormatter` to set a minor marker every day
#  2. Set the major ticks in the X-axis, using a `MonthLocator` and `DateForamtter` to set a major marker every month
#  3. Set the formatting in the Y-axis; this one is a bit more convoluted since we need to "manually" set the ticks reading the original ones with `FixedLocator`, then use a `FuncFormatter` (and a lambda function) to specify the new formatting.
#  4. Set some additional styles to make the major ticks stand out from the minor ones.

# %% description="Second version" gist="second_plot.py" gist_id="b4323d8f665845807bff8545acd5f7fa" image="second-version.png" tags=[]
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


fig, ax = line_plot(comments_histogram)
add_ticks(ax)


# %% [markdown]
# ![Second version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/second-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981035)
#
# Minor improvement, if you ask me!

# %% [markdown]
# #### Where are my labels??
#
# An unlabeled plot is a crappy plot; guided by this principle, let's add the `add_legends` function divided into two blocks:
#
#  - It sets the limits of what the plot shows; here is where we use the `window` defined above and set the Y-axis's starting point to 0.
#  - It sets all the labels and credit to the plot.

# %% description="Third version" gist="third_plot.py" gist_id="b651c9b8b73ae045d4e04c9921655ccd" image="third-version.png" tags=[]
def add_legends(axes, window):

    axes.set_ylim(ymin=0)
    axes.set_xlim(window)

    axes.set_title("r/WorldNews interest over the Russian Invasion of Ukraine")
    axes.set_xlabel("Day")
    axes.set_ylabel("Hourly comments")
    credit = f"u/fferegrino - comments from r/worldnews live threads"
    axes.add_artist(AnchoredText(credit, loc=1, frameon=True))


fig, ax = line_plot(comments_histogram)
add_ticks(ax)
add_legends(ax, window)


# %% [markdown]
# ![Third version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/third-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981190)
#
# Now people know what the plot is about! we are still not there, but we are getting close.

# %% [markdown]
# #### Major events
#
# Remember we created an array of tuples called `major_events`? Tt is its time to shine. The function `add_highlighted_events` takes the axis and the major events array and iterates over them, marking their locations with the `.annotate` method.

# %% description="Fourth version" gist="fourth_plot.py" gist_id="d8c876a949da27cb627fbfe3a84fd4e8" image="fourth-version.png" tags=[]
def add_highlighted_events(axes, events):
    for date, title in events:
        event_utc_date = datetime.fromtimestamp(lower_bound(date.astimezone(pytz.utc).timestamp()))
        try:
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
        except KeyError:
            # The event is not covered within our window, that is the reason
            # behind this failure
            pass


fig, ax = line_plot(comments_histogram)
add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)


# %% [markdown]
# ![Fourth version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/fourth-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981161)

# %% [markdown]
# #### More colours
#
# In the `add_final_touches` function, you will find that I am adding a `grid` so that there is a subtle distinction across days. Set the background colour of the plot to a light yellow and the overall background of our graphic to white – then we can save the figure.

# %% description="Fifth version" gist="fifth_plot.py" gist_id="50da8cf3614eb864e8fc17b17c2e835c" image="fifth-version.png" tags=[]
def add_final_touches(figure, axes):

    axes.grid(axis="x", which="both", color="#FFEE99")
    axes.set_facecolor("#FFF7CC")
    figure.patch.set_facecolor("white")
    figure.tight_layout()


fig, ax = line_plot(comments_histogram)
add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)
add_final_touches(fig, ax)

# %% [markdown]
# ![Fifth version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/fifth-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981153)
#
# Then we can save the figure:

# %%
fig.savefig("worldnews.png")

# %% [markdown]
# #### Appendix: Missing data on the 26 of February
#
# Do you see the drop between February 26 and 27? let's see what happened:
#
# The latest comment on the [Day 3, Part 6 (Thread #35)](https://reddit.com/r/worldnews/comments/t1oqrc/rworldnews_live_thread_russian_invasion_of/) thread was posted at 06:54:34 AM, while the earliest comment on the replacement thread, [Day 3, Part 7 (Thread #36)](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/?sort=old) is 07:57:52 AM.
#
# This makes it seem like there were absolutely no comments for around one hour. However, upon further investigation, it appears that there was an error on the mods team where one of them created a thread with the wrong name, left it around for around 1 hour and then deleted it, as evidenced by these comments:
#
#  > What happened to the last thread? – [*permalink*](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/hyhpo2p/)
#  >> Had the dates wrong, said it was day 4 thread 1.
#
# And
#
#  > New thread already? – [*permalink*](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/hyhpn5g/?utm_source=reddit&utm_medium=web2x&context=3)
#  >> Wrong day on the last one
#
# Let's add another note to our plot so that people do not get confused:
#

# %% description="Sixth version" gist="sixth_plot.py" gist_id="2852d044709584c6fba2956dff22c53c" image="sixth-version.png" tags=[]
fig, ax = line_plot(comments_histogram)

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
# ![Sixth and final version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/sixth-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981204)

# %% [markdown]
# ## Conclusion
#
# And there we are; we have a plot that is even more interesting to look at (and it was fun to make too).
#
# In a previous post, we had a look into how to create a dataset using Reddit data, and in this one we saw how to use this dataset to create something you can present. I hope you learned something new or at least that you liked it. As always, [code is available here](https://github.com/fferegrino/r-worldnews-live-threads-ukraine/blob/main/plot.ipynb), and I am open to answering any question on [Twitter at @io_exception](https://twitter.com/io_exception).

# %%
