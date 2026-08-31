import requests
from bs4 import BeautifulSoup

BASE_URL = "https://secure.nsaahome.org/wildcards/schedules/index.php?sport=fb"

def main():
    response = requests.get(BASE_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h2")

    if title:
        print(f"Found page title: {title.get_text(strip=True)}")
    else:
        print("Page loaded but title not found")

if __name__ == "__main__":
    main()
``
