import argparse
import os

import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw

from typing import List, Tuple

from dataclasses import dataclass

FONT_SIZE = 350


class Font:
    LATIN: PIL.ImageFont.FreeTypeFont = PIL.ImageFont.truetype(
        "fonts/noto-serif.ttf", FONT_SIZE
    )
    PHOENICIAN: PIL.ImageFont.FreeTypeFont = PIL.ImageFont.truetype(
        "fonts/noto-phoenician.ttf", FONT_SIZE
    )
    ARABIC: PIL.ImageFont.FreeTypeFont = PIL.ImageFont.truetype(
        "fonts/noto-arabic.ttf", FONT_SIZE
    )


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
    font: PIL.ImageFont.FreeTypeFont
    characters: List[str] | List[Tuple[str, str]]
    colour: str


alphabets = {
    "latin": Alphabet(
        base_image=BaseImage.GREY,
        colour=Colour.GREY,
        font=Font.LATIN,
        characters=[
            "a",
            "b",
            "g",
            "d",
            "e",
            "u",
            "i",
            "w",
            "z",
            "h",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
        ],
    ),
    "greek": Alphabet(
        base_image=BaseImage.GREEN,
        colour=Colour.GREEN,
        font=Font.LATIN,
        characters=[
            ("α", "a"),
            ("β", "b"),
            ("γ", "g"),
            ("δ", "d"),
            ("ε", "e"),
            ("υ", "u/i/w"),
            ("ζ", "z"),
            ("η", "h"),
            ("ι", "j"),
            ("κ", "k"),
            ("λ", "l"),
            ("μ", "m"),
            ("ν", "n"),
            ("χ", "ch ??"),
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
        font=Font.ARABIC,
        characters=[
            ("ﺍ", "a"),
            ("ﺏ", "b"),
            ("ﺝ", "g"),
            ("ﺩ", "d"),
            ("ﻩ", "e"),
            ("ﻭ", "u/i/w"),
            ("ﺯ", "z"),
            ("ﺡ", "h"),
            ("ﻱ", "j"),
            ("ﻙ", "k"),
            ("ﻝ", "l"),
            ("ﻡ", "m"),
            ("ﻥ", "n"),
            ("ﻉ", "o"),
            ("ﻑ", "p"),
            ("ﻕ", "q"),
            ("ﺭ", "r"),
            ("ﺱ", "s"),
            ("ﺕ", "t"),
        ],
    ),
    "phoenician": Alphabet(
        base_image=BaseImage.BLUE,
        colour=Colour.BLUE,
        font=Font.PHOENICIAN,
        characters=[
            ("𐤀", "a"),
            ("𐤁", "b"),
            ("𐤂", "g"),
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
            ("𐤎", "ch ??"),
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
    font: PIL.ImageFont.FreeTypeFont,
    color: str,
):
    image = base_image.copy()
    draw = PIL.ImageDraw.Draw(image)

    # 1. Get the bounding box of the text
    # We use (0, 0) as the dummy anchor to measure the text size
    bbox = draw.textbbox((0, 0), character, font=font)

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
    draw.text((target_x - left, target_y - top), character, font=font, fill=color)

    return image


def main(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    for alphabet_name, alphabet in alphabets.items():
        alphabet_dir = os.path.join(output_dir, alphabet_name)
        os.makedirs(alphabet_dir, exist_ok=True)

        for character_index, character_set in enumerate(alphabet.characters):
            # single character
            if isinstance(character_set, str):
                latin_character = character_set
                foreign_character = character_set
            elif isinstance(character_set, tuple):
                foreign_character, latin_character = character_set

            character_path = os.path.join(alphabet_dir, f"{character_index}.png")
            character_img = build_image(
                alphabet.base_image, foreign_character, alphabet.font, alphabet.colour
            )
            character_img.save(character_path)


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

    main(args.output_dir)
