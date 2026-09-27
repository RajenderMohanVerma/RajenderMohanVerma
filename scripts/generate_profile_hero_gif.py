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


def shifted_gradient(base_gradient: Image.Image, width: int, shift: int) -> Image.Image:
    """Move the gradient inside a fixed-size line without moving the line itself."""
    canvas = Image.new(
        "RGBA",
        (base_gradient.width * 2, base_gradient.height),
        (0, 0, 0, 0),
    )
    canvas.alpha_composite(base_gradient, (0, 0))
    canvas.alpha_composite(base_gradient, (base_gradient.width, 0))

    start = shift % base_gradient.width
    return canvas.crop((start, 0, start + width, base_gradient.height))


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

    # Slightly smaller than the source SVG so the complete name fits the card.
    font = ImageFont.truetype(FONT_PATH, 30)

    # Animation is restricted to these regions. Everything else is copied
    # pixel-for-pixel from the source SVG, including the outer container.
    name_box = (76, 150, 486, 198)
    top_line = (550, 224, 1128, 230)
    bottom_line = (76, 592, 254, 600)

    bbox = font.getbbox(NAME)
    text_width = bbox[2] - bbox[0]
    travel = text_width + 52

    top_width = top_line[2] - top_line[0]
    bottom_width = bottom_line[2] - bottom_line[0]

    top_gradient = make_gradient(420, 4, gradient_colors)
    bottom_gradient = make_gradient(356, 4, gradient_colors)

    frames = []

    for index in range(FRAMES):
        frame = base.copy()
        phase = index / FRAMES

        # Moving name, clipped to its existing card area.
        offset = int(round(travel * index / FRAMES))
        name_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        name_draw = ImageDraw.Draw(name_layer)

        name_draw.rounded_rectangle(name_box, radius=8, fill=card_color)
        name_draw.text((76 - offset, 154), NAME, font=font, fill=name_color)
        name_draw.text(
            (76 - offset + travel, 154),
            NAME,
            font=font,
            fill=name_color,
        )

        name_mask = Image.new("L", frame.size, 0)
        ImageDraw.Draw(name_mask).rounded_rectangle(
            name_box,
            radius=8,
            fill=255,
        )

        frame.alpha_composite(
            Image.composite(
                name_layer,
                Image.new("RGBA", frame.size, (0, 0, 0, 0)),
                name_mask,
            )
        )

        # Moving colors inside the existing accent lines.
        line_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        line_draw = ImageDraw.Draw(line_layer)

        line_draw.rectangle(top_line, fill=line_color)
        line_draw.rectangle(bottom_line, fill=line_color)

        top_shift = int(phase * top_gradient.width)
        bottom_shift = int(phase * bottom_gradient.width)

        top_visible = shifted_gradient(top_gradient, top_width, top_shift)
        bottom_visible = shifted_gradient(bottom_gradient, bottom_width, bottom_shift)

        line_layer.alpha_composite(top_visible, (top_line[0], top_line[1] + 1))
        line_layer.alpha_composite(
            bottom_visible,
            (bottom_line[0], bottom_line[1] + 2),
        )

        line_mask = Image.new("L", frame.size, 0)
        line_mask_draw = ImageDraw.Draw(line_mask)
        line_mask_draw.rectangle(top_line, fill=255)
        line_mask_draw.rectangle(bottom_line, fill=255)

        frame.alpha_composite(
            Image.composite(
                line_layer,
                Image.new("RGBA", frame.size, (0, 0, 0, 0)),
                line_mask,
            )
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

print("Generated hero GIFs: preserved container + smooth name + moving accent gradients.")
