from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import os
import datetime
import requests
from dateutil import parser
import pytz

MODEL = "gemini-2.5-pro"

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_CALENDAR_REFRESH_TOKEN")
TOKEN_URI = os.getenv("GOOGLE_CALENDAR_TOKEN_URI")
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

def get_access_token():
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    response = requests.post(TOKEN_URI, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def convert_to_iso_datetime(time_str: str) -> str:
    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.datetime.now(ist).date()
    parsed_time = parser.parse(time_str)
    combined = datetime.datetime.combine(today, parsed_time.time())
    localized = ist.localize(combined)
    return localized.isoformat()

def add_calendar_event(params: dict) -> str:
    try:
        event_name = params["event_name"]
        start_time = params["start_time"]
        end_time = params["end_time"]
    except KeyError as e:
        return f"Missing required key: {str(e)}"

    access_token = get_access_token()
    event = {
        "summary": event_name,
        "start": {
            "dateTime": convert_to_iso_datetime(start_time),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": convert_to_iso_datetime(end_time),
            "timeZone": "Asia/Kolkata",
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events",
        headers=headers,
        json=event,
    )

    if response.status_code in [200, 201]:
        return f"Event '{event_name}' added from {start_time} to {end_time}."
    else:
        return f"Failed to add event: {response.text}"

# Delete event by summary match
def delete_calendar_event(params: dict) -> str:
    try:
        event_name = params["event_name"]
    except KeyError:
        return "Missing required key: event_name"

    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Search events
    response = requests.get(
        f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events",
        headers=headers,
        params={"q": event_name}
    )

    events = response.json().get("items", [])
    for event in events:
        if event.get("summary", "").lower() == event_name.lower():
            event_id = event["id"]
            delete_response = requests.delete(
                f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events/{event_id}",
                headers=headers,
            )
            if delete_response.status_code == 204:
                return f"🗑️ Event '{event_name}' deleted successfully."
            else:
                return f"❌ Failed to delete event: {delete_response.text}"

    return f"⚠️ No matching event found to delete with name '{event_name}'."

def update_calendar_event(params: dict) -> str:
    try:
        event_name = params["event_name"]
        new_start_time = params["start_time"]
        new_end_time = params["end_time"]
    except KeyError as e:
        return f"Missing required key: {str(e)}"

    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


    response = requests.get(
        f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events",
        headers=headers,
        params={"q": event_name}
    )

    events = response.json().get("items", [])
    for event in events:
        if event.get("summary", "").lower() == event_name.lower():
            event_id = event["id"]
            update_payload = {
                "start": {
                    "dateTime": convert_to_iso_datetime(new_start_time),
                    "timeZone": "Asia/Kolkata",
                },
                "end": {
                    "dateTime": convert_to_iso_datetime(new_end_time),
                    "timeZone": "Asia/Kolkata",
                },
            }

            update_response = requests.patch(
                f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events/{event_id}",
                headers=headers,
                json=update_payload,
            )

            if update_response.status_code == 200:
                return f"🔄 Event '{event_name}' updated successfully."
            else:
                return f"Failed to update event: {update_response.text}"

    return f"No matching event found to update with name '{event_name}'."

add_calendar_event_tool = FunctionTool(add_calendar_event)
delete_calendar_event_tool = FunctionTool(delete_calendar_event)
update_calendar_event_tool = FunctionTool(update_calendar_event)

time_table_updator_agent = Agent(
    name="time_table_updator_agent",
    model=MODEL,
    description="Updates, deletes, or modifies calendar events",
    tools=[add_calendar_event_tool, delete_calendar_event_tool, update_calendar_event_tool],
    instruction="You are a helpful assistant that manages Google Calendar events based on user input."
)
