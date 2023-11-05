from bs4 import BeautifulSoup as BS
import requests
import time
from selenium import webdriver

dictCards = {}


def scroll_down_all(driver, pause_sec=1):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Pause
        time.sleep(pause_sec)
        # After scroll down, get current height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def selenium_request(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")
    #options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)
    scroll_down_all(driver, pause_sec=1)
    html = driver.page_source
    #print(html)
    driver.close()
    return html


def getcardsentry(cardname):
    url = f"https://www.sentryboxcards.com/search?s={cardname}&t=n"
    text = requests.get(url).text
    soup = BS(text, 'html.parser')
    div_bs4 = soup.find_all('div', id="mainContent")

    for divClass in div_bs4:
        cards = divClass.find_all('div', {"class": "cardBox"})
        for card in cards:
            cardStatus = card.find('div', {"class": "cbVariant"}).text
            cardStatus = cardStatus.replace('\t', '').strip().replace('\n', ' | ').replace('\r', '')
            cardStatus = cardStatus.split("|")[1].replace('  ', ' ')

            cardId = card.find('a')['href'].replace('item?id=', '')
            cardTitle = card.find('a')['title']
            field = card.find_all("span")[1].text
            if field == 'FOIL':
                cardQty = card.find_all("span")[2].text
                cardPrice = float(card.find_all('span')[4].text)
                cardType = 'Foil'

            else:
                cardQty = card.find_all("span")[1].text
                cardPrice = float(card.find_all("span")[3].text)
                cardType = 'Normal'

            if cardQty != "0":
                cardLink = "https://www.sentryboxcards.com/item?id=" + cardId
                # print(cardTitle, qtd, cardId, price, cardStatus)
                dictCards[cardId] = [cardTitle, cardQty, cardPrice, cardStatus,
                                     cardType, cardId, cardLink, "Sentry Box"]


def getcardwizard(cardname):
    url = f"https://kanatacg.crystalcommerce.com/advanced_search?utf8=%E2%9C%93&search%" \
          f"5Bfuzzy_search%5D={cardname}&search%5Btags_name_eq%5D=&search%5Bsell_price_gte%" \
          f"5D=&search%5Bsell_price_lte%5D=&search%5Bbuy_price_gte%5D=&search%5Bbuy_price_lte%" \
          f"5D=&search%5Bin_stock%5D=0&search%5Bin_stock%5D=1&buylist_mode=0&search%" \
          f"5Bcategory_ids_with_descendants%5D%5B%5D=&search%5Bcategory_ids_with_descendants%" \
          f"5D%5B%5D=&search%5Bsort%5D=name&search%5Bdirection%5D=ascend&commit=Search&search%5Bcatalog_group_id_eq%5D="
    text = requests.get(url).text
    soup = BS(text, 'html.parser')
    for ultag in soup.find_all('ul', {'class': 'products'}):
        for litag in ultag.find_all('li'):
            # print(litag)
            cardTitleFull = litag.find('a')['title']
            cardTitle = cardTitleFull.split('-')[0]
            if cardname not in cardTitle.lower():
                continue
            if 'foil' in cardTitleFull.lower():
                cardType = 'Foil'
            else:
                cardType = 'Normal'
            if 'showcase' in cardTitleFull.lower():
                cardType = cardType + ' - Showcase'

            cardQty = litag.find('span', {'class': 'variant-short-info variant-qty'})
            cardQty = cardQty.text.replace('In Stock', '').strip()
            if cardQty == "Out of stock.":
                continue

            cardId = litag.find('a')['href'].replace('/products/', '').split('/')[-1]
            cardPrice = litag.find('span', {'class': 'price'}).text.replace('$', '').replace('CAD', '').strip()
            cardPrice = float(cardPrice)
            cardStatus = litag.find('span', {'class': 'variant-short-info variant-description'}).text
            cardLink = "https://kanatacg.crystalcommerce.com/" + litag.find('a')['href']

            # print(cardTitle, cardQty, cardPrice, cardType, cardStatus, cardId, "Wizard Tower")
            dictCards[cardId] = [cardTitle, cardQty, cardPrice, cardStatus, cardType, cardId, cardLink, "Wizard Tower"]


def getcardfacetoface(cardname):
    url = f"https://www.facetofacegames.com/search/?keyword={cardname}&pg=1&child_inventory_level=1"
    html = selenium_request(url)
    soup = BS(html, 'lxml')

    CardType = [["NM", "Normal"], ["PL", "Normal"], ["NM", "Foil"], ["PL", "Foil"]]
    cardfull = soup.find_all('div', {"class": "hawk-results__item-name"})
    for eachcard in cardfull:
        cards = eachcard.find_all('div', {"class": "hawk-results__action-stockPrice"})
        cardTitle = eachcard.find('h4', {"class": "hawk-results__hawk-contentTitle"}).text
        cardLink = eachcard.find('a')['href']
        for card in cards:
            cardQtyAll = card.find('p', {"class": "hawk-results__hawk-contentStock hawk-results__hawk-contentStock__list"})
            cardPriceAll = card.find_all('span', {"class": "retailPrice hawkPrice"})
            count = 0

            for qtd in cardQtyAll:

                if "Out of Stock" not in qtd.text:
                    cardQty = qtd.text
                    cardPrice = float(cardPriceAll[count].text.replace("\n", "").replace(" ", "").replace("CAD$", ""))
                    cardStatus = CardType[count][0]
                    cardType = CardType[count][1]
                    cardId = qtd['data-var-id']
                    dictCards[cardId] = [cardTitle, cardQty, cardPrice, cardStatus, cardType, cardId, cardLink, "Face to Face"]
                count += 1


