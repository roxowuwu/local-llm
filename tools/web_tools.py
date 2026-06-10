import subprocess
import webbrowser


# -----------------------------
# OPEN URL
# -----------------------------
def open_url(params, prefs):
    url = params.get("url")

    if not url:
        raise ValueError("No URL provided")

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("Invalid URL format")

    browser = prefs.get("browser")

    try:
        if browser:
            subprocess.Popen([browser, url])
        else:
            raise Exception("No browser in prefs")

    except Exception:
        webbrowser.open(url)

    return f"Opened: {url}"


# -----------------------------
# WEB SEARCH
# -----------------------------
def web_search(params, prefs):
    query = params.get("query")

    if not query:
        raise ValueError("No search query provided")

    engine = prefs.get("preferred_search", "google").lower()

    if engine == "google":
        url = f"https://google.com/search?q={query}"
    elif engine == "bing":
        url = f"https://bing.com/search?q={query}"
    elif engine == "ddg":
        url = f"https://duckduckgo.com/?q={query}"
    else:
        url = f"https://google.com/search?q={query}"

    # reuse open_url
    open_url({"url": url}, prefs)

    return f"Searched for: {query}"
