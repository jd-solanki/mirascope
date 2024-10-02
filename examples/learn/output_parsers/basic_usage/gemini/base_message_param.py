from mirascope.core import BaseMessageParam, gemini


def parse_recommendation(response: gemini.GeminiCallResponse) -> tuple[str, str]:
    title, author = response.content.split(" by ")
    return (title, author)


@gemini.call("gemini-1.5-flash", output_parser=parse_recommendation)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=f"Recommend a {genre} book. Output only Title by Author",
        )
    ]


print(recommend_book("fantasy"))
# Output: ('"The Name of the Wind"', 'Patrick Rothfuss')
