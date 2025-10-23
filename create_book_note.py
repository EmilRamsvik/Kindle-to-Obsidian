import os
import re
from datetime import datetime




def clean_title(title: str) -> str:
    # Remove all special characters as well as what is inside a parenthesis, brackets, etc.
    # Myth of Sisyphus and Other Essays (Albert Camus).txt -> Myth of Sisyphus and Other Essays
    
    # Remove .txt extension
    title = title.replace('.txt', '')
    
    # Remove content in parentheses, brackets, etc.
    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^\]]*\]', '', title)
    title = re.sub(r'\{[^}]*\}', '', title)
    
    # Clean up extra spaces
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title




def create_book_note(quotes: str, title: str) -> str:
    """ create a book note by importing the template.md file and using {{title}} and {{quotes}} to replace the placeholders
    also add the date.  

    """
    # Read the template file
    with open('template.md', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Get current timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Replace placeholders
    note = template.replace('{{ title }}', title)
    note = note.replace('{{ quotes }}', quotes)
    note = note.replace('{{created_time}}', current_time)
    note = note.replace('{{updated_time}}', current_time)
    
    return note




def read_quotes_file(file_path: str) -> str:
    """ Read quotes from a text file """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_to_obsidian(file_path: str) -> None:
    """ write the note to the obsidian vault with name of the book """
    # read contents of the file:
    quotes = read_quotes_file(file_path)
    
    filename = os.path.basename(file_path)
    title = clean_title(filename)
    note = create_book_note(quotes, title)
    
    # obsidian_path = os.getenv('OBSIDIAN_PATH')
    # if not obsidian_path:
    #     raise ValueError("OBSIDIAN_PATH environment variable not set")
    obsidian_path = 'tmp'
    
    output_path = os.path.join(obsidian_path, f"{title}.md")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(note)
    
    print(f"Created note: {output_path}")


def process_all_unparsed_notes():
    """ Process all text files in the unparsed_notes folder """
    unparsed_notes_dir = 'unparsed_notes'
    
    txt_files = [f for f in os.listdir(unparsed_notes_dir) if f.endswith('.txt')]
    
    
    print(f"Found {len(txt_files)} files to process")
    
    for filename in txt_files:
        file_path = os.path.join(unparsed_notes_dir, filename)
        try:
            write_to_obsidian(file_path)
        except Exception as e:
            print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    process_all_unparsed_notes()
