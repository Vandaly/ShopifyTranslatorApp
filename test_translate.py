import json
from translator import translate_product, detect_language

p = json.load(open('test_product.json', 'r', encoding='utf-8'))
print('Original title:', p.get('title'))

sample = p.get('title','') + ' ' + (p.get('body_html','') or '')
print('Detected language:', detect_language(sample))

translated = translate_product(p)
print('\nTranslated title:', translated.get('title'))
print('\nTranslated body_html:', translated.get('body_html'))
print('\nOptions:')
for o in translated.get('options', []):
    print(' -', o.get('name'), ':', o.get('values'))
print('\nVariants:')
for v in translated.get('variants', []):
    print(' -', v.get('id'), v.get('option1'), v.get('option2'))
print('\nTags:', translated.get('tags'))
