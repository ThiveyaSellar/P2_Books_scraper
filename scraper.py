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
    description = soup.find("div", id = "product_description").findNext("p").text
    category = soup.find("ul", class_="breadcrumb").find_all("a")[-1].text
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

    """json_product = json.dumps(product, indent=4)
    print(json_product)"""
    return product

def save_product_info(product, file_name) :
    #En-tête du fichier CSV avec les clés du dictionnaire
    header = []
    for key in product.keys():
        header.append(key)

    with open(file_name,'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        line = []
        for k, v in product.items():
            line.append(v)
        writer.writerow(line)


# Extraire les url des produits sur une page
def extract_page_product_url(soup, tab):
    product_url_list = soup.find_all("h3")
    for a in product_url_list:
        b = a.find("a")['href']
        tab.append(b)


# Extraire les urls des produits sur toutes les pages d'une catégorie
def extract_all_product_url(url):

    # Requête avec le lien de la première page de la catégorie
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')

    # Tableau des urls de la catégorie
    category_product_url = []
    # Récupérer les liens de tous les produits de la page actuelle
    extract_page_product_url(soup, category_product_url)
    # Retirer index.html à l'url
    u = url[0:-10]
    # Chercher l'url de la page suivante
    next_page = soup.find("li", class_="next")

    # Tant qu'il existe une page suivante
    # Récupérer les url de tous les produits
    # Vérifier qu'il existe une page suivante
    # Récupérer la page
    while next_page != None :
        next_url = next_page.find("a")
        url = u + next_url['href']
        #print("http://books.toscrape.com/" + url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content,'html.parser')
        extract_page_product_url(soup, category_product_url)
        next_page = soup.find("li", class_="next")




# Extraire les urls des produits d'une catégorie
def retrieve_one_category():
    # URL de la page principale
    url_main = "http://books.toscrape.com/index.html"
    page = requests.get(url_main)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Récupérer le bloc des catégories
    category_section = soup.find("div", class_="side_categories")
    # Lister tous les url des catégories
    category_url_list = category_section.find_all("a")
    # Liste vide pour ajouter les catégories
    categories = []
    # Afficher les catégories et les ajouter à la liste des catégories
    for category in category_url_list:
        c = category.text.strip()
        print(c)
        categories.append(c.lower())

    # Demander de choisir une catégorie
    # Si catégorie est absente de la liste des catégories, répéter la saisie
    category = input("\nChoose a category : ").lower()
    while category not in categories:
        category = input("\nPlease write a valid category : ").lower()

    # Définir une expression régulière pour extraire l'url contenant la catégorie
    reg_exp = "." + category + "."
    # Chercher l'url contenant la catégorie souhaitée
    category_url = soup.find("a", href=re.compile(reg_exp))

    # Définir l'url complet de la catégorie
    category_url = "http://books.toscrape.com/" + category_url['href']
    print(category_url)

    #Récupérer la liste des url des produits de la page
    extract_all_product_url(category_url)

    # En-tête du fichier CSV avec les clés du dictionnaire
    header = [
        "product_page_url",
        "universal_product_code",
        "title",
        "price_including_tax",
        "price_excluding_tax",
        "number_available",
        "product_description",
        "category",
        "review_rating",
        "image_url"
    ]






# ----------------------------------------------------------------------------------------

# Main

# ----------------------------------------------------------------------------------------
# Url de la page d'un produit
url = "https://books.toscrape.com/catalogue/sharp-objects_997/index.html"
product = retrieve_product_info(url)
save_product_info(product, "product_info.csv")
# ----------------------------------------------------------------------------------------
#retrieve_one_category()








