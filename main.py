import csv
from src import BOOKSDIR
from src.notion_functions import create_highlight


def main(csv_filename: str, bookname_lib: str, test: bool = True) -> None:
    """
    Process a CSV file containing book highlights and notes, updating page numbers and creating highlights in a specified book in the library.

    Args:
        csv_filename: The name of the CSV file containing book highlights and notes.
        bookname_lib: The name of the book (to which the highlight belongs) in the Notion library databse.
        test: Flag indicating if the function call is a test (default is True).
    Returns:
        None
    """
    last_page_number = 0
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

            create_highlight(page_number, highlight_text, note_text, bookname_lib, test=test)


if __name__ == '__main__':
    bookname = 'Deep Work: Rules for Focused Success in a Distracted World'
    csv_name = 'deep_work_cal_newport_TEST.csv'

    main(csv_name, bookname, test=True)
