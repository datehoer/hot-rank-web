import logging

from feedgen.feed import FeedGenerator
from lxml import etree


def generate_ai_rss(summarizes):
    try:
        feed = FeedGenerator()
        feed.title("todayTopNewsWithAI")
        feed.link(href="https://www.hotday.uk")
        feed.description("Today top news with AI")
        for item in summarizes:
            entry = feed.add_entry()
            entry.title(item.get("title", item["hot_label"]))
            entry.link(href=item.get("url", item["hot_url"]))
            entry.description(item.get("description", item["hot_content"]))
        write_rss(feed, "/app/rss_feed_today_top_news.xml")
    except Exception as exc:
        logging.error(
            f"generate todayTopNewsWithAI rss feed error, error {exc}"
        )


def generate_rank_rss(data):
    try:
        feed = FeedGenerator()
        feed.title("today news")
        feed.link(href="https://www.hotday.uk")
        feed.description("Today news")
        for items in data:
            for item in items.get("data", []):
                if item and "hot_label" in item:
                    entry = feed.add_entry()
                    entry.title(item.get("title", item.get("hot_label")))
                    entry.link(href=item.get("url", item.get("hot_url")))
        write_rss(feed, "/app/rss_feed.xml")
    except Exception as exc:
        logging.error(f"generate today news rss feed error, {exc}")


def write_rss(feed, output_path):
    xml_bytes = feed.rss_str(pretty=True)
    root = etree.fromstring(xml_bytes)
    stylesheet_pi = etree.ProcessingInstruction(
        "xml-stylesheet",
        "type='text/xsl' href='pretty-feed-v3.xsl'",
    )
    root.addprevious(stylesheet_pi)
    tree = etree.ElementTree(root)
    tree.write(
        output_path,
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    )
