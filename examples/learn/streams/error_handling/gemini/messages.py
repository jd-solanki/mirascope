from mirascope.core import Messages, gemini


@gemini.call("gemini-1.5-flash", stream=True)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except Exception as e:
    print(f"Error: {str(e)}")