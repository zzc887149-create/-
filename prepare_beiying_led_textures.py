"""Generate authentic 1600x700 main-stage LED screen textures (led_left, led_center, led_right)
from the real 2026.09.13 Zhao Lei Beijing Bird's Nest concert footage of 《背影》
at the exact lyric moment '昨日是庆幸着 为何今日要感伤 / 让烦恼都随雨流进下水道'."""
import random
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

ROOT = Path(r"C:\Users\Lenovo\Desktop\赵雷鸟巢")
SCRATCH = Path(r"C:\Users\Lenovo\.gemini\antigravity\brain\50316f40-8b5c-454c-8524-27d94ec9e1ce\scratch\beiying")
OUT_TEX = ROOT / "textures"
UNITY_TEX = ROOT / "unity_enhanced/UnityProject/Assets/ZhaoLeiBirdsNestEnhanced/Textures"

W, H = 1600, 700

# Load real live frames from the 2026.09.13 Bird's Nest concert performance of 《背影》
f46 = Image.open(SCRATCH / "f_46.png").convert("RGB")
f49 = Image.open(SCRATCH / "f_49.png").convert("RGB")
f50 = Image.open(SCRATCH / "f_50.5.png").convert("RGB")
f52 = Image.open(SCRATCH / "f_52.png").convert("RGB")

# 1. Perspective-rectify the Left Wing Screen (flowing starry rain visual) from f_46 and f_50.5
# Quad in 640x360 frame: (top-left, bottom-left, bottom-right, top-right)
left_quad_50 = (27, 6, 23, 195, 305, 199, 309, 9)
left_quad_46 = (36, 6, 32, 195, 316, 198, 320, 9)

wing_50 = f50.transform((W, H), Image.Transform.QUAD, left_quad_50, Image.Resampling.BICUBIC)
wing_46 = f46.transform((W, H), Image.Transform.QUAD, left_quad_46, Image.Resampling.BICUBIC)
wing_49 = f49.transform((W, H), Image.Transform.QUAD, left_quad_50, Image.Resampling.BICUBIC)

# Blend the upper rain region from wing_50 and wing_49 to reduce H.264 compression noise
rain_base = Image.blend(wing_50, wing_49, 0.45)

# Clean out the low-res 360p burned-in subtitle strip at the bottom (y in 580..698, x in 160..1240)
# by patching from the clean rain pattern directly above it (y in 450..568 shifted along the diagonal rain angle)
rain_patch = rain_base.crop((220, 450, 1300, 568)).resize((1080, 118), Image.Resampling.BICUBIC)
mask_sub = Image.new("L", (1080, 118), 0)
mdraw = ImageDraw.Draw(mask_sub)
mdraw.rounded_rectangle((12, 8, 1068, 112), radius=22, fill=255)
mask_sub = mask_sub.filter(ImageFilter.GaussianBlur(radius=10))
rain_clean = rain_base.copy()
rain_clean.paste(rain_patch, (160, 580), mask_sub)

# Enhance contrast and color richness of the real live dark-blue starry rainwater streams
rain_clean = ImageEnhance.Contrast(rain_clean).enhance(1.18)
rain_clean = ImageEnhance.Color(rain_clean).enhance(1.12)
rain_clean = rain_clean.filter(ImageFilter.UnsharpMask(radius=2.2, percent=135, threshold=3))

# Add subtle high-resolution starry rain droplets ONLY where the real live frame already has bright blue-white rain streaks
rng = random.Random(20260913)
sparkle_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sdraw = ImageDraw.Draw(sparkle_layer)
px = rain_clean.load()
for _ in range(4200):
    x = rng.randint(8, W - 9)
    y = rng.randint(8, H - 9)
    r, g, b = px[x, y]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum > 42:
        alpha = min(210, int((lum - 35) * 1.9))
        rad = 1 if rng.random() < 0.78 else 2
        col = (min(255, r + 55), min(255, g + 60), min(255, b + 65), alpha)
        sdraw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col)

sparkle_layer = sparkle_layer.filter(ImageFilter.GaussianBlur(radius=0.6))
rain_hd = Image.alpha_composite(rain_clean.convert("RGBA"), sparkle_layer)


