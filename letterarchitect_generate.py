import argparse
import os

import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw

from typing import List, Tuple

from dataclasses import dataclass

FONT_SIZE = 350
SMALL_FONT_SIZE = 175


class Font:
    def __init__(self, font_path: str):
        self.LARGE: PIL.ImageFont.FreeTypeFont = PIL.ImageFont.truetype(
            font_path, FONT_SIZE
        )
        self.SMALL: PIL.ImageFont.FreeTypeFont = PIL.ImageFont.truetype(
            font_path, SMALL_FONT_SIZE
        )


class FontFamily:
    LATIN: Font = Font("fonts/noto-serif.ttf")
    PHOENICIAN: Font = Font("fonts/noto-phoenician.ttf")
    ARABIC: Font = Font("fonts/noto-arabic.ttf")


def load_image(image_path: str):
    with PIL.Image.open(image_path) as img:
        # Ensure image is in RGB mode to support custom colours
        img = img.convert("RGB")

    return img


class BaseImage:
    BLUE: PIL.Image.Image = load_image("materials/blue.png")
    GREY: PIL.Image.Image = load_image("materials/grey.png")
    GREEN: PIL.Image.Image = load_image("materials/green.png")
    ORANGE: PIL.Image.Image = load_image("materials/orange.png")


class Colour:
    BLUE: str = "#084FA9"
    GREY: str = "#505050"
    GREEN: str = "#14B530"
    ORANGE: str = "#F4CC3C"


@dataclass
class Alphabet:
    base_image: PIL.Image.Image
    font: Font
    characters: List[str] | List[Tuple[str, str]]
    colour: str


alphabets = {
    "latin": Alphabet(
        base_image=BaseImage.GREY,
        colour=Colour.GREY,
        font=FontFamily.LATIN,
        characters=[
            "x",
            "y",
        ],
    ),
    "greek": Alphabet(
        base_image=BaseImage.GREEN,
        colour=Colour.GREEN,
        font=FontFamily.LATIN,
        characters=[
            ("α", "a"),
            ("β", "b"),
            ("γ", "c/g"),
            ("δ", "d"),
            ("ε", "e"),
            ("ϝ", "f/v"),
            ("υ", "u/i/w"),
            ("ζ", "z"),
            ("η", "h"),
            ("ι", "j"),
            ("κ", "k"),
            ("λ", "l"),
            ("μ", "m"),
            ("ν", "n"),
            ("χ", "ch"),
            ("ο", "o"),
            ("π", "p"),
            ("ϙ", "q"),
            ("ρ", "r"),
            ("σ", "s"),
            ("τ", "t"),
        ],
    ),
    "arabic": Alphabet(
        base_image=BaseImage.ORANGE,
        colour=Colour.ORANGE,
        font=FontFamily.ARABIC,
        characters=[
            ("ﺍ", "a"),
            ("ﺏ", "b"),
            ("ﺝ", "g"),
            ("ﺩ", "d"),
            # ("ﻩ", "e"),
            ("ف", "f/v"),
            ("ﻭ", "u/i/w"),
            ("ز", "z"),
            ("ﺡ", "h"),
            ("ﻱ", "j"),
            ("ﻙ", "k"),
            ("ﻝ", "l"),
            ("ﻡ", "m"),
            ("ﻥ", "n"),
            # ("ﻉ", "o"),
            # ("ﻑ", "p"),
            ("ﻕ", "q"),
            ("ﺭ", "r"),
            ("ﺱ", "s"),
            ("ﺕ", "t"),
        ],
    ),
    "phoenician": Alphabet(
        base_image=BaseImage.BLUE,
        colour=Colour.BLUE,
        font=FontFamily.PHOENICIAN,
        characters=[
            ("𐤀", "a"),
            ("𐤁", "b"),
            ("𐤂", "c/g"),
            ("𐤃", "d"),
            ("𐤄", "e"),
            ("𐤅", "u/i/w"),
            ("𐤆", "z"),
            ("𐤇", "h"),
            ("𐤉", "j"),
            ("𐤊", "k"),
            ("𐤋", "l"),
            ("𐤌", "m"),
            ("𐤍", "n"),
            ("𐤎", "ch"),
            ("𐤏", "o"),
            ("𐤐", "p"),
            ("𐤒", "q"),
            ("𐤓", "r"),
            ("𐤔", "s"),
            ("𐤕", "t"),
        ],
    ),
}


