from typing import ItemsView
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np
from datetime import datetime

#Clase que más adelante voy a usar para agregar más portales de retailers: walmart, cencosud, exito, etc.
class Retailer():

    def __init__(self,retailer):
        self.retailer =retailer

    def urlRetailer(self,retailer):
        if retailer == 'Selecto Easy Shop':
            retailerPage = "https://www.selectoseasyshop.com"
        
        return retailerPage

#Clase para indicar donde buscar cada atributo que quiero extraer de cada portal, por ahora solo tiene atributos del único retailer codeado
class htmlComposition():

    def __init__(self) :
        pass

    def webSearcher(self, retailer):
        if retailer == 'Selecto Easy Shop':
            htmlSearcher = "fp-input-search"
            
        return htmlSearcher

    def firstMatch (self,retailer):
        if retailer == 'Selecto Easy Shop':
            matchUrl = 'div.fp-item-name a[href]'

        return matchUrl

    def itemDescHtml (self,retailer):
        if retailer =='Selecto Easy Shop':
            itemDescription="fp-page-header fp-page-title"
        return itemDescription

    def itemDetailsHtml (self,retailer):
        if retailer == 'Selecto Easy Shop':
            itemDet = "fp-item-description-content"
        return itemDet

    def itemSkuHtml (self,retailer):
        if retailer == 'Selecto Easy Shop':
            itemSkuUpc = "fp-margin-top fp-item-upc"
        return itemSkuUpc

    def itemSkuHtml2 (self,retailer):
        if retailer == 'Selecto Easy Shop':
            itemSkuUpc = "fp-margin-top fp-item-upc fp-item-upc-no-desc"
        return itemSkuUpc


    def itemNotFound (self,retailer):
        if retailer == 'Selecto Easy Shop':
            itmNotFound = "fp-product-not-found fp-not-found"
        return itmNotFound

    def imageHtml (self,retailer):
        if retailer == 'Selecto Easy Shop':
            imgHtml = 'fp-item-image fp-item-image-large'
        return imgHtml

    def imageNotFound(self,retailer):
        if retailer == 'Selecto Easy Shop':
            imageUrlNot = 'https://ipcdn.freshop.com/resize?url=https://images.freshop.com/5554875/09c1c58d54ae3e309c8cfce88eb1a764_large.png&width=512&type=webp&quality=80'

        return imageUrlNot

