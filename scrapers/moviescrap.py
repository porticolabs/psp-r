from datetime import datetime, timedelta
import time
import logging
import moviescraper
import dbmanager

def main():
    logging.basicConfig(level=logging.INFO)

    start = time.time()
    db = dbmanager.DBManager()
    ms = moviescraper.MovieScraper()

    status,movie,director,actores = ms.scrap_movie("tt2668134",True)
    if (status == 200):
        #print (backdrop)
        #print (poster)
        logging.info ("Titulo: {}".format(movie.titulo))
        logging.info ("urlPoster: {}".format(movie.urlPoster))
        #logging.info ("Argumento: {}".format(movie.argumento))
        logging.info ("Tagline: {}".format(movie.tagline))
        logging.info ("Director: {}".format(director.nombre))
        for ac in actores:
            logging.info ("Actor: {} ({})".format(ac.nombre, ac.personaje))
        
        dm = dbmanager.DBManager()
        result = dm.insertMovieFull(movie=movie,director=director,actores=actores)
        if (result):
            print("Insertada la película, director y actores/personajes")
        else:
            print("No se pudo insertar la película, director y actores/personajes")
    else:
        print ("Error en scrap de pelicula")

    stop = time.time()
    print("Tiempo de ejecución: {0}".format(timedelta(seconds=stop-start)))
    

if __name__ == '__main__':
    main()