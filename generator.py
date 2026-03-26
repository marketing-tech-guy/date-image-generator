import os
import shutil
import zipfile
from PIL import Image, ImageDraw, ImageFont

# --------------------------------
# CONFIG
# --------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "Template.png")
FONT_PATH = os.path.join(BASE_DIR, "fonts", "Poppins-Bold.ttf")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

TEXT_COLOR = "#000000"

# Bounding boxes from Figma (x, y, width, height)
DAY_BOX = (941, 668, 435, 295)
ORDINAL_BOX = (1324, 538, 211, 155)   # reference only
MONTH_BOX = (322, 935, 1673, 343)

# EXACT font sizes from Figma
DAY_FONT_SIZE = 340
ORDINAL_FONT_SIZE = 150
MONTH_FONT_SIZE = 280

# ---- IMPROVED vertical corrections ----
DAY_Y_OFFSET = -65
ORDINAL_Y_OFFSET = -65
MONTH_Y_OFFSET = -50

# Additional gap between day and month
DAY_MONTH_GAP = 15


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def center_text(draw, text, font, box):
    x, y, w, h = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x + (w - tw) // 2
    ty = y + (h - th) // 2
    return tx, ty, tw, th


def generate_images(month_name: str, year: int) -> str:
    safe_month = month_name.strip()
    batch_name = f"{safe_month}_{year}"
    output_dir = os.path.join(TEMP_DIR, batch_name)
    zip_path = os.path.join(TEMP_DIR, f"{batch_name}.zip")

    # Clean old folder/zip if exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    os.makedirs(output_dir, exist_ok=True)

    # Load fonts
    day_font = ImageFont.truetype(FONT_PATH, DAY_FONT_SIZE)
    ordinal_font = ImageFont.truetype(FONT_PATH, ORDINAL_FONT_SIZE)
    month_font = ImageFont.truetype(FONT_PATH, MONTH_FONT_SIZE)

    # Load template image
    template = Image.open(TEMPLATE_PATH).convert("RGBA")

    for day in range(1, 32):
        img = template.copy()
        draw = ImageDraw.Draw(img)

        # -------- DAY NUMBER --------
        day_text = str(day)
        day_x, day_y, day_w, day_h = center_text(draw, day_text, day_font, DAY_BOX)
        final_day_y = day_y + DAY_Y_OFFSET

        draw.text(
            (day_x, final_day_y),
            day_text,
            font=day_font,
            fill=TEXT_COLOR
        )

        # -------- ORDINAL --------
        ord_text = ordinal(day)
        ord_bbox = draw.textbbox((0, 0), ord_text, font=ordinal_font)
        ord_w = ord_bbox[2] - ord_bbox[0]
        ord_h = ord_bbox[3] - ord_bbox[1]

        ord_x = day_x + day_w + 10
        ord_y = final_day_y - (ord_h // 3) + ORDINAL_Y_OFFSET

        draw.text(
            (ord_x, ord_y),
            ord_text,
            font=ordinal_font,
            fill=TEXT_COLOR
        )

        # -------- MONTH --------
        month_x, month_y, _, month_h = center_text(draw, safe_month, month_font, MONTH_BOX)
        final_month_y = month_y + MONTH_Y_OFFSET + DAY_MONTH_GAP

        draw.text(
            (month_x, final_month_y),
            safe_month,
            font=month_font,
            fill=TEXT_COLOR
        )

        # -------- SAVE IMAGE --------
        filename = f"{day} {safe_month} {year}.png"
        img.save(os.path.join(output_dir, filename))

    # Create ZIP
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)
            zipf.write(file_path, arcname=file_name)

    return zip_path
