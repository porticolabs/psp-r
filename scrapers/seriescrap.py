from datetime import datetime, timedelta
import time
import logging
import seriesscraper
import dbmanager

def main():
    logging.basicConfig(level=logging.INFO)

    start = time.time()
    db = dbmanager.DBManager()
    ss = seriesscraper.SeriesScraper()

    status,serie,director,actores = ss.scrap_serie("tt5651844",True) # Probar con FRINGE
    if (status == 200):
        #print (backdrop)
        #print (poster)
        logging.info ("Titulo: {}".format(serie.titulo))
        logging.info ("urlPoster: {}".format(serie.urlPoster))
        logging.info ("Argumento: {}".format(serie.argumento))
        logging.info ("Tagline: {}".format(serie.tagline))
        # logging.info ("Director: {}".format(director.nombre))
        print (len(actores))
        for ac in actores:
            logging.info ("Actor: {} ({})".format(ac.nombre, ac.personaje))
        
        dm = dbmanager.DBManager()
        result = dm.insertSerieFull(serie=serie,actores=actores)
        if (result):
            print("Insertada la serie y actores/personajes")
        else:
            print("No se pudo insertar la serie, y actores/personajes")  
    else:
        print ("Error en scrap de serie")

    stop = time.time()
    print("Tiempo de ejecución: {0}".format(timedelta(seconds=stop-start)))
    

if __name__ == '__main__':
    main()