def add_live_subtitle(base_rgba: Image.Image, text: str, x_pos: int = 290, y_pos: int = 602) -> Image.Image:
    """Render crisp live concert subtitle at the bottom matching the exact position and style of f_50.5.png."""
    font_path = r"C:\Windows\Fonts\msyhbd.ttc"
    font = ImageFont.truetype(font_path, 48)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    fdraw = ImageDraw.Draw(fg)

    # Dark subtle shadow + soft cyan-white LED glow + crisp white glyph core
    gdraw.text((x_pos + 2, y_pos + 2), text, font=font, fill=(0, 8, 22, 210))
    gdraw.text((x_pos, y_pos), text, font=font, fill=(170, 225, 255, 155))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=5.5))

    fdraw.text((x_pos, y_pos), text, font=font, fill=(246, 250, 255, 250))
    out = Image.alpha_composite(base_rgba, glow)
    out = Image.alpha_composite(out, fg)
    return out.convert("RGB")


# Both wing screens in the real concert show the synchronized rain visual + current lyric subtitle '让烦恼都随雨流进下水道'
led_left_img = add_live_subtitle(rain_hd, "让烦恼都随雨流进下水道", x_pos=295, y_pos=604)

# For the right wing screen, slightly shift the rain crop horizontally so the two side screens feel organic and alive
rain_hd_right = rain_hd.transform((W, H), Image.Transform.AFFINE, (1, 0, 18, 0, 1, 0), Image.Resampling.BICUBIC)
led_right_img = add_live_subtitle(rain_hd_right, "让烦恼都随雨流进下水道", x_pos=295, y_pos=604)

# 2. Perspective-rectify the Center Curved Screen (starry rain arch + children's choir in white dresses)
# In f_50.5.png, the center screen spans x in [330, 639], y in [10, 198]
center_quad_50 = (332, 10, 326, 196, 639, 198, 639, 14)
center_50 = f50.transform((W, H), Image.Transform.QUAD, center_quad_50, Image.Resampling.BICUBIC)
center_46 = f46.transform((W, H), Image.Transform.QUAD, center_quad_50, Image.Resampling.BICUBIC)

# Also load the closer frontal shot from beiying.mp4 (sheet_line / line_full) to enrich facial/dress detail
line_full = Image.open(SCRATCH / "line_full.png").convert("RGB")
# Top-left tile of line_full.png is 640x360 at t=23s
choir_close = line_full.crop((0, 0, 640, 125)).resize((W, int(H * 0.62)), Image.Resampling.BICUBIC)

# Enhance the rectified real center screen from f_50.5.png (which has the full arch + cyan backlight + children's choir)
center_hd = ImageEnhance.Contrast(center_50).enhance(1.12)
center_hd = ImageEnhance.Color(center_hd).enhance(1.08)
center_hd = center_hd.filter(ImageFilter.UnsharpMask(radius=2.0, percent=125, threshold=3)).convert("RGBA")

# Add fine starry rain shimmer along the dark arch border at the top and left/right edges of the center screen
c_sparkle = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cdraw = ImageDraw.Draw(c_sparkle)
cpx = center_50.load()
for _ in range(2600):
    x = rng.randint(6, W - 7)
    y = rng.randint(6, H - 7)
    # Arch region is near the top/sides where blue/dark-teal starry particles appear
    r, g, b = cpx[x, y]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    # Only in the dark starry arch frame (not on the bright white dresses / faces where lum > 135)
    if 28 < lum < 115 and (y < 210 or x < 260 or x > 1380):
        alpha = min(185, int((lum - 22) * 1.8))
        rad = 1 if rng.random() < 0.8 else 2
        cdraw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(min(255, r + 60), min(255, g + 70), min(255, b + 80), alpha))

c_sparkle = c_sparkle.filter(ImageFilter.GaussianBlur(radius=0.6))
led_center_img = Image.alpha_composite(center_hd, c_sparkle).convert("RGB")

# Save to textures/ and Unity Assets/ZhaoLeiBirdsNestEnhanced/Textures/
led_left_img.save(OUT_TEX / "led_left.jpg", quality=95)
led_center_img.save(OUT_TEX / "led_center.jpg", quality=95)
led_right_img.save(OUT_TEX / "led_right.jpg", quality=95)

shutil.copy2(OUT_TEX / "led_center.jpg", UNITY_TEX / "BNE_020_texture.jpg")
shutil.copy2(OUT_TEX / "led_left.jpg", UNITY_TEX / "BNE_021_texture.jpg")
shutil.copy2(OUT_TEX / "led_right.jpg", UNITY_TEX / "BNE_022_texture.jpg")
print("Saved updated led_left.jpg, led_center.jpg, led_right.jpg and BNE_020..022_texture.jpg")
