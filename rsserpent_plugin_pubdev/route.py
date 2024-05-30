from typing import Any

import arrow
from lxml import html

from rsserpent_rev.utils import HTTPClient, cached

path = "/pubdev/update/{package}"


def get_date(date_str: str) -> arrow.Arrow:
    formats = ["YYYY-MM-DD", "YYYY-M-DD", "MMMM D, YYYY", "YYYY‑MM‑DD"]
    for fmt in formats:
        try:
            date = arrow.get(date_str.strip(), fmt)
            break
        except Exception:
            date = arrow.now()

    return date


@cached
async def provider(package: str) -> dict[str, Any]:
    async with HTTPClient() as client:
        changelog_url = f"https://pub.dev/packages/{package}/changelog"
        html_text = (await client.get(changelog_url)).content.decode("utf-8")
        tree = html.fromstring(html_text)

        changelog_entries = tree.xpath("//div[@class='changelog-entry']")
        changelog = {}
        for entry in changelog_entries:
            version = entry.xpath(".//h2")[0].text_content().strip().replace(" #", "")
            note = entry.xpath(".//div[@class='changelog-content']")[0].text_content()
            changelog[version] = note

        versions_url = f"https://pub.dev/packages/{package}/versions"
        versions_content = (await client.get(versions_url)).content.decode("utf-8")
        tree = html.fromstring(versions_content)

        tbody = tree.xpath("//tbody")[0]
        rows = tbody.xpath(".//tr")
        items = [
            {
                "title": f"{package} {row.xpath('.//td')[0].text_content()} 更新",
                "description": changelog.get(row.xpath(".//td")[0].text_content(), ""),
                "link": "https://pub.dev" + row.xpath(".//td")[0].xpath(".//a")[0].attrib["href"],
                # format a tag's data-timestamp
                "pub_date": arrow.get(row.xpath(".//td")[3].xpath(".//a")[0].attrib["data-timestamp"], "x"),
            }
            for row in rows
        ]

    return {
        "title": f"{package} 更新日志",
        "link": f"https://pub.dev/packages/{package}",
        "description": f"最新更新日期：{items[0]['pub_date'].format('YYYY-MM-DD')}",
        "pub_date": items[0]["pub_date"],
        "items": items,
    }
