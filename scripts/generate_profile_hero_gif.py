import io
import math
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FRAMES = 72
DURATION_MS = 90


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
    """Move gradient colors inside a fixed-size region."""
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
        line_color = (203, 213, 225, 255)
        accent_colors = [(109, 40, 217), (8, 145, 178), (5, 150, 105)]
        status_color = (5, 150, 105)
        avatar_color = (8, 145, 178)
    else:
        line_color = (38, 52, 73, 255)
        accent_colors = [(139, 92, 246), (34, 211, 238), (52, 211, 153)]
        status_color = (52, 211, 153)
        avatar_color = (34, 211, 238)

    top_line = (510, 226, 1148, 230)
    top_accent = (510, 226, 730, 230)
    footer_accent = (1048, 615, 1118, 619)
    online_dot = (1110, 50)
    avatar_center = (103, 188)

    top_width = top_accent[2] - top_accent[0]
    footer_width = footer_accent[2] - footer_accent[0]

    top_gradient = make_gradient(520, 4, accent_colors)
    footer_gradient = make_gradient(180, 4, accent_colors)

    frames = []

    for index in range(FRAMES):
        phase = index / FRAMES
        frame = base.copy()

        # 1) Smooth moving accent under the main identity.
        line_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(line_layer)
        draw.rounded_rectangle(top_line, radius=2, fill=line_color)

        top_visible = shifted_gradient(
            top_gradient,
            top_width,
            int(phase * top_gradient.width),
        )
        line_layer.alpha_composite(top_visible, (top_accent[0], top_accent[1]))

        footer_visible = shifted_gradient(
            footer_gradient,
            footer_width,
            int(phase * footer_gradient.width),
        )
        line_layer.alpha_composite(
            footer_visible,
            (footer_accent[0], footer_accent[1]),
        )

        line_mask = Image.new("L", frame.size, 0)
        mask_draw = ImageDraw.Draw(line_mask)
        mask_draw.rounded_rectangle(top_line, radius=2, fill=255)
        mask_draw.rounded_rectangle(footer_accent, radius=2, fill=255)

        frame.alpha_composite(
            Image.composite(
                line_layer,
                Image.new("RGBA", frame.size, (0, 0, 0, 0)),
                line_mask,
            )
        )

        # 2) Gentle ONLINE pulse, kept inside the existing terminal bar.
        pulse = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(phase * math.tau))
        status_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        status_draw = ImageDraw.Draw(status_layer)

        glow_radius = 7 + int(3 * pulse)
        glow_alpha = int(25 + 45 * pulse)
        status_draw.ellipse(
            (
                online_dot[0] - glow_radius,
                online_dot[1] - glow_radius,
                online_dot[0] + glow_radius,
                online_dot[1] + glow_radius,
            ),
            fill=(*status_color, glow_alpha),
        )
        status_draw.ellipse(
            (
                online_dot[0] - 5,
                online_dot[1] - 5,
                online_dot[0] + 5,
                online_dot[1] + 5,
            ),
            fill=(*status_color, 255),
        )
        frame.alpha_composite(status_layer)

        # 3) Soft avatar ring pulse. This adds motion without moving the layout.
        avatar_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        avatar_draw = ImageDraw.Draw(avatar_layer)
        ring_alpha = int(55 + 80 * pulse)
        ring_width = 2 + int(pulse)
        radius = 19 + int(2 * pulse)
        avatar_draw.ellipse(
            (
                avatar_center[0] - radius,
                avatar_center[1] - radius,
                avatar_center[0] + radius,
                avatar_center[1] + radius,
            ),
            outline=(*avatar_color, ring_alpha),
            width=ring_width,
        )
        frame.alpha_composite(avatar_layer)

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

print("Generated polished hero GIFs with fixed layout and subtle micro-animations.")