def getcardgamekeeper(cardname):
    url = f"https://www.gamekeeperonline.com/products/search?q={cardname}&c=1"
    text = requests.get(url).text
    soup = BS(text, 'html.parser')
    for ultag in soup.find_all('ul', {'class': 'products'}):
        for litag in ultag.find_all('li', {'itemtype': 'https://schema.org/Product'}):
            #print(litag)
            cardtest = litag.find('a')['href']
            if 'buylist' in cardtest:
                continue
            cardTitleFull = litag.find('a')['title']
            cardTitle = cardTitleFull.split('-')[0]

            if cardname not in cardTitle.lower():
                continue
            if 'foil' in cardTitleFull.lower():
                cardType = 'Foil'
            else:
                cardType = 'Normal'
            if 'showcase' in cardTitleFull.lower():
                cardType = cardType + ' - Showcase'

            cardQty = litag.find('span', {'class': 'drop-qty'})
            if not cardQty:
                continue
            cardQty = cardQty.text.replace('In Stock', '').strip()
            if cardQty == "Out of stock.":
                continue

            cardPrice = litag.find('span', {'class': 'regular price'}).text.replace('CAD$', '').strip()
            cardPrice = float(cardPrice)
            cardStatus = litag.find('span', {'class': 'variant-short-info'}).text
            cardLink = "https://www.gamekeeperonline.com" + litag.find_all('a')[1]['href']
            cardId = cardLink.split('/')[-1]

            #print(cardTitle, cardQty, cardPrice, cardType, cardStatus, cardId, cardLink, "Game Keeper")
            dictCards[cardId] = [cardTitle, cardQty, cardPrice, cardStatus, cardType, cardId, cardLink, "Game Keeper"]


'''def getcard401games(cardname):
    #url = f"https://store.401games.ca/pages/search-results?q={cardname}&filters=In+Stock,True"
    url = "https://store.401games.ca/pages/search-results?q=vadrik"
    html = selenium_request(url)
    soup = BS(html, 'lxml')
    #print(soup)'''


def getcardlamood(cardname):
    url = f"https://lamoodcomics.ca/search?q=*{cardname}*"
    text = requests.get(url).text
    soup = BS(text, 'html.parser')
    cards = soup.find_all('div', {"class": "product Norm"})
    for card in cards:
        cardTitle = (card.find('p', attrs={'class': 'productTitle'})).text
        if cardname in cardTitle.lower():
            cardPrice = (card.find('p', attrs={'class': 'productPrice'})).text
            if 'Sold' in cardPrice:
                continue
        else:
            continue

        cardId = card.find('img')['src'].split('=')[-1]
        cardPrice = float(cardPrice.strip().replace('$', ''))
        cardQty = 1
        cardStatus = card.find('p').text.split('-')[0].strip()
        if 'foil' in cardStatus.lower():
            cardType = 'Foil'
            cardStatus = cardStatus.split(' ')[0]
        else:
            cardType = 'Normal'
        cardLink = "https://lamoodcomics.ca" + card.find('a')['href']
        cardTitle = cardTitle.replace('\r\n        ', '')
        #print(cardTitle, cardQty, cardPrice, cardType, cardStatus, cardId, "Wizard Tower")
        dictCards[cardId] = [cardTitle, cardQty, cardPrice, cardStatus, cardType, cardId, cardLink, "Lamood Comics"]





def compareprice():
    lowest_price_cards = []
    min_price = float('inf')
    for card in dictCards:
        # (card)
        if dictCards[card][2] < min_price:
            min_price = dictCards[card][2]
            lowest_price_cards = [[card, dictCards[card][0], dictCards[card][2], dictCards[card][3], dictCards[card][4],
                                   dictCards[card][6], dictCards[card][7]]]
        elif dictCards[card][2] == min_price:
            lowest_price_cards.append([card, dictCards[card][0], dictCards[card][2], dictCards[card][3],
                                       dictCards[card][4], dictCards[card][6],  dictCards[card][7]])
    for card in lowest_price_cards:
        print(card)
        print("\n")


def printCards():
    for card in dictCards:
        print(dictCards[card])


cardname = "Gitrog"
cardname = cardname.lower()

getcardwizard(cardname)
getcardsentry(cardname)
getcardfacetoface(cardname)
getcardgamekeeper(cardname)
getcardlamood(cardname)
compareprice()
#printCards()
print("end")
