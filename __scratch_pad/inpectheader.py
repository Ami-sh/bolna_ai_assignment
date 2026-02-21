import requests

def print_feed_headers(url: str):
    """
    Fetches the feed headers only and prints them.
    """
    try:
        # Use HEAD to only get headers if server supports it
        resp = requests.head(url)
        if resp.status_code == 405:  # Some servers don't allow HEAD
            # fallback to GET but don't parse content
            resp = requests.get(url, stream=True)
            resp.close()  # we just want headers

        print(f"HTTP Status: {resp.status_code}\n")
        print("Headers:")
        for k, v in resp.headers.items():
            print(f"{k}: {v}")

    except Exception as e:
        print(f"Error fetching headers: {e}")

# Example usage:
print_feed_headers("https://status.openai.com/feed.atom")
print_feed_headers("https://status.openai.com/feed.rss")