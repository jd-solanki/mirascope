from mirascope.core import anthropic, prompt_template


def get_book_author(title: str) -> str:
    """Returns the author of the book with the given title

    Args:
        title: The title of the book.
    """
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


@anthropic.call("claude-3-5-sonnet-20240620", tools=[get_book_author])
@prompt_template("Who wrote {book}?")
def identify_author(book: str): ...


response = identify_author("The Name of the Wind")
if tool := response.tool:
    print(tool.call())
    # Output: Patrick Rothfuss
    print(f"Original tool call: {tool.tool_call}")
else:
    print(response.content)