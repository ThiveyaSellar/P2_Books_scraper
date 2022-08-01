import json
import csv
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
    print()

    #En-tête du fichier CSV avec les clés du dictionnaire
    header = []
    for key in product.keys():
        header.append(key)

    with open('product_info.csv','w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        line = []
        for k, v in product.items():
            line.append(v)
        writer.writerow(line)


def retrieve_one_category():
    # URL de la page principale
    url = "http://books.toscrape.com/index.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Récupérer le bloc des catégories
    category_section = soup.find("div", class_="side_categories")
    # Lister tous les url des catégories
    category_list = category_section.find_all("a")
    # Liste vide pour ajouter les catégories
    categories = []
    # Afficher les catégories et les ajouter à la liste des catégories
    for cat in category_list:
        c = cat.text.strip()
        print(c)
        categories.append(c.lower())

    # Demander de choisir une catégorie
    # Si catégorie non présente dans la liste des catégories, demande de recommencer la saisie
    category = input("\nChoose a category : ").lower()
    while category not in categories:
        category = input("\nPlease write a valid category : ").lower()

    # Définir une expression régulière pour extraire l'url contenant la catégorie
    reg_exp = "." + category + "."
    # Chercher l'url contenant la catégorie souhaitée
    category_url = soup.find("a", href=re.compile(reg_exp))
    print(category_url['href'])

    url = "http://books.toscrape.com/" + category_url['href']

    # A mettre dans une fonction a appelé à chaque page
    product_url = soup.find_all("h3")
    for a in product_url :
        b = a.find("a")['href']
        print(b)

    next = soup.find("li", class_="next")
    next_url = next.find("a")
    """if next_url['href']:
        url = url + next_url['href']
        print(url)
"""




# ----------------------------------------------------------------------------------------

# Main

# ----------------------------------------------------------------------------------------
# Url de la page d'un produit
url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
retrieve_product_info(url)
# ----------------------------------------------------------------------------------------
retrieve_one_category()








