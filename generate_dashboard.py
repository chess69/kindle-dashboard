from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1072, 1448  # Paperwhite 3 native resolution (portrait)

def main():
    # Create white background
    img = Image.new("L", (WIDTH, HEIGHT), 255)  # L = greyscale

    draw = ImageDraw.Draw(img)

    now = datetime.utcnow()  # later we can add your timezone

    # BIG CLOCK
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%a %d %b %Y")

    # Draw content
    draw.text((50, 100), "Bathroom Dashboard", fill=0)
    draw.text((50, 200), time_str, fill=0)
    draw.text((50, 260), date_str, fill=0)

    img.save("dashboard.png")

if __name__ == "__main__":
    main()
