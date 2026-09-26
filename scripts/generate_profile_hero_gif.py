import io
import re
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FRAMES = 32
DURATION_MS = 250
NAME = "Rajender Mohan Verma"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def render_base(svg_path: Path, light: bool) -> Image.Image:
    svg = svg_path.read_text(encoding="utf-8")

    # Remove only the animated name group. GitHub's README image pipeline can
    # render the SVG as a static image, so the GIF supplies the actual motion.
    svg = re.sub(
        r'<clipPath id="nameClip">.*?</g>\s*</g>\s*',
        '<text x="76" y="190" fill="#F8FAFC" font-family="ui-sans-serif,system-ui,Arial,sans-serif" font-size="34" font-weight="800">Rajender Mohan Verma</text>',
        svg,
        count=1,
        flags=re.DOTALL,
    )

    png = cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=1200,
        output_height=700,
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def make_gif(svg_path: Path, output_path: Path, light: bool) -> None:
    base = render_base(svg_path, light)
    font = ImageFont.truetype(FONT_PATH, 34)
    name_color = (15, 23, 42, 255) if light else (248, 250, 252, 255)

    frames = []
    travel = 480

    for index in range(FRAMES):
        frame = base.copy()
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        clip = (76, 150, 486, 208)
        offset = int(travel * index / (FRAMES - 1))
        draw.text((76 - offset, 150), NAME, font=font, fill=name_color)
        draw.text((76 - offset + travel, 150), NAME, font=font, fill=name_color)

        mask = Image.new("L", frame.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(clip, radius=8, fill=255)
        frame.alpha_composite(
            Image.composite(layer, Image.new("RGBA", frame.size), mask)
        )

        frames.append(
            frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
        )

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

print("Generated GitHub-compatible marquee GIFs.")
