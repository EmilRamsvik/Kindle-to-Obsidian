import shutil
import subprocess

"""
This script automates the process of extracting, cleaning, and organizing quotes from Kindle clippings. 

It performs the following functions:
1. Copies the 'My Clippings.txt' file from a connected Kindle device to a local directory and safely ejects the Kindle.
2. Extracts quotes from the copied file, organizing them by author or source.
3. Cleans up the quotes by removing unwanted characters and formatting issues.
4. Filters out redundant quotes based on the similarity of their starting words.
5. Writes the cleaned and filtered quotes to individual text files, organized by author or source.

The script is designed for those who wish to digitalize and manage their Kindle clippings efficiently, 
making it easier to access, share, and reference important quotes.

Usage:
Run the script with a connected Kindle device. The script will create text files for each author/source
in a specified directory, containing all the relevant quotes.

Note:
- Ensure that the Kindle device is properly connected before running the script.
- Modify the 'notes' directory path as needed to suit your file organization preferences.
"""


def copy_clippings_file():
    src_file = "/Volumes/Kindle/documents/My Clippings.txt"
    dst_file = "kindle_notes.txt"
    try:
        shutil.copy(src_file, dst_file)
        subprocess.call(
            ["osascript", "-e", 'tell application "Finder" to eject "Kindle"']
        )
        print("Copied clippings file from Kindle and ejected Kindle")
    except:
        print("Kindle not connected")
    return dst_file


def extract_quotes_from_file(filename):
    with open(filename, "r") as f:
        entries = f.read().split("==========\n")
        quotes_by_author = {}
        for entry in entries:
            if entry.strip() == "":
                continue
            lines = entry.strip().split("\n")
            header = lines[0]
            try:
                key = header.split("-")[1].strip()
                key = key.split("_")[0].strip()
            except:
                key = header
            quote = lines[-1].strip()
            if key not in quotes_by_author:
                quotes_by_author[key] = [quote]
            else:
                quotes_by_author[key].append(quote)
        return quotes_by_author


import os


def write_quotes_to_file(key, quotes):
    quotes = remove_quotes_with_similar_first_words(quotes, 5)
    quotes = [clean_quote_special_characters(quote) for quote in quotes]
    filename = key + ".txt"
    notes_dir = "notes"  # set notes directory here
    if os.path.exists(os.path.join(notes_dir, filename)):
        pass
    else:
        with open(filename, "w") as f:
            for quote in quotes:
                f.write("- *" + quote + "* \n \n")
        print(f"Wrote quotes to file '{filename}'")


def clean_quote_special_characters(quote):
    """removes () [] {} from quote"""
    if quote[0] == "(":
        quote = quote[1:]
    if quote[-1] == ")":
        quote = quote[:-1]
    quote = quote.replace("[", "\\[")
    quote = quote.replace("]", "\\]")
    quote = quote.replace("{", "\\{")
    quote = quote.replace("}", "\\}")

    # make the first letter uppercase
    quote = quote[0].upper() + quote[1:]

    return quote


def write_all_quotes(quotelist):
    for key, quotes in quotelist.items():
        write_quotes_to_file(key, quotes)


def remove_quotes_with_similar_first_words(quotes, n=5):
    last_words = ""
    for quote in quotes:
        # split quote into words
        words = quote.split(" ")
        # get first n words
        first_n_words = " ".join(words[:n])
        # if the first n words are the same as the last quote, then remove the quote
        if first_n_words == last_words:
            quotes.remove(last_quote)
        last_words = first_n_words
        last_quote = quote
    return quotes


def save_quotes_by_book():
    clippings_file = copy_clippings_file()
    quotes = extract_quotes_from_file(clippings_file)
    write_all_quotes(quotelist=quotes)


if __name__ == "__main__":
    save_quotes_by_book()
