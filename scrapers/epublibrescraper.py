from bs4 import BeautifulSoup
from mediaclasses import Libro, Autor
import requests

BOOK_DETAIL_URL = "https://www.epublibre.org/libro/detalle/"

class EPubLibreScraper:
    url = None
    online = True

    def __init__ (self,url: str, online=True):
        self.url = url
        self.online = online

    def get_title (self,soup):
        div = soup.find(id='titulo_libro')
        return div.string.strip()

    def get_author (self,soup):
        autor_div = soup.find('div',class_='negrita aut_sec')
        autor_link = autor_div.find('a')
        autor = autor_link.contents[0]
        link = autor_link.attrs['href']
        return (autor,link);

    def get_sinopsis (self,soup):
        pass

    def get_portada_url (self,soup):
        img_portada = soup.find('img',id='portada')
        img_url = img_portada.attrs['src']
        return img_url

    def get_book_data (self,soup):
        # Encontrar primero el panel de detalle
        div_detalle = soup.find('div',class_='cab_detalle')
        # dentro del panel buscar el texto 'Páginas'
        paginas_text = div_detalle.find('td',string='Páginas:')
        # Una vez encontrado buscar el 'sibling' que contiene el número
        paginas_nro = paginas_text.next_sibling.next_sibling
        cant_paginas = paginas_nro.string
        publicado_text = div_detalle.find('td',string='Publicado en:')
        publicado_nro = publicado_text.next_sibling.next_sibling
        publicado = publicado_nro.string 	
        return (cant_paginas,publicado)

    def get_sinopsis (self,soup):
        div_detalle = soup.find('div',class_='detalle')
        div_sinopsis = div_detalle.find('div',class_='negrita',string='Sinopsis')
        div_ali_justi = div_sinopsis.next_sibling
        span = div_ali_justi.find('span')
        sinopsis = span.text.replace("\n","").replace("'","")
        return sinopsis

    def get_download_link (self,soup):
        a_download_link = soup.find('a',id='en_desc')
        download_link = a_download_link.attrs['href']
        return download_link

    def scrap_book(self,source : str):
        sp = BeautifulSoup(source,"lxml")
        titulo = self.get_title(sp)    
        autor, link = self.get_author(sp)
        portada_url = self.get_portada_url(sp)
        cant_paginas,publicado = self.get_book_data(sp)
        sinopsis = self.get_sinopsis(sp)
        download_link = self.get_download_link(sp)
        # Crear y devolver un Libro y su correspondiente autor
        libro = Libro(titulo,cant_paginas,publicado,sinopsis,download_link,portada_url)
        autor = Autor(autor,link)
        #time.sleep(2)

        return (libro,autor)

    def scrap(self):
        source = None
        url = self.url
        if (self.online):
            # ONLINE
            response = requests.get(url)
            if (response.status_code == 200):
                source = response.text
        else:
            # LOCAL
            source = open(url)

        # Evaluar si Source es vacío (eso implica error)
        if (source != None):
            libro,autor = self.scrap_book(source)
        else:
            libro = None
            autor = None

        return (libro,autor)

def getBookUrl (book_number: int):
    return BOOK_DETAIL_URL+str(book_number)