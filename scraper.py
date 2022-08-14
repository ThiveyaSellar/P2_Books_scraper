from bs4 import BeautifulSoup
import concurrent.futures
import requests
import pprint
import csv
import os
import re


# Retrait du signe "£"
def transform_price(price):
    return float(price[1:])


# Récupérer la quantité en stock
def extract_number_in_stock(a):
    return int(re.search(r'\d+', a).group())


# Récupérer la note sur 5
def extract_rating(a):
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
    page = requests.get(url)
    if not page.ok:
        print("Problème chargement, code http : " + str(page.status_code))
    soup = BeautifulSoup(page.content, 'html.parser')
    
    upc = soup.find_all("td")[0].string
    title = soup.find("h1").string
    price_including_tax = transform_price(soup.find_all("td")[2].string)
    price_excluding_tax = transform_price(soup.find_all("td")[3].string)
    number_available = extract_number_in_stock(soup.find_all("td")[5].string)
    # Certains produits n'ont pas de description
    description = None
    try :
        description = soup.find("div", id = "product_description").findNext("p").text
    except AttributeError as error :
        print(error)
        print("Pas description pour : \n" + url)
    category = soup.find("ul", class_="breadcrumb").find_all("a")[-1].text
    review_rating = extract_rating(soup.find("p", class_="star-rating"))

    image_url = soup.find("div", id="product_gallery").find("img")['src']
    image_url = "https://books.toscrape.com/" + "/".join(image_url.split("/")[2:])

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

    """
    #Afficher proprement product
    print("Données récupérées : \n")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(product)
    """
    return product


# Sauvegarder les informations extraites d'un produit dans un fichier csv
def save_product_info(product):
    # En-tête du fichier CSV avec les clés du dictionnaire
    header = []
    for key in product.keys():
        header.append(key)
    # Définir le nom du fichier à partir du titre du livre
    name = product['title']
    name = '_'.join(name.split(' '))
    file_name = name + '_info.csv'
    # Ouvrir et écrire dans le fichier csv
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        line = []
        for k, v in product.items():
            line.append(v)
        writer.writerow(line)


# Extraire les url des produits sur une page
def extract_page_product_url(soup, tab, url_racine):
    product_url_list = soup.find_all("h3")
    for e in product_url_list:
        product_url = url_racine + '/' + e.find("a")['href']
        tab.append(product_url)


# Extraire les urls des produits sur toutes les pages d'une catégorie
def extract_all_product_url(url, category):
    # Requête avec le lien de la première page de la catégorie
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Tableau des urls de la catégorie
    category_product_url = []
    # Récupérer les liens de tous les produits de la page actuelle
    u = url.split("/")
    u = u[0:-1]
    u = "/".join(u)
    extract_page_product_url(soup, category_product_url, u)
    # Chercher url de la page suivante
    next_page = soup.find("li", class_="next")

    # Tant qu'il existe une page suivante
    # Récupérer les url de tous les produits
    # Vérifier qu'il existe une page suivante
    # Récupérer la page
    while next_page is not None:
        next_url = next_page.find("a")
        url = u + '/' + next_url['href']
        #print("http://books.toscrape.com/" + url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        extract_page_product_url(soup, category_product_url, u)
        next_page = soup.find("li", class_="next")
    return category_product_url


# Extraire les urls des produits d'une catégorie
def find_category_url(category):
    # Définir une expression régulière pour extraire url contenant la catégorie
    reg_exp = "./" + category + "_."
    # Chercher url contenant la catégorie souhaitée
    category_url = soup.find("a", href=re.compile(reg_exp))
    # Définir url complet de la catégorie
    category_url = "http://books.toscrape.com/" + category_url['href']
    return category_url


