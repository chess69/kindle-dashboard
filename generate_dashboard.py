from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1072, 1448  # Paperwhite 3 resolution

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def text_size(draw, text, font):
    # Use textbbox to get width/height
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top

def main():
    img = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # Time/date using proper timezone-aware UTC
    now = datetime.now(timezone.utc)
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%a %d %b %Y")

    # Fonts
    title_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    time_font  = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
    date_font  = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    section_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    event_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)

    y = 60

    # Title
    title_w, title_h = text_size(draw, "Bathroom Dashboard", title_font)
    draw.text(((WIDTH - title_w) // 2, y), "Bathroom Dashboard", font=title_font, fill=0)
    y += title_h + 30

    # Time
    time_w, time_h = text_size(draw, time_str, time_font)
    draw.text(((WIDTH - time_w) // 2, y), time_str, font=time_font, fill=0)
    y += time_h + 10

    # Date
    date_w, date_h = text_size(draw, date_str, date_font)
    draw.text(((WIDTH - date_w) // 2, y), date_str, font=date_font, fill=0)
    y += date_h + 40

    # Divider
    draw.line((80, y, WIDTH - 80, y), fill=0, width=3)
    y += 30

    # Section heading
    sec_w, sec_h = text_size(draw, "Today", section_font)
    draw.text(((WIDTH - sec_w) // 2, y), "Today", font=section_font, fill=0)
    y += sec_h + 20

    # Example events
    events = [
        ("10:00", "Coffee with Rachel"),
        ("12:30", "Rugby · Edendale vs Ashbourne"),
        ("19:00", "Movie Night"),
    ]

    left_margin = 80

    for time_text, desc in events:
        # Time
        t_w, t_h = text_size(draw, time_text, event_font)
        draw.text((left_margin, y), time_text, font=event_font, fill=0)

        # Description
        draw.text((left_margin + t_w + 20, y), desc, font=event_font, fill=0)

        # Move down
        y += max(t_h, 40) + 20

    img.save("dashboard.png")

if __name__ == "__main__":
    main()
