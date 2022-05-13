from datetime import datetime, timedelta

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import pytz
import streamlit as st

from plot import (add_final_touches, add_highlighted_events, add_legends,
                  add_ticks, line_plot)

st.title("r/WorldNews Live Thread: Russian Invasion of Ukraine")


@st.cache
def load_times():
    threads = pd.read_csv("data/threads.csv")
    created_dates = []
    for thread_id in threads["id"]:
        comments_file = f"data/comments/comments__{thread_id}.csv"
        data = pd.read_csv(comments_file, lineterminator="\n", usecols=["created_utc"])
        created_dates.append(data["created_utc"].values)

    return np.concatenate(created_dates)


created_dates = load_times()


def lower_bound(ts):
    return ts - (ts % INTERVAL)


def upper_bound(ts):
    return ts + (INTERVAL - ((ts) % INTERVAL) if (ts) % INTERVAL != 0 else 0)


col1, col2, col3 = st.columns(3)

options = [
    ("15 minutes", 15),
    ("30 minutes", 30),
    ("1 hour", 60),
    ("3 hours", 180),
    ("6 hours", 60 * 6),
]

with col1:
    selected_time = st.selectbox("Bin size", [opt[0] for opt in options], index=2)

[selected] = [opt[1] for opt in options if opt[0] == selected_time]
INTERVAL = selected * 60

bin_edges = np.arange(
    start=lower_bound(min(created_dates)),
    stop=upper_bound(max(created_dates)) + 1,
    step=INTERVAL,
    dtype=int,
)

values, bin_edges = np.histogram(created_dates, bins=bin_edges)

min_date = datetime.fromtimestamp(bin_edges.min())
max_date = datetime.fromtimestamp(bin_edges.max())


with col2:
    beginning = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    beginning = datetime(year=beginning.year, month=beginning.month, day=beginning.day)
with col3:
    end = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)
    end = datetime(year=end.year, month=end.month, day=end.day)

window = (beginning, end)

comments_histogram = pd.Series(data=values, index=pd.to_datetime(bin_edges[:-1], unit="s"))
comments_histogram = comments_histogram[(comments_histogram.index >= beginning) & (comments_histogram.index <= end)]


major_events = [
    (datetime(2022, 2, 21, 19, 35), "Russia recognizes the\nindependence of\nbreakaway regions"),
    (datetime(2022, 2, 24, 3, 0), 'Putin announces the\n"special military operation"\nin Ukraine'),
    (datetime(2022, 3, 16, 16, 0), "Chernihiv breadline massacre\n and Mariupol theatre airstrike"),
    (datetime(2022, 4, 3, 17, 42), "Discovery of the\nBucha massacre"),
    (datetime(2022, 4, 13, 17, 42, 42), "Sinking of the Moskva"),
    (datetime(2022, 4, 28, 6, 49), "US Government approves\nLend-lease for Ukraine"),
]

params = {
    "axes.titlesize": 20,
    "axes.labelsize": 15,
    "lines.linewidth": 1.5,
    "lines.markersize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 12,
}

mpl.rcParams.update(params)


fig, ax = line_plot(comments_histogram)

add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)
add_final_touches(fig, ax)


st.pyplot(fig=fig)
