from langchain_community.tools import DuckDuckGoSearchRun

_search = DuckDuckGoSearchRun()


def web_search(query: str) -> str:
    """Cari informasi terbaru dari internet via DuckDuckGo."""
    try:
        return _search.invoke(query)
    except Exception as e:
        return f"Web search gagal: {str(e)}"