#Función main, contiene un cronometro para medir el performance y llama a las clases de retailer y htmlcomp
def Main (retailer):
    start_time = datetime.now()
    scrappingRetailer = Retailer(retailer)
    urlRetailer = scrappingRetailer.urlRetailer(retailer)
    htmlAttr = htmlComposition()
    #Creo lista vacía para almacenar los resultados a medida los obtengo
    pd.set_option('display.max_colwidth', 0)
    listSku=[]
    listDescription=[]
    listDetails = []
    listImagen = []
    listItemsNotFound = []
    #Abro listado provisto por el usuario
    dfItems = pd.read_excel(r'C:\Users\floral02\Documents\Projects\Web Scraping\ITEMS SELECTOS.xlsx')
    listItems = dfItems['BAR CODE'].tolist()

    path=r"C:\Program Files\ChromeDriver\chromedriver.exe"
    driver =webdriver.Chrome(path)
    driver.get(urlRetailer)
    time.sleep(10)
    #ciclo que ejecuta los pasos para cada registro del listado provisto por el usuario
    for item in listItems:
        htmlSearcher = htmlAttr.webSearcher(retailer)
        firstMatch = htmlAttr.firstMatch(retailer)
        itemDescHtml = htmlAttr.itemDescHtml(retailer)
        itemDetailsHtml = htmlAttr.itemDetailsHtml(retailer)
        itemSkuHtml = htmlAttr.itemSkuHtml(retailer)
        itemSku2Html = htmlAttr.itemSkuHtml2(retailer)
        itemImage = htmlAttr.imageHtml(retailer)
        imageUrlNot = htmlAttr.imageNotFound(retailer)

        search = driver.find_element_by_name(htmlSearcher)
        search.send_keys(item)
        search.send_keys(Keys.RETURN)
        randomSleep = np.random.choice([13, 12, 15])
        time.sleep(randomSleep)
        pageSearchResults = BeautifulSoup(driver.page_source, 'lxml')
        productNotFound = pageSearchResults.find("div",attrs={"class":"fp-product-not-found fp-not-found"})
        if productNotFound:
            search = driver.find_element_by_name(htmlSearcher)
            search.send_keys(Keys.CONTROL+"a")
            search.send_keys(Keys.DELETE)
            listItemsNotFound.append(item) #Si no encuentro el registro lo guardo en otra lista para buscarlo en google images del país del retailer
            continue
        linkItem = pageSearchResults.select(firstMatch)
        linksItem =[str(linkItem['href']) for linkItem in linkItem]
        linkItemFirst = linksItem[0]
        urlMatch = urlRetailer + linkItemFirst
        driver.get(urlMatch)
        randomSleep = np.random.choice([13, 12, 15])
        time.sleep(randomSleep)
        pageMatch = BeautifulSoup(driver.page_source,'lxml')

        itemDesc = pageMatch.find("div",attrs={"class":itemDescHtml})
        itemDetails = pageMatch.find('div',attrs={"class":itemDetailsHtml})
        itemSku =pageMatch.find("div",attrs={"class":itemSkuHtml})
        imageUrl = pageMatch.find("div",attrs={"class":itemImage})
        imageUrl = imageUrl.find('img')
        imageUrl = imageUrl['src']
        if imageUrl == imageUrlNot:
            listItemsNotFound.append(item) #Si no encuentro la foto, guardo el registro en la otra lista para buscarlo en google images del país del retailer
            continue
        imageUrl = '<img src="'+ imageUrl + '" width="80" >'

        if not itemSku:
            itemSku =pageMatch.find("div",attrs={"class":itemSku2Html})
        #Guardo los resultados
        itemSku = itemSku.text
        itemSku = int("".join(c for c in itemSku if c.isdigit()))
        listSku.append(itemSku)
        listDescription.append(itemDesc.text)
        listDetails.append(itemDetails.text)
        listImagen.append(imageUrl)

        #imprimo los resultados en un html, que me deja previsualizar las imagenes mejor que un Excel
        df=pd.DataFrame(list(zip(listSku,listDescription,listDetails,listImagen)),columns=['SKU','DESCRIPTION','DETAILS','IMAGE'])
        df.to_html('test_html.html', escape=False)

###Agregado para la busqueda en google

    if listItemsNotFound:
        print(listItemsNotFound)
        dfDescItemsNotF = dfItems[dfItems['BAR CODE'].isin(listItemsNotFound)]
        listBarcodesNotFound  = dfDescItemsNotF['BAR CODE'].tolist()
        listDescsNotFound = dfDescItemsNotF[' ITEM DESCRIPTION'].tolist()
        driver.get("https://www.google.com.pr/imghp?hl=es-419&tab=ri&ogbl")
        time.sleep(6)

        for barcode,descripcion in zip(listBarcodesNotFound,listDescsNotFound):

            search = driver.find_element_by_name("q")
            search.send_keys(descripcion)
            search.send_keys(Keys.RETURN)
            randomSleep = np.random.choice([9, 12, 15])
            time.sleep(randomSleep)
            pageMatch = BeautifulSoup(driver.page_source,'lxml')
            imageUrl = pageMatch.find("div",attrs={"class":"bRMDJf islir"})
            imageUrl = imageUrl.find('img')
            imageUrl = imageUrl['src']
            imageUrl = '<img src="'+ imageUrl + '" width="80" >'
            randomSleep = np.random.choice([9, 12, 15])
            time.sleep(randomSleep)
            listSku.append(barcode)
            listDescription.append(descripcion)
            listDetails.append('Found On Google')
            listImagen.append(imageUrl)
            df=pd.DataFrame(list(zip(listSku,listDescription,listDetails,listImagen)),columns=['SKU','DESCRIPTION','DETAILS','IMAGE'])
            df.to_html('test_html.html', escape=False)
            search = driver.find_element_by_name("q")
            search.send_keys(Keys.CONTROL+"a")
            search.send_keys(Keys.DELETE)


    end_time = datetime.now()
    executionTime = (end_time - start_time)
    print('Finalizado en ', executionTime)







Main('Selecto Easy Shop')



