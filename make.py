#!/usr/bin/env python3

import html
import os
import re
import sys


def inline(text):
    text = html.escape(text)

    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)

    return text


def markdown_to_html(lines):
    out = []
    in_ul = False
    in_code = False

    for line in lines:
        line = line.rstrip()

        if line.startswith("```"):
            if not in_code:
                out.append("<pre><code>")
                in_code = True
            else:
                out.append("</code></pre>")
                in_code = False
            continue

        if in_code:
            out.append(html.escape(line))
            continue

        if line == "":
            if in_ul:
                out.append("</ul>")
                in_ul = False
            continue

        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
            continue

        if line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
            continue

        if line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
            continue

        if line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(line[2:])}</li>")
            continue

        if in_ul:
            out.append("</ul>")
            in_ul = False

        out.append(f"<p>{inline(line)}</p>")

    if in_ul:
        out.append("</ul>")

    return "\n".join(out)


def parse(mdfile):

    with open(mdfile, encoding="utf-8") as f:
        lines = f.readlines()

    meta = {}
    body = []

    header = True

    for line in lines:
        if header:
            if line.strip() == "":
                header = False
                continue

            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
                continue

        body.append(line)

    return meta, body


def make(mdfile):

    meta, body = parse(mdfile)

    article = markdown_to_html(body)

    title = meta.get("Title", "No Title")
    date = meta.get("Date", "")
    category = meta.get("Category", "")

    htmltext = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="../style.css">
</head>

<body>

<main class="container">

<p class="description">
{date} / {category}
</p>

{article}

<hr>

<p><a href="../index.html">← Home</a></p>

</main>

</body>
</html>
"""

    os.makedirs("articles", exist_ok=True)

    name = os.path.splitext(os.path.basename(mdfile))[0]

    outfile = f"articles/{name}.html"

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(htmltext)

    print(outfile)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("python make.py article.md")
        sys.exit(1)

    make(sys.argv[1])