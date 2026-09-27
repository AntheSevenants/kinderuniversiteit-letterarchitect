import argparse
import os
from typing import List, Tuple

import PIL.Image
import pandas as pd

from letterarchitect_generate import get_character_path, load_image

def read_frequencies(frequencies_file: str):
    return pd.read_csv(frequencies_file, sep=";")

def get_tallies(df: pd.DataFrame, tiles_path: str) -> List[Tuple[str, PIL.Image.Image, int]]:
    basket = []

    for index, row in df.iterrows():
        letter = row["Letter"].lower().replace("/", "_")
        alphabets = ["Latin", "Greek", "Arabic", "Phoenician"]

        for alphabet in alphabets:
            needed_count = int(row[alphabet])
            if needed_count == 0:
                continue

            image_path = get_character_path(tiles_path, alphabet.lower(), letter)
            image = load_image(image_path)

            basket.append((letter, image, needed_count))

    return basket

def generate_tile_sheets(basket: List[Tuple[str, PIL.Image.Image, int]], output_dir: str, max_tile_height_px: int=500):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # A4 Dimensions at 300 DPI (standard for print)
    # 210mm x 297mm -> ~2480 x 3508 pixels
    A4_WIDTH = 2480
    A4_HEIGHT = 3508

    # Packing Logic (Shelf Packing Algorithm)
    pages = []
    current_page = PIL.Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 255, 255))

    padding = 175
    cursor_x = 0 + padding
    cursor_y = 0 + padding
    shelf_height = 0
    
    for letter, img, count in basket:
        for i in range(count):
            w, h = img.size
            aspect_ratio = w / h
            new_h = max_tile_height_px
            new_w = int(new_h * aspect_ratio)

            img = img.resize((new_w, new_h), PIL.Image.Resampling.LANCZOS)

            # Check if we need a new shelf (row)
            if cursor_x + new_w > A4_WIDTH:
                cursor_x = 0 + padding
                cursor_y += shelf_height
                shelf_height = 0

            # Check if we need a new page
            if cursor_y + new_h > A4_HEIGHT:
                # Save current page
                page_idx = len(pages)
                page_path = os.path.join(output_dir, f"sheet_{page_idx+1:03d}.png")
                current_page.save(page_path)
                pages.append(page_path)

                # Reset for new page
                current_page = PIL.Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 255, 255))
                cursor_x = 0 + padding
                cursor_y = 0 + padding
                shelf_height = 0

            # Place image
            current_page.paste(img, (cursor_x, cursor_y))

            # Advance cursor
            cursor_x += new_w
            shelf_height = max(shelf_height, new_h)

    # Save the last page
    if len(pages) == 0 or current_page != None:
        page_idx = len(pages)
        page_path = os.path.join(output_dir, f"sheet_{page_idx+1:03d}.png")
        current_page.save(page_path)
        pages.append(page_path)

    print(f"Done! Generated {len(pages)} sheets in '{output_dir}/'")
    return pages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="letterarchitect-a4 - put character tiles on an A4 paper"
    )
    parser.add_argument(
        "frequencies_file", type=str, help="path to the CSV with desired frequencies"
    )
    parser.add_argument(
        "tiles_path", type=str, help="where the generated tiles are"
    )
    parser.add_argument(
        "output_dir", type=str, help="where to save the generated A4 sheets"
    )
    args = parser.parse_args()

    df = read_frequencies(args.frequencies_file)
    basket = get_tallies(df, args.tiles_path)
    generate_tile_sheets(basket, os.path.join(args.output_dir, "sheets/"))
    