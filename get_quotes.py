#!/usr/bin/env python3

import shutil
import subprocess
import os


def copy_clippings_file():
    src_file = "/Volumes/Kindle/documents/My Clippings.txt"
    dst_file = "kindle_notes.txt"
    try:
        shutil.copy(src_file, dst_file)
        subprocess.call(
            ["osascript", "-e", 'tell application "Finder" to eject "Kindle"']
        )
        print("Copied clippings file from Kindle and ejected Kindle")
    except Exception as e:
        print("Kindle not connected")
        print("Error:", e)
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
            except Exception as e:
                print(f"Error parsing header: {header} in {filename} with error: {e}")
                key = header
            quote = lines[-1].strip()
            if key not in quotes_by_author:
                quotes_by_author[key] = [quote]
            else:
                quotes_by_author[key].append(quote)
        return quotes_by_author



def write_quotes_to_file(key, quotes):
    quotes = remove_quotes_with_similar_first_words(quotes, 5)
    quotes = [clean_quote_special_characters(quote) for quote in quotes]
    filename = key + ".txt"
    parsed_notes_path = "parsed_notes/"
    if filename in os.listdir(parsed_notes_path):
        pass
    else:
        with open(filename, "w") as f:
            for quote in quotes:
                f.write("- " + quote + " \n \n")
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
    last_quote = ""
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
