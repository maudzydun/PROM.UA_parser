from bs4 import BeautifulSoup as bs4
# pip install beautifulsoup4
import requests
# pip install requests
from time import sleep
import random
from functions import one_group_href, how_many_pages, card_parser
import sqlite3  as sql



# Создаем хидер чтобы сайт думал что на него заходит живой человек
headers = {"user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}


# ===============================================
# Главная страница
# ===============================================

url =input('Введите ссылку на сайт из площадки PROM.UA (без последнего знака /): ')
product_list = url + '/product_list' #добавляем продукт лист чтобы попасть на страницу с категориями товаров
response = requests.get(product_list, headers=headers)
soup = bs4(response.text, 'html.parser')
# Получили весь код страницы товаров и услуг и сделали из нее суп

# Получаем список групп товаров
groups_item = soup.find_all('li', {'class':'cs-product-groups-gallery__item'})

# Из этого списка нужно взять все ссылки и записать их в свой список
href_groups = []
for block in groups_item:
    #для єтого воспользуемся функцией которая принимает один єлемент со списка и возвращает ссылку (еще один обязательный параметр это url, нужен в том случае если ссылка была относительная)
    href_groups.append(one_group_href(block, url))
# вконце мы получаем список с ссылками на каждую группу товаров на сайте


# ============================================
# Группы товаров
# ============================================

# дальше большинство сайтов имеет еще и подгруппы , но и есть такие что имеют сразу список товаров. Мы парсим сразу товарную группу потому что в обеих вариантах мы получим такое же количество товаров, просто в первом случае будет больше таблиц что не удобно ни для баз данных , ни для екселевских таблиц
for href in href_groups:
    response = requests.get(href, headers=headers)
    sleep(random.randint(1, 5))
    soup = bs4(response.text, 'html.parser') #Получаем суп из полученой категории товаров

    # ============================================База данных==========================================================
    title = (soup.find('h1', {'class':'cs-title'}).text.replace('-', '_').replace('+', '_').replace(' ', '_').replace(',', '_').replace('.', '_').replace('(', '').replace(')', '').replace('/', '').replace("'", '')) 
    # получаем название категории товаров и записываем ее в переменную тайтл чтобы потом создать таблицу в БД с названием этой переменной

    site = url.replace('https://', '').replace('.com', '').replace('.prom', '').replace('.net', '').replace('.ua', '') #Делаем так чтобы название нашей таблицы было таким же как название домена сайта (если домен будет еще какой-то дополнительно - добавить реплейсы или переделать систему парсинга ссылки)
    connection = sql.connect(f'{site}.sqlite') #создаем или конектимся с базой данных (ее название может быть с расширением db или sqlite)
    curs = connection.cursor() #c помощью курсора можно совершать действия связаные с базой данных которая находится в переменной конекшн

    # Создаем табличку товаров в базе данных
    try:
        curs.execute(f'''CREATE TABLE {title} (id VARCHAR , name TEXT , v_nalicii TEXT , price VARCHAR , description TEXT)''')
        connection.commit()
    except:
        pass #если табличка уже есть - не создаем

    # Создаем табличку с характеристиками и называем ее как название группы товаров с добавлением слова характеристики
    try:
        curs.execute(f'''CREATE TABLE {title}_specifications (id VARCHAR , specification TEXT , value TEXT)''')
        connection.commit()
    except:
        pass #если табличка уже есть - не создаем
    # ============================================База данных==========================================================

    # дальше воспользуемся функцией для определения кол-ва страниц в текущей группе товаров
    last_page = how_many_pages(href) + 1
    for count_page in range (1, last_page):
        main_page = f'{href}/page_{count_page}' #получаем страницы по порядку и записываем в переменную текущая страница по порядку
        response = requests.get(main_page, headers=headers)
        soup = bs4(response.text, 'html.parser')
        sleep(random.randint(1, 5))
        # Получили весь код страницы и ее распарсили 

        card_li = soup.find_all('li', {'data-tg-chain':'{"view_type": "preview"}'})
        #находим список всех товаров и нужно будет вытянуть ссылку на каждый товар по отдельности

        for a in card_li:
            all_a = a.find_all('a')
            # Нашли все теги а

            for href_a in all_a:
                card_href = href_a.get('href')
                # вытянули из них все ссылку на каждый товар


# =========================================
# Товар
# =========================================
                if card_href != None:
                    card_parser(card_href, site, title) #исспользуем функцию которую я создал для парсинга ссылки любой товар на проме
                    break