import os
import json
from datetime import datetime

import pytz
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from PIL import Image, ImageDraw, ImageFont

# Google Calendar scope
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_calendar_service():
    """
    Build an authenticated Google Calendar service
    using the GOOGLE_AUTH_JSON secret.
    """
    auth_json = os.environ["GOOGLE_AUTH_JSON"]
    info = json.loads(auth_json)

    # info should contain: type, client_id, client_secret, refresh_token
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    creds.refresh(Request())

    service = build("calendar", "v3", credentials=creds)
    return service


def get_upcoming_events(max_results=5, timezone="Europe/Dublin"):
    """
    Fetch the next few upcoming events from the configured calendar.
    """
    service = get_calendar_service()
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    now_iso = now.isoformat()

    events_result = service.events().list(
        calendarId=os.environ["GOOGLE_CALENDAR_ID"],
        timeMin=now_iso,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    items = events_result.get("items", [])
    events = []

    for ev in items:
        start = ev.get("start", {})
        dt_str = start.get("dateTime") or start.get("date")
        if not dt_str:
            continue

        # Normal timed event
        if "T" in dt_str:
            # Handle possible trailing Z
            if dt_str.endswith("Z"):
                dt_str = dt_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(dt_str).astimezone(tz)
        else:
            # All-day event (date only)
            dt_full = dt_str + "T00:00:00"
            dt = datetime.fromisoformat(dt_full).astimezone(tz)

        events.append(
            {
                "summary": ev.get("summary", "(No title)"),
                "datetime": dt,
            }
        )

    return events


# Canvas size for the dashboard image
WIDTH = 1200
HEIGHT = 1600  # portrait


def draw_dashboard():
    tz = pytz.timezone("Europe/Dublin")
    now = datetime.now(tz)

    # White background, 8-bit grayscale
    img = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # TEMP TEST: draw a big black bar at the very top
    draw.rectangle((0, 0, WIDTH, 200), fill=0)
    
    # Fonts – try custom, fall back to default
    try:
        font_big = ImageFont.truetype("Roboto-Bold.ttf", 96)
        font_med = ImageFont.truetype("Roboto-Regular.ttf", 48)
        font_small = ImageFont.truetype("Roboto-Regular.ttf", 36)
    except IOError:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # ----- TIME & DATE -----
    time_text = now.strftime("%H:%M")
    date_text = now.strftime("%A, %d %B %Y")

    # Measure time text
    time_bbox = draw.textbbox((0, 0), time_text, font=font_big)
    tw = time_bbox[2] - time_bbox[0]
    th = time_bbox[3] - time_bbox[1]

    # Measure date text
    date_bbox = draw.textbbox((0, 0), date_text, font=font_med)
    dw = date_bbox[2] - date_bbox[0]
    dh = date_bbox[3] - date_bbox[1]

    # Draw time centered near the top
    draw.text(((WIDTH - tw) // 2, 60), time_text, font=font_big, fill=0)

    # Draw date centered below time
    draw.text(((WIDTH - dw) // 2, 60 + th + 20), date_text, font=font_med, fill=0)

    # Divider line
    divider_y = 60 + th + 20 + dh + 40
    draw.line((80, divider_y, WIDTH - 80, divider_y), fill=0, width=3)

    # Start y-position for events
    y = divider_y + 40

    # Get events
    events = get_upcoming_events()

    if not events:
        draw.text((80, y), "No upcoming events", font=font_med, fill=0)
    else:
        # Section title
        draw.text((80, y), "Upcoming Events:", font=font_med, fill=0)
        y += 70

        for ev in events:
            dt = ev["datetime"]

            # e.g. "Sat 30 Nov"
            day_date = dt.strftime("%a %d %b")
