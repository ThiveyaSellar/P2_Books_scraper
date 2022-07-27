import requests
from bs4 import BeautifulSoup
import re

#----------------------------------------------------------------------------------------
    #Fonctions
#----------------------------------------------------------------------------------------

def transform_price(price):
    return float(price[1:])

def retrieve_number_in_stock(a):
    return int(re.search(r'\d+', a).group())

def retrieve_product_info(url):

    #Récupérer les informations d'un produit
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')


#----------------------------------------------------------------------------------------

url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
page = requests.get(url)
#print(page.content)

soup = BeautifulSoup(page.content, 'html.parser')

product_page_url = url
upc = soup.find_all("td")[0].string
title = soup.find("h1").string
price_including_tax = transform_price(soup.find_all("td")[2].string)
price_excluding_tax = transform_price(soup.find_all("td")[3].string)
number_available = retrieve_number_in_stock(soup.find_all("td")[5].string)
description = soup.find_all("p")[-1].string
category = soup.find_all("ul", class_="breadcrumb")
print(category)

product = {
    "product_page_url": url,
    "universal_product_code": upc,
    "title": title,
    "price_including_tax": price_including_tax,
    "price_excluding_tax": price_excluding_tax,
    "number_available": number_available,
    "product_description": description,
    "category": "",
    "review_rating": 0,
    "image_url": ""
}

