import csv
from notion_client import Client
from notion_client.errors import APIResponseError

NOTION = Client(auth="secret_V2HSKyo1MEsHpTwAgjeIesOVZJdIluqFJz7S45piOi2")

DATABASE_ID = "be26fd1c20214740b04879bbf74f04f4"
SOURCE_DATABASE_ID = "35c3f1c6f4e24a809127c5cab9637b5f"


def get_source_id_by_name(source_name):
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
        else:
            print(f"No source found with the name '{source_name}'")
            return None
    except APIResponseError as e:
        print(f"An error occurred: {e}")
        return None


def create_highlight(page_number, highlight_text, note_text=None, source_name=None, favorite=False):
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

    # Add a note as a heading if note_text exists
    if note_text:
        children_blocks.append(
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
            }
        )
        children_blocks.append(
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
                }
            }
        )

    properties = {
        "Page": {"number": page_number},
        "Favorite": {"checkbox": favorite},
    }

    if source_name:
        source_id = get_source_id_by_name(source_name)
        if source_id:
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

last_page_number = 0

with open('books/the_art_of_communicating_thich_nhat_hanh_clippings_2024-8-15.csv', mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row_idx, row in enumerate(csv_reader):
        if row['page'].isdigit():
            page_number = int(row['page'])
            last_page_number = page_number  # Update last_page_number to keep it in sync
        else:
            last_page_number += 1
            page_number = last_page_number

        highlight_text = row['highlight_text']
        note_text = row.get('note_text')  # Get the note_text column value

        create_highlight(page_number, highlight_text, note_text, SOURCE_NAME)
