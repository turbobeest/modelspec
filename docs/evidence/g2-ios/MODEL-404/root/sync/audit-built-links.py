"""Audit merged guide/navigation routes without changing their output."""
from html.parser import HTMLParser
from pathlib import Path


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.extend(value for key, value in attrs if key == "href" and value)


tree = Path("dist/modelspec")
assert (tree / "decide/index.html").is_file()
assert (tree / "decide/details/index.html").is_file()
for directory in ("guides", "compare", "use-cases"):
    pages = sorted((tree / directory).rglob("index.html"))
    assert pages, directory
    actions = 0
    for path in pages:
        links = Links()
        links.feed(path.read_text())
        assert "/decide/" in links.hrefs, path
        assert not any(href.startswith("/decide/?template=") for href in links.hrefs), path
        actions += sum(href.startswith("/decide/details/?template=") for href in links.hrefs)
    assert actions, directory
    print(f"{directory}: {len(pages)} pages retain simple Decide links; {actions} detailed template actions")
print("Both Decide routes are present.")
