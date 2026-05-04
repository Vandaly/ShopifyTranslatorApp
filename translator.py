from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
import re

DetectorFactory.seed = 0

COLOR_NAMES = {
    'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown',
    'gray', 'grey', 'cyan', 'magenta', 'navy', 'teal', 'lime', 'maroon', 'olive', 'silver',
    'gold', 'beige', 'coral', 'aqua', 'turquoise', 'indigo', 'violet'
}

SIZE_MAP = {
    'small': 'S',
    'medium': 'M',
    'large': 'L',
    'one size': 'One Size',
    'onesize': 'One Size'
}


def is_hex(value):
    if not isinstance(value, str):
        return False
    return bool(re.match(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', value.strip()))


def is_color(value):
    if not isinstance(value, str):
        return False
    v = value.strip().lower()
    if re.match(r'^#(?:[0-9a-f]{3}|[0-9a-f]{6})$', v):
        return True
    if v in COLOR_NAMES:
        return True
    return False


def detect_language(text):
    try:
        return detect(text)
    except Exception:
        return 'unknown'


def translate(text):
    if not text or not str(text).strip():
        return text
    return GoogleTranslator(source='auto', target='nl').translate(text)


def translate_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup.find_all(string=True):
        if element.strip():
            # skip nodes that look like color codes or pure numeric codes
            if is_hex(element):
                continue
            element.replace_with(translate(element))

    return str(soup)


def translate_product(product):
    title = product.get('title', '') or ''
    body_html = product.get('body_html', '') or ''

    # build sample text for language detection
    sample_text = title
    try:
        sample_text += ' ' + BeautifulSoup(body_html, 'html.parser').get_text(separator=' ')
    except Exception:
        pass

    lang = detect_language(sample_text) if sample_text.strip() else 'unknown'

    # Only translate when source language is English; skip if already Dutch
    if lang == 'nl':
        tags = product.get('tags', '')
        if 'translated' not in tags:
            product['tags'] = (tags + ', translated').strip(', ')
        return product

    if lang != 'en':
        # we only handle English -> Dutch in this mode
        return product

    # translate title and HTML body (preserves tags/styles)
    product['title'] = translate(title)
    product['body_html'] = translate_html(body_html)

    # determine which option indices represent colors (option1 -> options[0])
    options = product.get('options', []) or []
    color_option_indices = set()
    for idx, opt in enumerate(options):
        name = (opt.get('name') or '').strip().lower()
        if name in ('color', 'colour', 'farbe', 'colorway', 'colourway'):
            color_option_indices.add(idx)

    # translate options
    for option in options:
        opt_name = option.get('name', '')
        option['name'] = translate(opt_name)
        values = option.get('values', []) or []
        new_values = []
        for v in values:
            # preserve hex codes; translate color names to English
            if is_hex(v):
                new_values.append(v)
                continue

            if opt_name.strip().lower() in ('color', 'colour', 'farbe', 'colorway', 'colourway'):
                # translate color name to English; if translation is a known color, use it
                translated = translate(v)
                tlow = (translated or '').strip().lower()
                if tlow in COLOR_NAMES:
                    # normalize capitalization
                    new_values.append(tlow.capitalize())
                else:
                    # fallback: use translated text
                    new_values.append(translated)
                continue

            # handle size mappings for short option values
            vlow = (v or '').strip().lower()
            if vlow in SIZE_MAP:
                new_values.append(SIZE_MAP[vlow])
            else:
                new_values.append(translate(v))
        option['values'] = new_values

    # translate variants, translating color names but preserving hex codes
    variants = product.get('variants', []) or []
    for variant in variants:
        for idx, key in enumerate(('option1', 'option2', 'option3')):
            if variant.get(key):
                val = variant[key]
                if is_hex(val):
                    continue

                if idx in color_option_indices:
                    translated = translate(val)
                    tlow = (translated or '').strip().lower()
                    if tlow in COLOR_NAMES:
                        variant[key] = tlow.capitalize()
                    else:
                        variant[key] = translated
                    continue

                # sizes mapping
                vlow = (val or '').strip().lower()
                if vlow in SIZE_MAP:
                    variant[key] = SIZE_MAP[vlow]
                else:
                    variant[key] = translate(val)

    # append translated tag if not present
    tags = product.get('tags', '')
    if 'translated' not in tags:
        product['tags'] = (tags + ', translated').strip(', ')

    return product