from datetime import datetime, timedelta
import time
import logging
import epublibrescraper


def main():
    logging.basicConfig(level=logging.WARNING)

    start = time.time()
    # Libro 627: Ready Player One
    # ONLINE
    url = epublibrescraper.getBookUrl(627)
    # LOCAL
    #url = "test-data/ready-player-one.html"
    epub = epublibrescraper.EPubLibreScraper(url)
    libro,autor = epub.scrap()
    if (libro is not None and autor is not None):    
        print(libro.__dict__)
        print(autor.__dict__)
    else:
        print ("No se pudo obtener el libro indicado")
    stop = time.time()

    print("Tiempo de ejecución: {0}".format(timedelta(seconds=stop-start)))
    

if __name__ == '__main__':
    main()