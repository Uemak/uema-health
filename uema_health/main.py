import os
from datetime import date, timedelta

import requests
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
import plotly.express as px


@st.cache
def request_health(item):
    url = f"https://api.ouraring.com/v2/usercollection/daily_{item}"

    end_date = date.today()
    days = 30
    if item == "activity":
        days = 31
    start_date = end_date - timedelta(days=days)
    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('OURA_TOKEN')}"
    }

    res = requests.request("GET", url, headers=headers, params=params)
    data = [{"day": d.get("day"), "score": d.get("score")}
            for d in res.json().get("data")]
    df = pd.DataFrame(data)
    df = df.set_index("day")
    return df


def get_health_df():
    readiness_df = request_health("readiness")
    readiness_df = readiness_df.rename(columns={"score": "readiness_score"})
    sleep_df = request_health("sleep")
    sleep_df = sleep_df.rename(columns={"score": "sleep_score"})
    activity_df = request_health("activity")
    activity_df = activity_df.rename(columns={"score": "activity_score"})
    health_df = readiness_df.join([sleep_df, activity_df], how="outer")
    health_df = health_df.fillna(0).sort_index()
    return health_df, readiness_df, sleep_df, activity_df


def main():
    today = date.today()
    str_today = today.strftime("%Y-%m-%d")
    yesterday = today - timedelta(days=1)
    str_yesterday = yesterday.strftime("%Y-%m-%d")

    health_df, readiness_df, sleep_df, activity_df = get_health_df()

    st.header("UEMA's Health Score")
    col1, col2, col3 = st.columns(3)
    today_readiness = int(readiness_df.at[str_today, "readiness_score"])
    yesterday_readiness = int(
        readiness_df.at[str_yesterday, "readiness_score"])
    col1.metric("Today Readiness Score",
                today_readiness, today_readiness - yesterday_readiness)
    today_sleep = int(sleep_df.at[str_today, "sleep_score"])
    yesterday_sleep = int(sleep_df.at[str_yesterday, "sleep_score"])
    col2.metric("Today Sleep Score",
                today_sleep, today_sleep - yesterday_sleep)
    today_activity = int(activity_df.at[str_today, "activity_score"])
    yesterday_activity = int(activity_df.at[str_yesterday, "activity_score"])
    col3.metric("Today Activity Score",
                today_activity, today_activity - yesterday_activity)
    st.subheader("Default line chart")
    st.line_chart(health_df)
    st.subheader("Line chart of Plotly")
    fig = px.line(health_df, markers=True)
    st.plotly_chart(fig)
    st.subheader("AgGrid library")
    AgGrid(health_df.reset_index())


main()
