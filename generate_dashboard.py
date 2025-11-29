import os
import json
from datetime import datetime
import pytz


from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from PIL import Image, ImageDraw, ImageFont

# ----- Google Calendar bits -----

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_service():
    # GOOGLE_AUTH_JSON is a JSON string with type, client_id, client_secret, refresh_token
    auth_json = os.environ["GOOGLE_AUTH_JSON"]
    info = json.loads(auth_json)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    creds.refresh(Request())
    service = build("calendar", "v3", credentials=creds)
    return service


def get_upcoming_events(max_results=5, timezone="Europe/Dublin"):
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

        # dateTime (has a time) vs all-day (date only)
        if "T" in dt_str:
            # Normal event with time
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(tz)
        else:
            # All-day event
            dt = datetime.fromisoformat(dt_str + "T00:00:00").astimezone(tz)

        events.append({
            "summary": ev.get("summary", "(No title)"),
            "datetime": dt,
        })

    return events

# ----- Drawing the dashboard -----

WIDTH = 1200
HEIGHT = 1600  # portrait-ish

def draw_dashboard():
    tz = pytz.timezone("Europe/Dublin")
    now = datetime.now(tz)

    # White background, 8-bit grayscale
    img = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # Fonts – will fall back to default if custom ones aren't present
    try:
        font_big = ImageFont.truetype("Roboto-Bold.ttf", 96)
        font_med = ImageFont.truetype("Roboto-Regular.ttf", 48)
        font_small = ImageFont.truetype("Roboto-Regular.ttf", 36)
    except IOError:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Time and date
    time_text = now.strftime("%H:%M")
    date_text = now.strftime("%A %d %B %Y")

    # Measure time text
    time_bbox = draw.textbbox((0, 0), time_text, font=font_big)
    tw = time_bbox[2] - time_bbox[0]
    th = time_bbox[3] - time_bbox[1]

    # Measure date text
    date_bbox = draw.textbbox((0, 0), date_text, font=font_med)
    dw = date_bbox[2] - date_bbox[0]
    dh = date_bbox[3] - date_bbox[1]


    draw.text(((WIDTH - tw) // 2, 40), time_text, font=font_big, fill=0)
    draw.text(((WIDTH - dw) // 2, 40 + th + 10), date_text, font=font_med, fill=0)

    # Horizontal line
    y = 40 + th + 10 + dh + 30
    draw.line((80, y, WIDTH - 80, y), fill=0, width=2)
    y += 30

    # Get events
    events = get_upcoming_events()

    if not events:
        draw.text((80, y), "No upcoming events", font=font_med, fill=0)
    else:
        draw.text((80, y), "Upcoming events:", font=font_med, fill=0)
        y += 60
        for ev in events:
            dt = ev["datetime"]
            line1 = dt.strftime("%a %d %b  %H:%M")
            line2 = ev["summary"]

            draw.text((80, y), line1, font=font_small, fill=0)
            y += 40
            draw.text((120, y), line2, font=font_small, fill=0)
            y += 60

    img.save("dashboard.png")

if __name__ == "__main__":
    draw_dashboard()
