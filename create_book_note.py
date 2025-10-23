import os
import re
import shutil
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from openrouter_api import agent, BookReview


def clean_title(title: str) -> str:
    # Remove all special characters as well as what is inside a parenthesis, brackets, etc.
    # Myth of Sisyphus and Other Essays (Albert Camus).txt -> Myth of Sisyphus and Other Essays

    # Remove .txt extension
    title = title.replace(".txt", "")

    # Remove content in parentheses, brackets, etc.
    title = re.sub(r"\([^)]*\)", "", title)
    title = re.sub(r"\[[^\]]*\]", "", title)
    title = re.sub(r"\{[^}]*\}", "", title)

    # Clean up extra spaces
    title = re.sub(r"\s+", " ", title).strip()

    return title


def create_book_note(quotes: str, title: str, book_review: BookReview = None) -> str:
    """create a book note by importing the template.md file and using {{title}} and {{quotes}} to replace the placeholders
    also add the date.
    """
    # Read the template file
    with open("template.md", "r", encoding="utf-8") as f:
        template = f.read()

    # Get current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Replace placeholders
    note = template.replace("{{ title }}", title)
    note = note.replace("{{ quotes }}", quotes)
    note = note.replace("{{created_time}}", current_time)
    note = note.replace("{{updated_time}}", current_time)

    if book_review:
        note = note.replace("{{ summary }}", book_review.summary)
        note = note.replace("{{ impressions }}", book_review.impressions)
        tags_multiline = "\n  ".join(book_review.tags)
        note = note.replace("{{ tags }}", tags_multiline)
    else:
        note = note.replace("{{ summary }}", quotes)
        note = note.replace("{{ impressions }}", quotes)
        note = note.replace("{{ tags }}", "")

    return note


def read_quotes_file(file_path: str) -> str:
    """Read quotes from a text file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_to_obsidian(file_path: str) -> None:
    """write the note to the obsidian vault with name of the book"""
    # read contents of the file:
    quotes = read_quotes_file(file_path)

    filename = os.path.basename(file_path)
    title = clean_title(filename)
    note = create_book_note(quotes, title)

    obsidian_path = os.getenv("OBSIDIAN_PATH")
    if not obsidian_path:
        raise ValueError("OBSIDIAN_PATH environment variable not set")

    output_path = os.path.join(obsidian_path, f"{title}.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(note)

    print(f"Created note: {output_path}")


def move_to_parsed(file_path: str) -> None:
    """Move file from unparsed_notes to parsed_notes after successful processing"""
    filename = os.path.basename(file_path)
    parsed_notes_dir = "parsed_notes"

    # Create parsed_notes directory if it doesn't exist
    os.makedirs(parsed_notes_dir, exist_ok=True)

    destination = os.path.join(parsed_notes_dir, filename)
    shutil.move(file_path, destination)
    print(f"Moved {filename} to parsed_notes/")


async def process_all_unparsed_notes():
    """Process all text files in the unparsed_notes folder with interactive confirmation"""
    unparsed_notes_dir = "unparsed_notes"

    txt_files = sorted(
        [f for f in os.listdir(unparsed_notes_dir) if f.endswith(".txt")]
    )

    if not txt_files:
        print("No unparsed files found!")
        return

    print(f"Found {len(txt_files)} files to process\n")

    # Ask if user wants to use LLM
    use_llm_input = (
        input("Do you want to use LLM for processing? (y/n): ").strip().lower()
    )
    use_llm = use_llm_input == "y"

    print(f"\nUsing {'LLM' if use_llm else 'direct template'} processing\n")
    print("-" * 60)

    processed_count = 0
    skipped_count = 0

    for filename in txt_files:
        file_path = os.path.join(unparsed_notes_dir, filename)
        title = clean_title(filename)

        print(f"\nFile: {filename}")
        print(f"Title: {title}")

        # Interactive confirmation
        user_input = input("Parse this file? (y/n): ").strip().lower()

        if user_input != "y":
            print(f"Skipped {filename}")
            skipped_count += 1
            print("-" * 60)
            continue

        try:
            if use_llm:
                await process_book_with_llm(file_path)
            else:
                write_to_obsidian(file_path)

            # Move to parsed_notes after successful processing
            #move_to_parsed(file_path)
            processed_count += 1
            print(f"Successfully processed {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")



async def process_book_with_llm(file_path):
    quotes = read_quotes_file(file_path)
    title = clean_title(os.path.basename(file_path))
    book_review = await agent.run(f" Title: {title} \n Quotes: {quotes}")

    note = create_book_note(quotes, title, book_review.output)

    obsidian_path = os.getenv("OBSIDIAN_PATH")
    if not obsidian_path:
        raise ValueError("OBSIDIAN_PATH environment variable not set")

    output_path = os.path.join(obsidian_path, f"{title}.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(note)

    print(f"Created note: {output_path}")


if __name__ == "__main__":
    asyncio.run(process_all_unparsed_notes())
