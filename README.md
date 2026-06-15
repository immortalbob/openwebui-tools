# openwebui-tools

Self-hosted Open WebUI tools for a local-first homelab stack. No cloud dependencies, no API keys you don't own. Drop these into Workspace → Tools and point the Valves at your own services.

## Tools

### 🗞️ FreshRSS — Recent Articles
Fetches recent articles from your [FreshRSS](https://freshrss.github.io/FreshRSS/) instance via the GReader API and injects them as context into chat.

**File:** `freshrss_recent_articles.py`

| Valve | Description | Default |
|-------|-------------|---------|
| `FRESHRSS_URL` | Base URL of your FreshRSS instance | `http://freshrss` |
| `FRESHRSS_USER` | FreshRSS username | |
| `FRESHRSS_API_PASSWORD` | API password (set in Profile → API password) | |
| `MAX_ARTICLES` | Max articles to fetch per call | `10` |

**Prerequisites:**
- FreshRSS running and reachable from Open WebUI
- API access enabled: **Administration → Authentication → Allow API access**
- API password set: **Profile → API password**

---

### 📚 Kiwix — Offline Knowledge Base
Search your local [Kiwix](https://www.kiwix.org/) ZIM library and return article content as context. Supports Wikipedia, Stack Exchange, iFixit, FreeCodeCamp, DevDocs, and more. Keyword routing automatically selects the most relevant ZIM for a given query, with Wikipedia as the default fallback.

**File:** `kiwix_search.py`

| Setting | Description | Default |
|---------|-------------|---------|
| `kiwix_url` | Base URL of your Kiwix instance | `http://kiwix:8080` |

> **Note:** `kiwix_url` is hardcoded in `__init__` rather than a Valve. Edit it directly if your Kiwix container name or port differs. If Open WebUI and Kiwix share a Docker network, use the container name (e.g. `http://kiwix:8080`). Otherwise use the LAN IP and port (e.g. `http://192.168.3.5:8081`).

**Exposes two callable functions:**

- **`search_kiwix`** — returns a list of matching results with titles, excerpts, and URLs. Good for "what's available on X."
- **`search_and_fetch`** — searches and pulls full article text from the top result. Good for "tell me about X."

Both accept an `all_books` parameter — if `True`, the tool searches up to 5 of the most relevant ZIMs and deduplicates results.

**Prerequisites:**
- Kiwix running with at least one ZIM loaded
- Kiwix container on the same Docker network as Open WebUI (e.g. `ai-net`)
- Kiwix internal port is `8080` (mapped to whatever host port you prefer)

**Keyword routing:**
The tool scores ZIMs against the query using a keyword map and searches the highest-scoring book first. Unmatched queries fall back to Wikipedia. The keyword map covers: Raspberry Pi, ESP32, Arduino, Docker, nginx, bash, Python, machine learning, mathematics, retrocomputing, iFixit repairs, and more. Edit `keyword_mapping` in `__init__` to add your own ZIMs.

---

## Installation

1. In Open WebUI, go to **Workspace → Tools → New Tool**
2. Paste the contents of the tool file
3. Save, then click the ⚙️ Valves icon to configure your service URLs and credentials
4. Add the tool to your model under **Workspace → Models**

## Network Notes

These tools are written assuming Open WebUI and your self-hosted services share a Docker network (e.g. `ai-net`). If that's the case, you can use container names as hostnames (`http://freshrss`, `http://kiwix:8080`, etc.) instead of IP addresses.

If your services are on separate hosts, just set the URL to the LAN IP and port instead.

## Philosophy

Local-first, privacy-preserving, subscription-free. These tools are designed for homelabs where the data stays home. No telemetry, no external calls, no surprises.

## Contributing

PRs welcome. If you've built a tool for another self-hosted service and want to add it here, open an issue or submit a pull request. Combo detection left as an exercise for the reader.
