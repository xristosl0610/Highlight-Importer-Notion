import csv
from src import BOOKSDIR
from src.notion_functions import (get_database_name, create_highlight, get_source_id_by_name,
                                  HIGHLIGHTS_DB_ID, LIBRARY_DB_ID, TEST_DB_ID)


def parse_csv_and_update_page_numbers(csv_filename: str) -> list[dict]:
    """
    Parse a CSV file containing book highlights and notes, updating page numbers
    and returning a list of dictionaries representing the parsed highlights.

    Args:
        csv_filename: The name of the CSV file containing book highlights and notes.

    Returns:
        list[dict]: A list of dictionaries representing the parsed highlights with keys 'page_number', 'highlight_text', and 'note_text'.
    """
    last_page_number = 0
    highlights = []
    with open(BOOKSDIR.joinpath(csv_filename), mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row_idx, row in enumerate(csv_reader):
            if row['page'].isdigit():
                page_number = int(row['page'])
                last_page_number = page_number
            else:
                last_page_number += 1
                page_number = last_page_number

            highlight_text = row['highlight_text']
            note_text = row.get('note_text')

            highlights.append({'page_number': page_number,
                               'highlight_text': highlight_text,
                               'note_text': note_text})

    return highlights


def process_highlights(highlights: list[dict], bookname_lib: str, test: bool) -> int:
    """
    Process a list of highlights by creating them in a specified book in the library.

    Args:
        highlights: A list of dictionaries representing the highlights to be processed.
        bookname_lib: The name of the book in the library to which the highlights belong.
        test: A flag indicating whether the processing is for testing purposes.

    Returns:
        int: The number of successfully added highlights.
    """
    return sum(bool(create_highlight(
        highlight['page_number'],
        highlight['highlight_text'],
        highlight['note_text'],
        bookname_lib,
        test=test,
    ))
               for highlight in highlights)


def main() -> None:
    """
    Main function to retrieve highlights from a CSV, add them to the highlights Notion database
    and link them with a specified book in the library Notion database.
    """
    csv_filename = input("Enter the CSV filename: ")
    bookname_lib = input("Enter the book name: ")

    highlight_db_name = get_database_name(HIGHLIGHTS_DB_ID)
    library_db_name = get_database_name(LIBRARY_DB_ID)
    test_db_name = get_database_name(TEST_DB_ID)

    print(f"\nSelected databases:")
    print(f"1. Highlights Database: {highlight_db_name}")
    print(f"2. Library Database: {library_db_name}")
    print(f"3. Test Database: {test_db_name}\n")

    use_test_db = input(f"Do you want to add highlights to the test database '{test_db_name}'? (yes/no): ").lower()
    test = use_test_db == 'yes'

    if not get_source_id_by_name(bookname_lib):
        print(f"Book '{bookname_lib}' not found in the library database.")
        return

    proceed = input(f"Are you sure you want to proceed with adding highlights to the '{bookname_lib}'? (yes/no): ").lower()
    if proceed != 'yes':
        print("Operation canceled.")
        return

    highlights = parse_csv_and_update_page_numbers(csv_filename)
    added_highlights = process_highlights(highlights, bookname_lib, test)

    print(f"\n{added_highlights} highlights were successfully added to '{test_db_name if test else highlight_db_name}'.")


if __name__ == '__main__':
    main()
