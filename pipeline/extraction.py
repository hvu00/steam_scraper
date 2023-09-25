from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
import logging

_extraction_config = {
    "url": "https://store.steampowered.com/specials",
    "containers": [
        {
            "name": "store_sale_divs",
            "selector": 'div[class*=salepreviewwidgets_StoreSaleWidgetContainer]',
            "match": "all",
            "items": [
                {
                    "name": "title",
                    "selector": 'div[class*="StoreSaleWidgetTitle"]',
                    "match": "first",
                    "type": "text"
                },
                {
                    "name": "thumbnail",
                    "selector": 'img[class*="salepreviewwidgets_CapsuleImage"]',
                    "match": "first",
                    "type": "node",
                    "attr": "src"
                },
                {
                    "name": "categories",
                    "selector": 'a[class*="salepreviewwidgets_AppTag"]',
                    "match": "all",
                    "type": "text"
                },
                {
                    "name": "release_date",
                    "selector": 'div[class*="salepreviewwidgets_WidgetReleaseDateAndPlatformCtn"] > div[class*="salepreviewwidgets_StoreSaleWidgetRelease"]',
                    "match": "first",
                    "type": "text"
                },
                {
                    "name": "review_category",
                    "selector": 'div[class*="gamehover_ReviewScoreValue"]',
                    "match": "first",
                    "type": "text"
                },
                {
                    "name": "review_count",
                    "selector": 'div[class*="gamehover_ReviewScoreValue"]',
                    "match": "first",
                    "type": "text"
                },
                {
                    "name": "price_currency",
                    "selector": 'div[class*="salepreviewwidgets_StoreOriginalPrice"]',
                    "match": "first",
                    "type": "text"
                },
                {
                    "name": "original_price",
                    "selector": 'div[class*="salepreviewwidgets_StoreOriginalPrice"]',
                    "match": "first",
                    "type": "text"
                },
                {
                    "name": "discounted_price",
                    "selector": 'div[class*="salepreviewwidgets_StoreSalePriceBox"]',
                    "match": "first",
                    "type": "text"
                },
            ]
        }
    ]
}

def get_config():
    return _extraction_config

def extract_body_html(url, wait_for_selector=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        
        page.wait_for_load_state("networkidle")
        page.evaluate("() => window.scroll(0, document.body.scrollHeight)")
        page.wait_for_load_state("domcontentloaded")

        if wait_for_selector:
            page.wait_for_selector(wait_for_selector)

        return page.inner_html("body")

def extract_raw_node_data(type, attr, nodes):
    if type == "text":
        return nodes.text()
    elif type == "node":
        if attr:
            return nodes.attributes.get(attr)
        else:
            return nodes
    else:
        raise NotImplementedError(f"no handling for type config '{type}' in extract_raw_node_data")

def extract_raw_container_data(node, config):
    raw_data_item = {}

    try:
        for n_config in config:
            name = n_config['name']
            selector = n_config['selector']
            match = n_config['match']
            type = n_config['type']
            attr = None if 'attr' not in n_config else n_config['attr']

            if match == "all":
                selected_nodes = node.css(selector)
            elif match == "first":
                selected_nodes = node.css_first(selector)
            else:
                raise NotImplementedError(f"no handling for match config '{match}' in extract_raw_container_data")

            if not selected_nodes:
                return None

            if match == "all":
                raw_data_item[name] = [extract_raw_node_data(type, attr, n) for n in selected_nodes]
            elif match == "first":
                raw_data_item[name] = extract_raw_node_data(type, attr, selected_nodes)
    except AttributeError:
        logging.exception(n_config)

    return raw_data_item

def extract_raw_data(config):
    html_tree = HTMLParser(
        extract_body_html(config["url"], "div[class*=salepreviewwidgets_StoreSaleWidgetContainer]")
        )

    raw_data_result = []

    logging.debug(f"{len(config['containers'])} container(s) found in config")

    for c_config in config['containers']:
        match = c_config['match']
        selector = c_config['selector']
        
        if match == "all":
            container_nodes = html_tree.css(selector)
        elif match == "first":
            container_nodes = [html_tree.css_first(selector)]
        else:
            raise NotImplementedError(f"no handling for match config '{match}' in extract_raw_data")

        logging.debug(f"{len(container_nodes)} container nodes found in page")
        for c_node in container_nodes:
            raw_data_result.append(
                extract_raw_container_data(c_node, c_config['items'])
            )

    return raw_data_result