"""
title: FreshRSS Recent Articles
description: Fetches recent articles from FreshRSS to use as context in chat
author: immortalbob
version: 1.0.0
"""

import requests
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        FRESHRSS_URL: str = Field(
            default="http://freshrss",
            description="FreshRSS base URL (container name or IP)"
        )
        FRESHRSS_USER: str = Field(
            default="",
            description="FreshRSS username"
        )
        FRESHRSS_API_PASSWORD: str = Field(
            default="",
            description="FreshRSS API password (set in Profile → API password)"
        )
        MAX_ARTICLES: int = Field(
            default=10,
            description="Max number of recent articles to fetch"
        )

    def __init__(self):
        self.valves = self.Valves()

    def _get_auth_token(self) -> str | None:
        """Authenticate with FreshRSS GReader API and return token."""
        url = f"{self.valves.FRESHRSS_URL}/api/greader.php/accounts/ClientLogin"
        resp = requests.post(url, data={
            "Email": self.valves.FRESHRSS_USER,
            "Passwd": self.valves.FRESHRSS_API_PASSWORD,
        }, timeout=5)
        if resp.status_code != 200:
            return None
        for line in resp.text.splitlines():
            if line.startswith("Auth="):
                return line[5:]
        return None

    def get_recent_articles(self, count: int = None) -> str:
        """
        Fetch recent articles from FreshRSS.
        :param count: Number of articles to fetch (optional, uses default if not set)
        :return: Formatted list of recent articles with title, source, and summary
        """
        token = self._get_auth_token()
        if not token:
            return "Error: Could not authenticate with FreshRSS. Check your credentials in Valves."

        n = count or self.valves.MAX_ARTICLES
        url = f"{self.valves.FRESHRSS_URL}/api/greader.php/reader/api/0/stream/contents/reading-list"
        headers = {"Authorization": f"GoogleLogin auth={token}"}
        params = {"n": n, "output": "json"}

        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code != 200:
            return f"Error: FreshRSS returned {resp.status_code}"

        data = resp.json()
        items = data.get("items", [])
        if not items:
            return "No recent articles found in FreshRSS."

        results = []
        for item in items:
            title = item.get("title", "No title")
            source = item.get("origin", {}).get("title", "Unknown source")
            summary = item.get("summary", {}).get("content", "")
            # Strip basic HTML tags from summary
            import re
            summary = re.sub(r"<[^>]+>", "", summary)[:300].strip()
            results.append(f"**{title}** ({source})\n{summary}")

        return "\n\n---\n\n".join(results)