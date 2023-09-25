from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
import json
import logging

def get_config():
    with open('./config.json', 'r') as conf_file:
        config_str = conf_file.read()
        logging.debug(config_str)
        return json.loads(config_str)

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
        extract_body_html(config["url"], config["wait_for_selector"])
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