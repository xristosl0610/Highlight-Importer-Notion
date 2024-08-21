import os
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

load_dotenv()

NOTION = Client(auth=os.getenv("NOTION_AUTH"))
HIGHLIGHTS_DB_ID = os.getenv("HIGHLIGHTS_DB_ID")
LIBRARY_DB_ID = os.getenv("LIBRARY_DB_ID")
TEST_DB_ID = os.getenv("TEST_DB_ID")


def get_database_name(database_id: str) -> str | None:
    """
    Retrieves the name of a Notion database by its ID.

    Args:
        database_id: The ID of the database.

    Returns:
        str | None: The name of the database if found, None if an error occurs.
    """
    try:
        database = NOTION.databases.retrieve(database_id=database_id)
        return database['title'][0]['text']['content']
    except APIResponseError as e:
        print(f"An error occurred while retrieving the database name: {e}")
        return None


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
            database_id=LIBRARY_DB_ID,
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
                     source_name: str | None = None, favorite: bool = False, test: bool = True) -> bool:
    """
    Creates a highlight in a Notion database with optional note, source, and favorite status.

    Args:
        page_number: The page number where the highlight is from.
        highlight_text: The text content of the highlight.
        note_text: Optional text for additional notes (default is None).
        source_name: Optional name of the source for the highlight (default is None).
        favorite: Flag indicating if the highlight is a favorite (default is False).
        test: Flag indicating if the function call is a test (default is True).

    Returns:
        bool: True if the highlight was successfully created, False otherwise.
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
            parent={"database_id": TEST_DB_ID if test else HIGHLIGHTS_DB_ID},
            properties=properties,
            children=children_blocks
        )
        return True
    except APIResponseError as e:
        print(f"An error occurred while creating the highlight: {e}")
        return False
