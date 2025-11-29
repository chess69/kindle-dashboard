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

      # ----- TIME & DATE -----
    time_text = now.strftime("%H:%M")
    date_text = now.strftime("%A, %d %B %Y")

    # Time text bounding box
    time_bbox = draw.textbbox((0, 0), time_text, font=font_big)
    tw = time_bbox[2] - time_bbox[0]
    th = time_bbox[3] - time_bbox[1]

    # Date text bounding box
    date_bbox = draw.textbbox((0, 0), date_text, font=font_med)
    dw = date_bbox[2] - date_bbox[0]
    dh = date_bbox[3] - date_bbox[1]

    # Draw time centered
    draw.text(((WIDTH - tw) // 2, 60), time_text, font=font_big, fill=0)

    # Draw date centered below time
    draw.text(((WIDTH - dw) // 2, 60 + th + 20), date_text, font=font_med, fill=0)

    # Divider line
    divider_y = 60 + th + 20 + dh + 40
    draw.line((80, divider_y, WIDTH - 80, divider_y), fill=0, width=3)

    # Start y-position for events
    y = divider_y + 40

    # ----- EVENT TITLE -----
    draw.text((80, y), "Upcoming Events:", font=font_med, fill=0)
    y += 70


    # Get events
    events = get_upcoming_events()

    if not events:
        draw.text((80, y), "No upcoming events", font=font_med, fill=0)
    else:
        draw.text((80, y), "Upcoming events:", font=font_med, fill=0)
        y += 60
              for ev in events:
        dt = ev["datetime"]

        # e.g. "Mon 11 Dec"
        day_date = dt.strftime("%a %d %b")

        # e.g. "14:30"
        time_str = dt.strftime("%H:%M")

        # Event title
        title = ev["summary"]

        # Height of each event bar
        bar_height = 90

        # Stop if we’re near the bottom of the screen
        if y + bar_height + 40 > HEIGHT:
            break

        # Draw full-width black bar with side margins
        left_margin = 40
        right_margin = 40
        draw.rectangle(
            (left_margin, y, WIDTH - right_margin, y + bar_height),
            fill=0
        )

        # Text positions inside the bar
        text_y = y + 20  # a bit down from the top of the bar

        # White text
        # Date on the left
        draw.text((left_margin + 20, text_y), day_date, font=font_small, fill=255)

        # Time next to date
        draw.text((left_margin + 220, text_y), time_str, font=font_small, fill=255)

        # Title a bit further right
        draw.text((left_margin + 380, text_y), title, font=font_small, fill=255)

        # Move y down for the next event
        y += bar_height + 25



    img.save("dashboard.png")

if __name__ == "__main__":
    draw_dashboard()
