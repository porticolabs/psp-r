import json
from logging import exception, log
import logging

from requests.models import HTTPError
from mediaclasses import Director, Actor, Personaje, Pelicula
import requests
from urllib import parse
import pandas as pd
import scraperconstants as ct

class MovieScraper:
    apiUrl = None
    online = True
    imagesUrl = None
    sci_fi_movie_id = None
    sci_fi_tv_id = None

    def __init__ (self,url: str=ct.THEMOVIEDB_API_URL, online=True):
        self.apiUrl = url
        self.online = online
        self.getConfiguration()
        self.getSciFiIds()

    def __apicall__ (self, endpoint: str, params: dict=None):
        try:
            url = parse.urljoin(THEMOVIEDB_API_URL,endpoint)
            parameters = {"api_key" : THEMOVIEDB_API_KEY}
            # Si vienen parámetros adicionales, agregarlos a continuacion de la API KEY
            if (params):
                parameters.update(params)
            response = requests.get(url,params=parameters)
            if (response.ok):
                result = json.loads(response.text)
                return response.status_code,result
            else:
                return response.status_code,response.reason
        except Exception as e:
            logging.error(e)
            return None,e.__str__

    def getConfiguration (self):
        try:
            status, result = self.__apicall__(ct.CONFIG_ENDPOINT)
            if (status == 200):
                self.imagesUrl = result["images"]["secure_base_url"]+ct.IMAGE_SIZE
        except Exception as e:
            logging.error(e)

    def getGenres (self,type:str="M"):
        try:
            if (type == "M"):
                status, result = self.__apicall__(ct.GENRES_MOVIES_ENDPOINT)
            else: 
                status, result = self.__apicall__(ct.GENRES_TV_ENDPOINT)
            return status, result
        except Exception as e:
            logging.error(e)

    def getSciFiIds (self):
        status,result = self.getGenres()
        if (status == 200):
            movie_genres = result
        status,result = self.getGenres("T")
        if (status == 200):
            tv_genres = result

        if (movie_genres):
            for record in movie_genres['genres']:
                id = record['id']
                genre = record['name']
                if (genre == "Science Fiction"):
                    self.sci_fi_movie_id = id
                    break;

        if (tv_genres):
            for record in tv_genres['genres']:
                id = record['id']
                genre = record['name']
                if (genre == "Sci-Fi & Fantasy"):
                    self.sci_fi_tv_id = id
                    break;

    def discoverMovies (self,pretty:bool=False):
        try:
            parameters = {"with_genres":self.sci_fi_movie_id,"language":"es-ES"}
            status, result = self.__apicall__(ct.DISCOVER_MOVIE_ENDPOINT,params=parameters)
            if (status == 200):
                if (pretty):
                    result = json.dumps(result,indent=3)
            return status, result
        except Exception as e:
            logging.error(e)

    def getMovieById (self,id:str,pretty:bool=False):
        try:
            parameters = {"language":"es"}
            url = parse.urljoin(ct.MOVIE_ENDPOINT,str(id))
            status, result = self.__apicall__(url,params=parameters)
            if (status == 200):
                if (pretty):
                    result = json.dumps(result,indent=3)
            return status, result
        except Exception as e:
            logging.error(e)

    def getMovieCastCrew (self,id:str,pretty:bool=False):
        try:
            parameters = {"language":"es"}
            url = parse.urljoin(ct.MOVIE_ENDPOINT,str(id)+"/credits")
            status, result = self.__apicall__(url,params=parameters)
            if (status == 200):
                json_cast = result["cast"]
                json_crew = result["crew"]
                df_cast = pd.json_normalize(json_cast)
                df_crew = pd.json_normalize(json_crew)
                if (pretty):
                    indent_spaces = 3
                else:
                    indent_spaces = 0
                cast = df_cast.head(3).filter(["name","character","order"]).to_json(orient="records",indent=indent_spaces)
                crew = df_crew.loc[df_crew['job']=='Director'].filter(["name","job"]).to_json(orient="records",indent=indent_spaces)
            return status, cast, crew
        except Exception as e:
            logging.error(e)

    def getMovieByIMDBId (self,imdbId:str,pretty:bool=False):
        try:
            parameters = {"external_source":"imdb_id","language":"es"}
            url = parse.urljoin(ct.FIND_EXTERNAL_ENDPOINT,imdbId)
            status, result = self.__apicall__(url,params=parameters)
            if (status == 200):
                # Si la encontró, sacar el ID, repetir la consulta y devolver el resultado
                id = result["movie_results"][0]["id"]
                status,result = self.getMovieById(id,pretty)
            return status, result
        except Exception as e:
            logging.error(e)

    def getMovieImageUrl (self,id:str):
        try:
            parameters = {"language":"en"} # Las imágenes se buscan en idioma original
            url = parse.urljoin(ct.MOVIE_ENDPOINT,str(id)+ct.MOVIE_IMAGE_ENDPOINT)
            status, result = self.__apicall__(url,params=parameters)
            backdrop_url = ""
            poster_url = ""
            if (status == 200):
                if (len(result["backdrops"])):
                    backdrop = result["backdrops"][0]["file_path"]
                    backdrop_url = self.imagesUrl+backdrop
                if (len(result["posters"])):
                    poster = result["posters"][0]["file_path"]
                    poster_url = self.imagesUrl+poster
            return status, backdrop_url, poster_url
        except Exception as e:
            logging.error(e)

    def scrap_movie (self,movie_id:str,is_imdb:bool=False):
        if (is_imdb):
            status, movie_data = self.getMovieByIMDBId (imdbId=movie_id)
        else:
            status, movie_data = self.getMovieById (movie_id)
        # Ya tengo los datos generales de la pelicula
        if (status == 200):
            movie_id = movie_data["id"]
            status,cast,crew = self.getMovieCastCrew(movie_id)
            if (status == 200):
                status,backdrop,poster = self.getMovieImageUrl(movie_id)
                if (status == 200):
                    # Armar los objetos con todos los datos y devolverlos
                    movie = Pelicula(
                        movie_data["title"],
                        movie_id,
                        anio=movie_data["release_date"][0:4],
                        argumento=movie_data["overview"],
                        tagline=movie_data["tagline"],
                        imdb_id=movie_data["imdb_id"],
                        urlPoster=poster
                        )
                    
                    director = Director(json.loads(crew)[0]["name"])
                    actores = []
                    #personajes = []
                    for a in json.loads(cast):
                        actor = Actor (a["name"],a["character"])
                        #personaje = Personaje (a["character"])
                        actores.append(actor)
                        #personajes.append(personaje)

                    return status,movie,director,actores#,personajes    

    