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


def make_gradient(width: int, height: int, colors: list[tuple[int, int, int]]) -> Image.Image:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = image.load()

    segments = len(colors) - 1
    for x in range(width):
        position = x / max(1, width - 1) * segments
        segment = min(int(position), segments - 1)
        local = position - segment
        c1 = colors[segment]
        c2 = colors[segment + 1]
        rgb = tuple(int(c1[i] + (c2[i] - c1[i]) * local) for i in range(3))
        for y in range(height):
            pixels[x, y] = (*rgb, 255)

    return image


def paste_wrapped_gradient(
    frame: Image.Image,
    gradient: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
    clip_left: int,
    clip_right: int,
) -> None:
    # Repeat the gradient horizontally so the moving band never disappears.
    band = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for start in range(-gradient.width, width + gradient.width, gradient.width):
        band.alpha_composite(gradient, (start, 0))

    visible = band.crop((0, 0, width, height))
    mask = Image.new("L", frame.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle((clip_left, y, clip_right, y + height), fill=255)

    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    layer.alpha_composite(visible, (x, y))
    frame.alpha_composite(Image.composite(layer, Image.new("RGBA", frame.size), mask))


def make_gif(svg_path: Path, output_path: Path, light: bool) -> None:
    base = render_base(svg_path)

    if light:
        name_color = (15, 23, 42, 255)
        card_color = (241, 245, 249, 255)
        line_color = (203, 213, 225, 255)
        gradient_colors = [(109, 40, 217), (8, 145, 178), (5, 150, 105)]
    else:
        name_color = (248, 250, 252, 255)
        card_color = (15, 23, 42, 255)
        line_color = (38, 52, 73, 255)
        gradient_colors = [(139, 92, 246), (34, 211, 238), (52, 211, 153)]

    font = ImageFont.truetype(FONT_PATH, 34)

    # Exact name window inside the left card.
    name_box = (76, 150, 486, 198)
    bbox = font.getbbox(NAME)
    text_width = bbox[2] - bbox[0]
    travel = text_width + 52

    # Exact accent-line regions already present in the SVG.
    top_line = (550, 224, 1128, 230)
    bottom_line = (76, 592, 254, 600)

    gradient_top = make_gradient(210, 4, gradient_colors)
    gradient_bottom = make_gradient(178, 4, gradient_colors)

    frames = []

    for index in range(FRAMES):
        frame = base.copy()
        offset = int(round(travel * index / FRAMES))

        # Replace only the static name pixels. The surrounding card/container
        # remains untouched because the mask is limited to the name window.
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rectangle(name_box, fill=card_color)

        draw.text(
            (76 - offset, 150),
            NAME,
            font=font,
            fill=name_color,
        )
        draw.text(
            (76 - offset + travel, 150),
            NAME,
            font=font,
            fill=name_color,
        )

        name_mask = Image.new("L", frame.size, 0)
        ImageDraw.Draw(name_mask).rounded_rectangle(name_box, radius=8, fill=255)
        frame.alpha_composite(
            Image.composite(overlay, Image.new("RGBA", frame.size), name_mask)
        )

        # Restore the thin base line first, then animate the colored segment.
        line_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        line_draw = ImageDraw.Draw(line_layer)

        line_draw.rectangle(top_line, fill=line_color)
        line_draw.rectangle(bottom_line, fill=line_color)

        # Moving top accent.
        top_x = 550 + int((578 + 210) * index / FRAMES) - 210
        top_segment = gradient_top
        line_layer.alpha_composite(top_segment, (top_x, 225))

        # Moving bottom workflow accent.
        bottom_x = 76 + int((178 + 236) * index / FRAMES) - 178
        line_layer.alpha_composite(gradient_bottom, (bottom_x, 594))

        line_mask = Image.new("L", frame.size, 0)
        line_mask_draw = ImageDraw.Draw(line_mask)
        line_mask_draw.rectangle((550, 224, 1128, 230), fill=255)
        line_mask_draw.rectangle((76, 592, 490, 600), fill=255)

        frame.alpha_composite(
            Image.composite(line_layer, Image.new("RGBA", frame.size), line_mask)
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

print("Generated profile hero GIFs with preserved container and animated accent lines.")
