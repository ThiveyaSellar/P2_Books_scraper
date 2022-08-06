import requests
from bs4 import BeautifulSoup
import re
import pprint
import csv
import concurrent.futures


# Retrait du signe "£"
def transform_price(price):
    return float(price[1:])


# Récupérer la quantité en stock
def retrieve_number_in_stock(a):
    return int(re.search(r'\d+', a).group())


# Récupérer la note sur 5
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


# Récupérer diverses informations d'un produit sur sa page
def retrieve_product_info(url):
    # Récupérer les informations d'un produit

    # Récupérer le contenu de la page grâce au package request
    page = requests.get(url)
    if not page.ok :
        print("Problème chargement, code http : " + str(page.status_code))
    # Parser le contenu récupéré graĉe au package BeautifulSoup
    soup = BeautifulSoup(page.content, 'html.parser')
    upc = soup.find_all("td")[0].string
    title = soup.find("h1").string
    price_including_tax = transform_price(soup.find_all("td")[2].string)
    price_excluding_tax = transform_price(soup.find_all("td")[3].string)
    number_available = retrieve_number_in_stock(soup.find_all("td")[5].string)
    # Certains produits n'ont pas de description
    description = None
    try :
        description = soup.find("div", id = "product_description").findNext("p").text
    except AttributeError as error :
        print(error)
        print("Pas description : " + url)
    category = soup.find("ul", class_="breadcrumb").find_all("a")[-1].text
    review_rating = retrieve_rating(soup.find("p", class_="star-rating"))
    image_url = soup.find("div", id="product_gallery").find("img")['src']

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

    """print("Données récupérées : \n")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(product)"""
    return product


# Sauvegarder les informations extraites d'un produit dans un fichier csv
def save_product_info(product) :
    #En-tête du fichier CSV avec les clés du dictionnaire
    header = []
    for key in product.keys():
        header.append(key)

    name = product['title']
    name = name.split(' ')
    name = '_'.join(name)
    file_name = name + '_info.csv'
    with open(file_name,'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        line = []
        for k, v in product.items():
            line.append(v)
        writer.writerow(line)


# Extraire les url des produits sur une page
def extract_page_product_url(soup, tab, url_racine):
    product_url_list = soup.find_all("h3")
    for a in product_url_list:
        b = url_racine + '/' +a.find("a")['href']
        tab.append(b)


# Extraire les urls des produits sur toutes les pages d'une catégorie
def extract_all_product_url(url, category):

    # Requête avec le lien de la première page de la catégorie
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')

    # Tableau des urls de la catégorie
    category_product_url = []
    # Récupérer les liens de tous les produits de la page actuelle
    urla = url.split("/")
    urla = urla[0:-1]
    u = "/".join(urla)
    extract_page_product_url(soup, category_product_url, u)
    # Chercher l'url de la page suivante
    next_page = soup.find("li", class_="next")

    # Tant qu'il existe une page suivante
    # Récupérer les url de tous les produits
    # Vérifier qu'il existe une page suivante
    # Récupérer la page
    while next_page != None :
        next_url = next_page.find("a")
        url = u + '/' + next_url['href']
        #print("http://books.toscrape.com/" + url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content,'html.parser')
        extract_page_product_url(soup, category_product_url, u)
        next_page = soup.find("li", class_="next")
    return category_product_url


# Extraire les urls des produits d'une catégorie
def find_category_url(category):

    # Définir une expression régulière pour extraire l'url contenant la catégorie
    reg_exp = "./" + category + "_."
    # Chercher l'url contenant la catégorie souhaitée
    category_url = soup.find("a", href=re.compile(reg_exp))



    # Définir l'url complet de la catégorie
    category_url = "http://books.toscrape.com/" + category_url['href']
    return category_url


def save_category_product_info(urls, file_name):
    #En-tête du fichier CSV
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

    with open(file_name,'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)

        for url in urls:
            product = retrieve_product_info(url)
            line = []
            for k, v in product.items():
                line.append(v)
            writer.writerow(line)


def choose_category() :
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

    return category, categories

def scrap_category(c):
    print(c)
    c_url = find_category_url(c)
    print(c_url)
    c_url_list = extract_all_product_url(c_url,c)
    save_category_product_info(c_url_list, c + "_product_info.csv")
    return len(c_url_list)




# ----------------------------------------------------------------------------------------

    # Récupérer les informations d'un produit à partir de l'url de sa page

# ----------------------------------------------------------------------------------------
"""
url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
product = retrieve_product_info(url)
save_product_info(product)
"""

# ----------------------------------------------------------------------------------------

    # Extraire les url et les informations des produits d'une catégorie

# ----------------------------------------------------------------------------------------

# Requête avec url de la page principale
URL_MAIN = "http://books.toscrape.com/index.html"
page = requests.get(URL_MAIN)
soup = BeautifulSoup(page.content, 'html.parser')

# Afficher la liste des catégories et choisir une catégorie
category, categoriess = choose_category()
# Récupérer l'url de la catégorie
category_url = find_category_url(category)
# Récupérer la liste des urls de tous les produits de la catégorie souhaitée
url_list = extract_all_product_url(category_url,category)

"""
somme = 0
for c in categoriess :
    print(c)
    c = c.split(" ")
    c = "-".join(c)
    c_url = find_category_url(c)
    url_l = extract_all_product_url(c_url, c)
    print(len(url_l))
    if c == "christian" or c == "biography" or c == "science" :
        print(c_url)
    somme = somme + len(url_l)
print(somme-1000)
"""


# Récupérer les informations de tous les produits et les enregistrer dans un fichier csv
save_category_product_info(url_list, category + "_product_info.csv")

# Extraire toutes les catégories
category_section = soup.find("div", class_="side_categories")
category_url_list = category_section.find_all("a")
categories = []
# Afficher les catégories et les ajouter à la liste des catégories
for category in category_url_list:
    c = category.text.strip()
    if " " in c :
        c = c.replace(' ','-')
    categories.append(c.lower())

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    a = []
    for c in categories :
        a.append(executor.submit(scrap_category,c))
    executor.shutdown()
    print(sum([ f.result() for f in a ]))








