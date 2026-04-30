import requests
import os
from dotenv import load_dotenv

load_dotenv()

SHOP = os.getenv("SHOPIFY_STORE")
TOKEN = os.getenv("SHOPIFY_TOKEN")

def update_product(product):
    url = f"https://{SHOP}/admin/api/2024-01/products/{product['id']}.json"

    headers = {
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }

    data = {"product": product}

    requests.put(url, json=data, headers=headers)