def save_category_product_info(urls, file_name, directory):
    # En-tête du fichier CSV
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
    with open(directory + "/" + file_name, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        for url in urls:
            product = retrieve_product_info(url)
            line = []
            for k, v in product.items():
                line.append(v)
            writer.writerow(line)
    print("Fichier créé : " + file_name)

def choose_category():
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
    category = input("\nChoisir une catégorie : ").lower()
    while category not in categories:
        category = input("\nChoisir une catégorie valide : ").lower()
    return category


def scrap_category(category, directory):
    print("\n" + category.upper())
    c_url = find_category_url(category)
    print(c_url)
    c_url_list = extract_all_product_url(c_url, category)
    save_category_product_info(c_url_list, category + "_product_info.csv", directory)
    return len(c_url_list)


def extract_page_images_urls(soup, tab_img, tab_title):
    img_tags = soup.findAll("img")
    h3_tags = soup.findAll("h3")
    for h3 in h3_tags:
        title = h3.find("a")['title']
        title = title.replace("/", "_")
        title = "_".join(title.split(' '))
        tab_title.append(title)
    for tag in img_tags:
        image_url = tag['src']
        image_url = image_url.split("/")
        image_url = image_url[3:]
        image_url = "/".join(image_url)
        image_url = "https://books.toscrape.com/" + image_url
        tab_img.append(image_url)


def extract_all_images_urls(soup, tab_urls, tab_titles):
    extract_page_images_urls(soup, tab_urls, tab_titles)
    next_page = soup.find("li", class_="next")
    while next_page is not None:
        next_url = "https://books.toscrape.com/catalogue/category/books_1/" + next_page.find("a")['href']
        page = requests.get(next_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        extract_page_images_urls(soup, tab_urls, tab_titles)
        next_page = soup.find("li", class_="next")


def save_products_images(tab_urls, tab_titles, dir):
    for i in range(len(tab_urls)):
        file = open(dir + '/' + tab_titles[i] + '.jpg', 'wb')
        response = requests.get(tab_urls[i])
        file.write(response.content)
        file.close()
    print("Les images des produits sont enregistrées : " + dir + "/")


# ----------------------------------------------------------------------------------------

    # Récupérer les informations d'un produit à partir url de sa page

# ----------------------------------------------------------------------------------------
print("\n1) Extraire les informations d'un produit à partir de l'url de sa page")
print("Souhaitez-vous saisir l'url d'un produit ? 'O' pour oui ou 'N' non")
rep = input().lower()
while rep != 'o' and rep != 'n':
    print("Saisir 'O' pour oui ou 'N' non")
    rep = input().lower()
if rep == 'o':
    print("Saisir l'url d'un produit")
    url_choisi = input()
    product = retrieve_product_info(url_choisi)
    print("Données récupérées : \n")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(product)
    save_product_info(product)
else:
    url_ex = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    product = retrieve_product_info(url_ex)
    print("Données récupérées : \n")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(product)
    save_product_info(product)

# ----------------------------------------------------------------------------------------

    # Extraire les url et les informations des produits d'une catégorie

# ----------------------------------------------------------------------------------------
URL_MAIN = "http://books.toscrape.com/index.html"
page = requests.get(URL_MAIN)
soup = BeautifulSoup(page.content, 'html.parser')
print("\n2) Extraire les informations des produits d'une catégorie")
category = choose_category()
category = category.replace(" ", "-")
category_url = find_category_url(category)
# Récupérer la liste des urls de tous les produits de la catégorie souhaitée
url_list = extract_all_product_url(category_url, category)
save_category_product_info(url_list, category + "_product_info.csv", "./")

# ----------------------------------------------------------------------------------------

    # Extraire toutes les catégories

# ----------------------------------------------------------------------------------------
print("\n3) Extraire les informations des produits de toutes les catégories")
category_section = soup.find("div", class_="side_categories")
category_url_list = category_section.find_all("a")[1:]
categories = []
# Afficher les catégories et les ajouter à la liste des catégories
for category in category_url_list:
    c = category.text.strip()
    if " " in c:
        c = c.replace(' ', '-')
    categories.append(c.lower())

category_dir = "Categories"
parent_directory = "./"
path = os.path.join(parent_directory, category_dir)
try:
    os.mkdir(path)
except FileExistsError as error:
    print(error)

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    a = []
    for c in categories:
        a.append(executor.submit(scrap_category, c, category_dir))
    executor.shutdown()
    print("Nombre de produits scrappés : " + sum([f.result() for f in a]))

# ----------------------------------------------------------------------------------------

    # Télécharger les images des pages produits

# ----------------------------------------------------------------------------------------
print("\n4) Télécharger et enregistrer les images des produits")
page = requests.get("https://books.toscrape.com/catalogue/category/books_1/index.html")
soup = BeautifulSoup(page.content, 'html.parser')
tab_img_urls = []
tab_img_titles = []

extract_all_images_urls(soup, tab_img_urls,tab_img_titles)

directory = "Products_images"
parent_directory = "./"
path = os.path.join(parent_directory, directory)
try:
    os.mkdir(path)
except FileExistsError as error:
    print(error)

save_products_images(tab_img_urls, tab_img_titles,directory)
