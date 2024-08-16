import csv
from notion_client import Client
from notion_client.errors import APIResponseError

from src import BOOKSDIR

NOTION = Client(auth="PASTE_TOKEN")

DATABASE_ID = "be26fd1c20214740b04879bbf74f04f4"
SOURCE_DATABASE_ID = "35c3f1c6f4e24a809127c5cab9637b5f"


def get_source_id_by_name(source_name: str) -> str | None:
    """
    Retrieves the ID of a source by its name from a Notion database.

    Args:
        source_name: The name of the source to search for.

    Returns:
        str | None: The ID of the source if found, None if not found or an error occurs.
    """
    try:
        response = NOTION.databases.query(
            database_id=SOURCE_DATABASE_ID,
            filter={
                "property": "Name",  # Assuming the title of the book is stored under the "Name" property
                "title": {
                    "equals": source_name
                }
            }
        )
        if response["results"]:
            return response["results"][0]["id"]
        print(f"No source found with the name '{source_name}'")
        return None
    except APIResponseError as e:
        print(f"An error occurred: {e}")
        return None


def create_highlight(page_number: int, highlight_text: str, note_text: str | None = None,
                     source_name: str | None = None, favorite: bool = False) -> None:
    """
    Creates a highlight in a Notion database with optional note, source, and favorite status.

    Args:
        page_number: The page number where the highlight is from.
        highlight_text: The text content of the highlight.
        note_text: Optional text for additional notes (default is None).
        source_name: Optional name of the source for the highlight (default is None).
        favorite: Flag indicating if the highlight is a favorite (default is False).

    Returns:
        None
    """
    children_blocks = [
        {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": highlight_text,
                        },
                        "annotations": {
                            "italic": True,
                        },
                    }
                ],
            }
        }
    ]

    if note_text:
        children_blocks.extend(
            (
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Note",
                                },
                            }
                        ],
                    },
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": note_text,
                                },
                            }
                        ],
                    },
                },
            )
        )
    properties = {
        "Page": {"number": page_number},
        "Favorite": {"checkbox": favorite},
    }

    if source_name:
        if source_id := get_source_id_by_name(source_name):
            properties["Source"] = {
                "relation": [{"id": source_id}]
            }

    try:
        NOTION.pages.create(
            parent={"database_id": DATABASE_ID},
            properties=properties,
            children=children_blocks
        )
    except APIResponseError as e:
        print(f"An error occurred while creating the highlight: {e}")


SOURCE_NAME = 'The Art of Communicating'
CSV_NAME = 'the_art_of_communicating_thich_nhat_hanh_clippings_2024-8-15.csv'
last_page_number = 0

with open(BOOKSDIR.joinpath(CSV_NAME), mode='r', encoding='utf-8') as file:
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

        create_highlight(page_number, highlight_text, note_text, SOURCE_NAME)
