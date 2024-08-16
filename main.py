import csv
from src import BOOKSDIR
from src.notion_functions import create_highlight


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


def process_highlights(highlights: list[dict], bookname_lib: str, test: bool) -> None:
    """
    Process a list of highlights by creating them in a specified book in the library.

    Args:
        highlights: A list of dictionaries representing the highlights to be processed.
        bookname_lib: The name of the book in the library to which the highlights belong.
        test: A flag indicating whether the processing is for testing purposes.

    Returns:
        None
    """
    for highlight in highlights:
        create_highlight(highlight['page_number'],
                         highlight['highlight_text'],
                         highlight['note_text'],
                         bookname_lib, test=test)


def main(csv_filename: str, bookname_lib: str, test: bool = True) -> None:
    """
    Retrieve highlights from a csv, add them to the highlights Notion database (or test one)
    and link them with a specified book in the library Notion database.

    Args:
        csv_filename: The name of the CSV file containing book highlights and notes.
        bookname_lib: The name of the book (to which the highlight belongs) in the Notion library databse.
        test: Flag indicating if the function call is a test (default is True).
    Returns:
        None
    """
    highlights = parse_csv_and_update_page_numbers(csv_filename)
    process_highlights(highlights, bookname_lib, test)


if __name__ == '__main__':
    bookname = 'Deep Work: Rules for Focused Success in a Distracted World'
    csv_name = 'deep_work_cal_newport_TEST.csv'

    main(csv_name, bookname, test=True)
