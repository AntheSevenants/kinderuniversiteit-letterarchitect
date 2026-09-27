import argparse
import os
from typing import List, Tuple

import PIL.Image
import pandas as pd

from letterarchitect_generate import (
    build_image,
    get_character_path,
    load_image,
    alphabets,
)


def generate_key(tiles_path: str, output_dir: str, max_tile_height_px: int = 375):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # A4 Dimensions at 300 DPI (standard for print)
    A4_WIDTH = 3508
    A4_HEIGHT = 2480

    for alphabet_name, alphabet in alphabets.items():
        padding = 50
        padding_y = 35
        cursor_x = 0 + padding
        cursor_y = 0 + padding
        shelf_height = 0

        pages = []
        current_page = PIL.Image.new("RGB", (A4_WIDTH, A4_HEIGHT), (255, 255, 255))

        if alphabet_name == "latin":
            continue

        for foreign_character, latin_character in alphabet.characters:
            latin_character = latin_character.replace("/", "_")

            character_path = get_character_path(
                tiles_path, alphabet_name, latin_character
            )
            img = load_image(character_path)

            w, h = img.size
            aspect_ratio = w / h
            new_h = max_tile_height_px
            new_w = int(new_h * aspect_ratio)

            img = img.resize((new_w, new_h), PIL.Image.Resampling.LANCZOS)

            # Check if we need a new shelf (row)
            if cursor_x + new_w > A4_WIDTH:
                cursor_x = 0 + padding
                cursor_y += shelf_height + padding_y
                shelf_height = 0

            # Check if we need a new page
            if cursor_y + new_h > A4_HEIGHT:
                # Save current page
                page_idx = len(pages)
                page_path = os.path.join(output_dir, f"sheet_{alphabet_name}_{page_idx+1:03d}.png")
                current_page.save(page_path)
                pages.append(page_path)

                # Reset for new page
                current_page = PIL.Image.new(
                    "RGB", (A4_WIDTH, A4_HEIGHT), (255, 255, 255)
                )
                cursor_x = 0 + padding
                cursor_y = 0 + padding_y
                shelf_height = 0

            # Place image
            current_page.paste(img, (cursor_x, cursor_y))

            # Advance cursor
            cursor_x += new_w + padding
            shelf_height = max(shelf_height, new_h)

        # Save the last page
        if len(pages) == 0 or current_page != None:
            page_idx = len(pages)
            page_path = os.path.join(output_dir, f"sheet_{alphabet_name}_{page_idx+1:03d}.png")
            current_page.save(page_path)
            pages.append(page_path)

        print(f"Done! Generated {len(pages)} sheets in '{output_dir}/'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="letterarchitect-a4 - put character tiles on an A4 paper"
    )
    parser.add_argument("tiles_path", type=str, help="where the generated tiles are")
    parser.add_argument(
        "output_dir", type=str, help="where to save the generated A4 sheets"
    )
    args = parser.parse_args()

    generate_key(args.tiles_path, os.path.join(args.output_dir, "keys/"))
