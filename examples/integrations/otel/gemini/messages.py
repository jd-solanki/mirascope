from mirascope.core import Messages, gemini
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@gemini.call("gemini-1.5-flash")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))