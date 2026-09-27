import io
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FRAMES = 72
DURATION_MS = 90
NAME = "Rajender Mohan Verma"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def render_base(svg_path: Path) -> Image.Image:
    png = cairosvg.svg2png(
        url=str(svg_path),
        output_width=1200,
        output_height=700,
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def make_gif(svg_path: Path, output_path: Path, light: bool) -> None:
    base = render_base(svg_path)
    font = ImageFont.truetype(FONT_PATH, 34)
    name_color = (15, 23, 42, 255) if light else (248, 250, 252, 255)
    bg_color = (241, 245, 249, 255) if light else (15, 23, 42, 255)

    clip_left, clip_top, clip_right, clip_bottom = 76, 150, 486, 198
    clip_width = clip_right - clip_left

    # Measure the real rendered text width so the loop has no jump/gap.
    bbox = font.getbbox(NAME)
    text_width = bbox[2] - bbox[0]
    gap = 52
    travel = text_width + gap

    frames = []
    for index in range(FRAMES):
        frame = base.copy()

        # Clear the static name area.
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle(
            (clip_left, clip_top, clip_right, clip_bottom),
            radius=8,
            fill=bg_color,
        )

        # Move continuously by one exact text+gap distance.
        offset = int(round(travel * index / FRAMES))
        x1 = clip_left - offset
        x2 = x1 + travel

        draw.text((x1, 150), NAME, font=font, fill=name_color)
        draw.text((x2, 150), NAME, font=font, fill=name_color)

        # Hard clip the moving text to the name window.
        mask = Image.new("L", frame.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (clip_left, clip_top, clip_right, clip_bottom),
            radius=8,
            fill=255,
        )
        clipped = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        clipped = Image.composite(overlay, clipped, mask)

        frame.alpha_composite(clipped)
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )


make_gif(
    ROOT / "assets/profile-hero-20260926-dark.svg",
    ROOT / "assets/profile-hero-marquee-dark.gif",
    light=False,
)
make_gif(
    ROOT / "assets/profile-hero-20260926-light.svg",
    ROOT / "assets/profile-hero-marquee-light.gif",
    light=True,
)

print("Generated smooth looping GitHub-compatible marquee GIFs.")
