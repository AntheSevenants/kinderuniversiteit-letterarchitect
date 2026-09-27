import argparse
import csv
import unicodedata
import sys
import os

def normalise_text(text):
    # Normalise to decomposed form (NFD) to separate characters from their accents
    text = unicodedata.normalize('NFD', text)
    # Filter out non-spacing mark characters (the accents) and keep only lowercase letters
    # We also filter out spaces and punctuation to focus only on letters
    text = "".join(
        char.lower() for char in text 
        if unicodedata.category(char) != 'Mn' and char.isalpha()
    )
    return text

def process_names(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"'{input_file}' does not exist")
        return

    frequencies = {}

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = normalise_text(line)
            for char in clean_line:
                frequencies[char] = frequencies.get(char, 0) + 1

    # Sort by frequency (descending) and then alphabetically
    sorted_freq = sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Letter', 'Frequency'])
        writer.writerows(sorted_freq)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="letterarchitect-name-analysis - how many latters do we need?"
    )
    parser.add_argument(
        "input_file", type=str, help="name list to analyse - one name per line"
    )
    parser.add_argument(
        "output_file", type=str, help="CSV with frequencies"
    )
    args = parser.parse_args()

    process_names(args.input_file, args.output_file)