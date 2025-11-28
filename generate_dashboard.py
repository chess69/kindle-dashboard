from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1072, 1448  # Paperwhite 3 native resolution (portrait)

def load_font(path, size):
    """Try to load a TTF font; fall back to default if not available."""
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def main():
    # Create white background
    img = Image.new("L", (WIDTH, HEIGHT), 255)  # L = greyscale
    draw = ImageDraw.Draw(img)

    # Time & date (UTC – fine for now)
    now = datetime.utcnow()
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%a %d %b %Y")

    # Fonts
    title_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    time_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
    date_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    section_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    event_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)

    # Header: title, time, date
    y = 60
    title_w, title_h = draw.textsize("Bathroom Dashboard", font=title_font)
    draw.text(((WIDTH - title_w) // 2, y), "Bathroom Dashboard", font=title_font, fill=0)
    y += title_h + 30

    time_w, time_h = draw.textsize(time_str, font=time_font)
    draw.text(((WIDTH - time_w) // 2, y), time_str, font=time_font, fill=0)
    y += time_h + 10

    date_w, date_h = draw.textsize(date_str, font=date_font)
    draw.text(((WIDTH - date_w) // 2, y), date_str, font=date_font, fill=0)
    y += date_h + 40

    # Divider line
    draw.line((80, y, WIDTH - 80, y), fill=0, width=3)
    y += 30

    # Section title
    section_text = "Today"
    sec_w, sec_h = draw.textsize(section_text, font=section_font)
    draw.text(((WIDTH - sec_w) // 2, y), section_text, font=section_font, fill=0)
    y += sec_h + 20

    # Hard-coded events
    events = [
        ("10:00", "Coffee with Rachel"),
        ("12:30", "Rugby · Edendale vs Ashbourne"),
        ("19:00", "Movie Night"),
    ]

    left_margin = 80
    max_text_width = WIDTH - 2 * left_margin

    for time_text, desc in events:
        # Draw time
        time_w, time_h = draw.textsize(time_text, font=event_font)
        draw.text((left_margin, y), time_text, font=event_font, fill=0)

        # Draw description to the right (no fancy wrapping yet)
        desc_x = left_margin + time_w + 20
        desc_y = y
        draw.text((desc_x, desc_y), desc, font=event_font, fill=0)

        # Move down for next event
        y += max(time_h, date_h) + 20

    img.save("dashboard.png")

if __name__ == "__main__":
    main()
