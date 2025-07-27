from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import os
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    data = {
        "client_id": os.getenv("GOOGLE_CALENDAR_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_CALENDAR_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }
    response = requests.post(os.getenv("GOOGLE_CALENDAR_TOKEN_URI"), data=data)
    return response.json().get("access_token")


def get_today_events() -> list:
    access_token = get_access_token()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    end = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + "Z"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"https://www.googleapis.com/calendar/v3/calendars/{os.getenv('CALENDAR_ID')}/events?timeMin={now}&timeMax={end}",
        headers=headers,
    )
    return response.json().get("items", [])


get_today_events_tool = FunctionTool(func=get_today_events)

time_table_summarization_agent = Agent(
    name="time_table_summarization_agent",
    model="gemini-2.5-pro",
    description="Summarizes today's calendar schedule for a student.",
    instruction=(
        "Summarize today's classes using the Google Calendar events."
        "Output should be concise and friendly for a student."
    ),
    tools=[get_today_events_tool],
)


