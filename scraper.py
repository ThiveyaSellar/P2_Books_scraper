import json

import requests
from bs4 import BeautifulSoup
import re


# ----------------------------------------------------------------------------------------

# Fonctions

# ----------------------------------------------------------------------------------------


def transform_price(price):
    return float(price[1:])


def retrieve_number_in_stock(a):
    return int(re.search(r'\d+', a).group())


def retrieve_rating(a):
    rating = a['class'][1].upper()
    if rating == 'ONE':
        return 1
    elif rating == 'TWO':
        return 2
    elif rating == 'THREE':
        return 3
    elif rating == 'FOUR':
        return 4
    elif rating == 'FIVE':
        return 5
    else:
        return 0


def retrieve_product_info(url):
    # Récupérer les informations d'un produit
    page = requests.get(url)
    # print(page.content)
    soup = BeautifulSoup(page.content, 'html.parser')
    product_page_url = url
    upc = soup.find_all("td")[0].string
    title = soup.find("h1").string
    price_including_tax = transform_price(soup.find_all("td")[2].string)
    price_excluding_tax = transform_price(soup.find_all("td")[3].string)
    number_available = retrieve_number_in_stock(soup.find_all("td")[5].string)
    description = soup.find_all("p")[-1].string
    category = soup.find_all("a")[-1].string
    review_rating = retrieve_rating(soup.find("p", class_="star-rating"))
    image_url = soup.find("img")['src']

    product = {
        "product_page_url": url,
        "universal_product_code": upc,
        "title": title,
        "price_including_tax": price_including_tax,
        "price_excluding_tax": price_excluding_tax,
        "number_available": number_available,
        "product_description": description,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_url
    }

    json_product = json.dumps(product, indent=4)
    print(json_product)


# ----------------------------------------------------------------------------------------

# Main

# ----------------------------------------------------------------------------------------


url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

retrieve_product_info(url)
