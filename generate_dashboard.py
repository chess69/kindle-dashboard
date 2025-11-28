from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1072, 1448  # Paperwhite 3 native resolution (portrait)

def load_font(path, size):
    """Try to load a TTF font; fall back to default if not available."""
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_centered_text(draw, text, y, font, fill=0):
    """Draw a single line of text centered horizontally."""
    w, h = draw.textsize(text, font=font)
    x = (WIDTH - w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + h

def wrap_text(draw, text, font, max_width):
    """Very simple word-wrap for one paragraph."""
    words = text.split()
    lines = []
    current = []

    for word in words:
        test = " ".join(current + [word])
        w, _ = draw.textsize(test, font=font)
        if w <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines

def main():
    # Create white background
    img = Image.new("L", (WIDTH, HEIGHT), 255)  # L = greyscale
    draw = ImageDraw.Draw(img)

    # --- Time & date (Europe/Dublin) ---
    now = datetime.now(ZoneInfo("Europe/Dublin"))
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%a %d %b %Y")

    # --- Fonts ---
    # These paths exist on GitHub's ubuntu runners. If they fail, we fall back.
    title_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    time_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
    date_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    section_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    event_font = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)

    # --- Header: Title / Time / Date ---
    y = 60
    y = draw_centered_text(draw, "Bathroom Dashboard", y, title_font)
    y += 30
    y = draw_centered_text(draw, time_str, y, time_font)
    y += 10
    y = draw_centered_text(draw, date_str, y, date_font)
    y += 40

    # Draw a horizontal divider line
    draw.line((80, y, WIDTH - 80, y), fill=0, width=3)
    y += 30

    # --- Events (for now, hard-coded examples) ---
    # Later we can replace this list with real calendar events.
    events = [
        ("10:00", "Coffee with Rachel"),
        ("12:30", "Rugby · Edendale vs Ashbourne"),
        ("19:00", "Movie Night"),
    ]

    # Section heading
    y = draw_centered_text(draw, "Today", y, section_font)
    y += 10

    left_margin = 80
    right_margin = WIDTH - 80
    max_text_width = right_margin - left_margin

    for time_text, desc in events:
        # Time
        time_w, time_h = draw.textsize(time_text, font=event_font)
        draw.text((left_margin, y), time_text, font=event_font, fill=0)

        # Description to the right, wrapped if too long
        desc_lines = wrap_text(draw, desc, event_font, max_text_width - time_w - 20)
        line_y = y
        for i, line in enumerate(desc_lines):
            x = left_margin + time_w + 20
            draw.text((x, line_y), line, font=event_font, fill=0)
            _, lh = draw.textsize(line, font=event_font)
            line_y += lh + 4

        y = max(line_y, y + time_h) + 12  # gap before next event

    img.save("dashboard.png")

if __name__ == "__main__":
    main()