def build_image(
    base_image: PIL.Image.Image,
    character: str,
    font: Font,
    color: str,
):
    image = base_image.copy()
    draw = PIL.ImageDraw.Draw(image)

    if len(character) == 1:
        true_font = font.LARGE
    else:
        true_font = font.SMALL

    # 1. Get the bounding box of the text
    # We use (0, 0) as the dummy anchor to measure the text size
    bbox = draw.textbbox((0, 0), character, font=true_font)

    # bbox is (left, top, right, bottom)
    left, top, right, bottom = bbox

    text_width = right - left
    text_height = bottom - top

    text_width = right - left
    text_height = bottom - top

    # 2. Calculate the center position
    # We want the visual center of the text to be at the center of the image
    target_x = (base_image.width - text_width) / 2
    target_y = (base_image.height - text_height) / 2

    # 3. Draw the text
    # IMPORTANT: We must subtract the 'left' and 'top' offsets from the bbox.
    # If we don't, the internal font padding will push the characters
    # down and to the right.
    draw.text((target_x - left, target_y - top), character, font=true_font, fill=color)

    return image


def combine_into_foldable(
    front_image: PIL.Image.Image, back_image: PIL.Image.Image
) -> PIL.Image.Image:
    line_thickness = 1

    combined_width = front_image.width + line_thickness + back_image.width
    combined_height = max(front_image.height, back_image.height)

    combined_image = PIL.Image.new("RGB", (combined_width, combined_height))
    combined_image.paste(front_image, (0, 0))
    combined_image.paste(back_image, (back_image.width + line_thickness, 0))

    line_x = front_image.width
    line_color = (128, 128, 128, 64)
    dot_size = 2  # Length of each dash/dot
    gap_size = 4  # Gap between dots

    draw = PIL.ImageDraw.Draw(combined_image)
    for y in range(0, combined_height, dot_size + gap_size):
        # Draw a tiny vertical line segment
        draw.line(
            [(line_x, y), (line_x, min(y + dot_size, combined_height))], fill=line_color
        )

    draw.line([(0, 0), (combined_width, 0)], fill=line_color)
    draw.line([(0, 0), (0, combined_height)], fill=line_color)
    draw.line([(combined_width - 1, 0), (combined_width - 1, combined_height - 1)], fill=line_color)
    draw.line([(0, combined_height - 1), (combined_width - 1, combined_height - 1)], fill=line_color)

    return combined_image


def get_character_path(output_dir: str, alphabet_name: str, character_name: str):
    character_name = character_name.replace("/", "_")
    alphabet_dir = os.path.join(output_dir, alphabet_name)
    os.makedirs(alphabet_dir, exist_ok=True)

    return os.path.join(alphabet_dir, f"{character_name}.png")


def generate_tiles(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    for alphabet_name, alphabet in alphabets.items():
        for character_index, character_set in enumerate(alphabet.characters):
            # single character
            if isinstance(character_set, str):
                latin_character = character_set
                foreign_character = character_set
            elif isinstance(character_set, tuple):
                foreign_character, latin_character = character_set
            else:
                raise TypeError("Character set is of an invalid type")

            character_path = get_character_path(
                output_dir, alphabet_name, latin_character
            )
            character_img = build_image(
                alphabet.base_image, foreign_character, alphabet.font, alphabet.colour
            )
            character_img.save(character_path)


def generate_folds(foldables_dir: str):
    os.makedirs(foldables_dir, exist_ok=True)

    latin_alphabet = alphabets["latin"]

    for alphabet_name, alphabet in alphabets.items():
        for character_index, character_set in enumerate(alphabet.characters):
            # single character
            if isinstance(character_set, str):
                latin_character = character_set
                foreign_character = character_set
            elif isinstance(character_set, tuple):
                foreign_character, latin_character = character_set
            else:
                raise TypeError("Character set is of an invalid type")

            character_path = get_character_path(
                foldables_dir, alphabet_name, latin_character
            )
            foreign_character_image = build_image(
                alphabet.base_image, foreign_character, alphabet.font, alphabet.colour
            )
            latin_character_image = build_image(
                latin_alphabet.base_image,
                latin_character,
                latin_alphabet.font,
                latin_alphabet.colour,
            )

            foldable_image = combine_into_foldable(
                foreign_character_image, latin_character_image
            )
            foldable_image.save(character_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="letterarchitect - generate character tiles"
    )
    parser.add_argument(
        "output_dir", type=str, help="where to save the generated characters"
    )
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        raise FileNotFoundError("Output directory does not exist")

    singles_dir = os.path.join(args.output_dir, "single")
    os.makedirs(singles_dir, exist_ok=True)
    generate_tiles(singles_dir)

    foldables_dir = os.path.join(args.output_dir, "foldables")
    os.makedirs(foldables_dir, exist_ok=True)
    generate_folds(foldables_dir)
