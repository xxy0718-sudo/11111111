# app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io, os

# default local image path (provided in conversation)
DEFAULT_IMAGE_PATH = "/mnt/data/IMG_8504.JPG"

st.set_page_config(page_title="Photo Poster with Chinese Text", layout="wide")

st.title("📷 Photo Poster — add Chinese text overlay")
st.markdown("Display the photo and overlay Chinese text. Default phrase: **诡秘晚上一起打三角洲**")

# Sidebar controls
st.sidebar.header("Image / Text Settings")
use_default = st.sidebar.checkbox("Use default image (/mnt/data/IMG_8504.JPG)", value=True)
uploaded = None
if not use_default:
    uploaded = st.sidebar.file_uploader("Upload an image (PNG / JPG)", type=["png","jpg","jpeg"])

# Font upload (optional)
st.sidebar.markdown("**Optional:** upload a .ttf font that supports Chinese (recommended if characters do not show).")
uploaded_font = st.sidebar.file_uploader("Upload .ttf font", type=["ttf","otf"])

# Text settings
text_default = "诡秘晚上一起打三角洲"
text_input = st.sidebar.text_input("Text to overlay", value=text_default)
font_size = st.sidebar.slider("Font size", 24, 220, 96)
color = st.sidebar.color_picker("Text color", "#0b0b0b")
alpha = st.sidebar.slider("Text opacity", 0, 255, 230)
stroke_width = st.sidebar.slider("Stroke width (outline)", 0, 8, 2)
stroke_fill = st.sidebar.color_picker("Stroke color", "#ffffff")
pos_x = st.sidebar.slider("Horizontal position (%)", 0, 100, 50)
pos_y = st.sidebar.slider("Vertical position (%)", 0, 100, 20)

# Effects
brightness = st.sidebar.slider("Image brightness", 0.2, 2.0, 1.0)
contrast = st.sidebar.slider("Image contrast", 0.2, 2.0, 1.0)

if use_default:
    if os.path.exists(DEFAULT_IMAGE_PATH):
        image = Image.open(DEFAULT_IMAGE_PATH).convert("RGBA")
    else:
        st.error(f"Default image not found at {DEFAULT_IMAGE_PATH}. Please upload one.")
        image = None
else:
    image = None
    if uploaded:
        image = Image.open(uploaded).convert("RGBA")

if image is None:
    st.stop()

# Apply brightness/contrast
if brightness != 1.0:
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)
if contrast != 1.0:
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)

# Try to load a Chinese-capable font.
def load_chinese_font(uploaded_font_file, size):
    # 1) if user uploaded a font file, use it
    if uploaded_font_file is not None:
        try:
            font_bytes = uploaded_font_file.read()
            return ImageFont.truetype(io.BytesIO(font_bytes), size=size)
        except Exception as e:
            st.sidebar.error(f"Failed to load uploaded font: {e}")
    # 2) try common system font paths
    common_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/truetype/arphic/ukai.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:\\Windows\\Fonts\\simhei.ttf",
        "C:\\Windows\\Fonts\\msyh.ttc",
    ]
    for p in common_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue
    # 3) fallback to default PIL font (may not render Chinese)
    return ImageFont.load_default()

font = load_chinese_font(uploaded_font, font_size)

# Prepare draw canvas
canvas = image.copy()
draw = ImageDraw.Draw(canvas)

# Compute position
W, H = canvas.size
x = int(W * (pos_x / 100.0))
y = int(H * (pos_y / 100.0))

# Measure text size and adjust anchor to center
try:
    text_bbox = draw.textbbox((0,0), text_input, font=font, stroke_width=stroke_width)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
except Exception:
    text_w, text_h = draw.textsize(text_input, font=font)

anchor_x = x - text_w // 2
anchor_y = y - text_h // 2

# Draw stroke (outline) first if stroke_width > 0 by drawing multiple offsets
if stroke_width > 0:
    # PIL supports stroke parameters in recent versions; use stroke if available
    try:
        draw.text((anchor_x, anchor_y), text_input, font=font, fill=stroke_fill + (255,), stroke_width=stroke_width, stroke_fill=stroke_fill)
    except TypeError:
        # Fallback: manual outline by drawing text multiple times
        for dx in range(-stroke_width, stroke_width+1):
            for dy in range(-stroke_width, stroke_width+1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((anchor_x+dx, anchor_y+dy), text_input, font=font, fill=stroke_fill)

# Draw main text with requested opacity
# color is hex like '#rrggbb', convert to RGBA with alpha
def hex_to_rgba(hex_color, alpha_val):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, alpha_val)

rgba = hex_to_rgba(color, alpha)
try:
    draw.text((anchor_x, anchor_y), text_input, font=font, fill=rgba, stroke_width=0)
except Exception:
    # fallback: draw without alpha if something fails
    draw.text((anchor_x, anchor_y), text_input, font=font, fill=rgba[:3])

# Show UI: original and edited
st.subheader("Preview")
col1, col2 = st.columns(2)
with col1:
    st.image(image, caption="Original image", use_column_width=True)
with col2:
    # convert to bytes for download
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    buf.seek(0)
    st.image(buf, caption=f"Poster with text: {text_input}", use_column_width=True)
    st.download_button("Download poster (PNG)", data=buf, file_name="poster_with_text.png", mime="image/png")

# Helpful note about fonts
st.markdown("---")
st.markdown("**Note:** If Chinese characters don't render correctly, either upload a Chinese-capable `.ttf` font in the sidebar or deploy to an environment that has CJK fonts (e.g. Noto Sans CJK).")
