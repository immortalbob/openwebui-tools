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
*(Coming soon)* Search your local [Kiwix](https://www.kiwix.org/) ZIM library (Wikipedia, Stack Exchange, etc.) and return relevant content as context.

**File:** `kiwix_openwebui_tool.py`

---

## Installation

1. In Open WebUI, go to **Workspace → Tools → New Tool**
2. Paste the contents of the tool file
3. Save, then click the ⚙️ Valves icon to configure your service URLs and credentials
4. Add the tool to your model under **Workspace → Models**

## Network Notes

These tools are written assuming Open WebUI and your self-hosted services share a Docker network (e.g. `ai-net`). If that's the case, you can use container names as hostnames (`http://freshrss`, `http://kiwix`, etc.) instead of IP addresses.

If your services are on separate hosts, just set the Valve URL to the LAN IP and port instead.

## Philosophy

Local-first, privacy-preserving, subscription-free. These tools are designed for homelabs where the data stays home. No telemetry, no external calls, no surprises.

## Contributing

PRs welcome. If you've built a tool for another self-hosted service and want to add it here, open an issue or submit a pull request.
