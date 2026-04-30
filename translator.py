from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup

def translate(text):
    return GoogleTranslator(source='auto', target='en').translate(text)

def translate_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup.find_all(string=True):
        if element.strip():
            element.replace_with(translate(element))

    return str(soup)

def translate_product(product):
    product["title"] = translate(product["title"])
    product["body_html"] = translate_html(product["body_html"])

    # translate options
    for option in product["options"]:
        option["name"] = translate(option["name"])
        option["values"] = [translate(v) for v in option["values"]]

    # translate variants
    for variant in product["variants"]:
        if variant.get("option1"):
            variant["option1"] = translate(variant["option1"])

    product["tags"] = product.get("tags", "") + ", translated"

    return product