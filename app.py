from flask import Flask, request
from translator import translate_product
from shopifyAPI import update_product
import time

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    product = request.json

    # prevent re-processing
    if "translated" in product.get("tags", ""):
        return "ok", 200

    time.sleep(5)  # wait for Poky to finish

    translated = translate_product(product)

    update_product(translated)

    return "ok", 200

app.run(port=5000)