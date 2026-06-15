"""
Kiwix Search Tool for Open WebUI
Searches a self-hosted Kiwix server across offline ZIM libraries.

Install in Open WebUI: Workspace → Tools → Create Tool
Paste this file contents into the tool editor and save.

Requires: requests, beautifulsoup4 (available in Open WebUI's environment)
"""

import requests
from bs4 import BeautifulSoup


class Tools:
    def __init__(self):
        self.kiwix_url = "http://192.168.3.5:8081"
        self.default_book = "wikipedia_en_all_maxi_2026-02"
        self.books = [
            "ai.stackexchange.com_en_all_2026-02",
            "arduino.stackexchange.com_en_all_2026-02",
            "cs.stackexchange.com_en_all_2026-02",
            "datascience.stackexchange.com_en_all_2026-02",
            "dba.stackexchange.com_en_all_2026-02",
            "devdocs_en_nginx_2026-04",
            "devdocs_en_python_2026-05",
            "devops.stackexchange.com_en_all_2026-02",
            "electronics.stackexchange.com_en_all_2026-02",
            "freecodecamp_en_all_2026-05",
            "ifixit_en_all_2025-12",
            "iot.stackexchange.com_en_all_2026-02",
            "math.stackexchange.com_en_all_2026-02",
            "raspberrypi.stackexchange.com_en_all_2026-02",
            "unix.stackexchange.com_en_all_2026-02",
            "wikipedia_en_all_maxi_2026-02",
            "wiktionary_en_all_nopic_2025-09"
        ]
        self.keyword_mapping = {
            "raspberry pi": ["raspberrypi.stackexchange.com_en_all_2026-02", "ifixit_en_all_2025-12"],
            "esp32": ["iot.stackexchange.com_en_all_2026-02", "electronics.stackexchange.com_en_all_2026-02"],
            "gpio": ["raspberrypi.stackexchange.com_en_all_2026-02", "electronics.stackexchange.com_en_all_2026-02"],
            "arduino": ["arduino.stackexchange.com_en_all_2026-02", "electronics.stackexchange.com_en_all_2026-02"],
            "docker": ["devops.stackexchange.com_en_all_2026-02", "unix.stackexchange.com_en_all_2026-02"],
            "nginx": ["devdocs_en_nginx_2026-04", "unix.stackexchange.com_en_all_2026-02"],
            "bash": ["unix.stackexchange.com_en_all_2026-02"],
            "unix": ["unix.stackexchange.com_en_all_2026-02"],
            "python": ["devdocs_en_python_2026-05", "freecodecamp_en_all_2026-05", "cs.stackexchange.com_en_all_2026-02"],
            "coding": ["freecodecamp_en_all_2026-05", "cs.stackexchange.com_en_all_2026-02"],
            "algorithm": ["cs.stackexchange.com_en_all_2026-02", "datascience.stackexchange.com_en_all_2026-02"],
            "machine learning": ["ai.stackexchange.com_en_all_2026-02"],
            "artificial intelligence": ["ai.stackexchange.com_en_all_2026-02"],
            "data science": ["datascience.stackexchange.com_en_all_2026-02"],
            "web": ["freecodecamp_en_all_2026-05", "devdocs_en_python_2026-05"],
            "wiki": ["wikipedia_en_all_maxi_2026-02"],
        }

    def _get_relevant_books(self, query: str) -> list:
        query_lower = query.lower()
        book_scores = {}
        matched_books = set()
        for keyword, relevant_books in self.keyword_mapping.items():
            if keyword in query_lower:
                for book in relevant_books:
                    book_scores[book] = book_scores.get(book, 0) + 1
                    matched_books.add(book)
        prioritized = [b for b, _ in sorted(book_scores.items(), key=lambda x: x[1], reverse=True)]
        prioritized += [b for b in self.books if b not in matched_books]
        return prioritized

    def _search_book(self, query: str, book: str, limit: int = 3) -> list:
        try:
            response = requests.get(
                f"{self.kiwix_url}/search",
                params={"pattern": query, "books.name": book, "limit": limit},
                timeout=5
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            results_div = soup.find("div", class_="results")
            if not results_div:
                return []
            results = []
            for item in results_div.find_all("li"):
                a_tag = item.find("a")
                cite_tag = item.find("cite")
                if not a_tag:
                    continue
                url = f"{self.kiwix_url}{a_tag.get('href', '')}"
                # Skip tag index pages — they are low-signal aggregate pages
                if "/questions/tagged/" in url:
                    continue
                results.append({
                    "title": a_tag.get_text(strip=True),
                    "excerpt": cite_tag.get_text(strip=True) if cite_tag else "",
                    "url": url,
                    "book": book
                })
            return results
        except Exception:
            return []

    def search_kiwix(self, query: str, all_books: bool = False) -> str:
        """
        Search the local Kiwix offline knowledge base for information.
        Use this when you need factual information from Wikipedia, Stack Exchange,
        iFixit, FreeCodeCamp, or other offline reference libraries.

        :param query: The search query string
        :param all_books: If True, search all configured books with relevance weighting. If False, search the most relevant book only.
        :return: Search results as formatted text
        """
        if all_books:
            books_to_search = self._get_relevant_books(query)[:5]
            all_results = []
            seen = set()
            for book in books_to_search:
                for r in self._search_book(query, book, limit=3):
                    if r["url"] not in seen:
                        seen.add(r["url"])
                        all_results.append(r)
            results = all_results[:10]
        else:
            book = self._get_relevant_books(query)[0]
            results = self._search_book(query, book, limit=5)

        if not results:
            return "No results found in Kiwix knowledge base."

        output = []
        for i, r in enumerate(results, 1):
            output.append(f"{i}. **{r['title']}** (from {r['book']})\n   {r['excerpt']}\n   {r['url']}")
        return "\n\n".join(output)
