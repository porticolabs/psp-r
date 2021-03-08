import json
from logging import exception, log
import logging

from requests.models import HTTPError
from mediaclasses import Director, Actor, Personaje, Pelicula, Serie
import requests
from urllib import parse
import pandas as pd
import scraperconstants as ct

class SeriesScraper:
    apiUrl = None
    online = True
    imagesUrl = None
    sci_fi_movie_id = None
    sci_fi_tv_id = None

    # TODO: Generalizar esto en una superclase
    def __init__ (self,url: str=ct.THEMOVIEDB_API_URL, online=True):
        self.apiUrl = url
        self.online = online
        self.getConfiguration()
        self.getSciFiIds()

    # TODO: Generalizar esto en una superclase
    def __apicall__ (self, endpoint: str, params: dict=None):
        try:
            url = parse.urljoin(ct.THEMOVIEDB_API_URL,endpoint)
            parameters = {"api_key" : ct.THEMOVIEDB_API_KEY}
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

    # TODO: Generalizar esto en una superclase
    def getConfiguration (self):
        try:
            status, result = self.__apicall__(ct.CONFIG_ENDPOINT)
            if (status == 200):
                self.imagesUrl = result["images"]["secure_base_url"]+ct.IMAGE_SIZE
        except Exception as e:
            logging.error(e)

    # TODO: Generalizar esto en una superclase
    def getGenres (self,type:str="M"):
        try:
            if (type == "M"):
                status, result = self.__apicall__(ct.GENRES_MOVIES_ENDPOINT)
            else: 
                status, result = self.__apicall__(ct.GENRES_TV_ENDPOINT)
            return status, result
        except Exception as e:
            logging.error(e)

    # TODO: Generalizar esto en una superclase
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

    def discoverSeries (self,pretty:bool=False):
        try:
            parameters = {"with_genres":self.sci_fi_movie_id,"language":"es-ES"}
            status, result = self.__apicall__(ct.DISCOVER_TV_ENDPOINT,params=parameters)
            if (status == 200):
                if (pretty):
                    result = json.dumps(result,indent=3)
            return status, result
        except Exception as e:
            logging.error(e)

    def getSerieById (self,id:str,pretty:bool=False):
        try:
            parameters = {"language":"es"}
            url = parse.urljoin(ct.TV_ENDPOINT,str(id))
            status, result = self.__apicall__(url,params=parameters)
            if (status == 200):
                if (pretty):
                    result = json.dumps(result,indent=3)
            return status, result
        except Exception as e:
            logging.error(e)

    def getSerieCastCrew (self,id:str,pretty:bool=False):
        try:
            parameters = {"language":"es"}
            url = parse.urljoin(ct.TV_ENDPOINT,str(id)+"/credits")      # TODO: Sacar el /credits como constante
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
                if (json_cast):
                    cast = df_cast.head(3).filter(["name","character","order"]).to_json(orient="records",indent=indent_spaces)
                else:
                    cast = ""
                if (json_crew):
                    crew = df_crew.loc[df_crew['job']=='Director'].filter(["name","job"]).to_json(orient="records",indent=indent_spaces)
                else:
                    crew = ""
            return status, cast, crew
        except Exception as e:
            logging.error(e)

    def getSerieByIMDBId (self,imdbId:str,pretty:bool=False):
        try:
            parameters = {"external_source":"imdb_id","language":"es"}
            url = parse.urljoin(ct.FIND_EXTERNAL_ENDPOINT,imdbId)
            status, result = self.__apicall__(url,params=parameters)
            if (status == 200):
                # Si la encontró, sacar el ID, repetir la consulta y devolver el resultado
                id = result["tv_results"][0]["id"]
                status,result = self.getSerieById(id,pretty)
            return status, result
        except Exception as e:
            logging.error(e)

    def getSerieImageUrl (self,id:str):
        try:
            parameters = {"language":"en"} # Las imágenes se buscan en idioma original
            url = parse.urljoin(ct.TV_ENDPOINT,str(id)+ct.TV_IMAGE_ENDPOINT)
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

    def scrap_serie (self,serie_id:str,is_imdb:bool=False):
        imdb_id = ""
        if (is_imdb):
            # Si es un ID de imdb usarlo porque no viene con los datos de la API
            imdb_id = serie_id
            status, serie_data = self.getSerieByIMDBId (imdbId=serie_id)
        else:
            status, serie_data = self.getSerieById (serie_id)
        # Ya tengo los datos generales de la pelicula
        if (status == 200):
            serie_id = serie_data["id"]
            status,cast,crew = self.getSerieCastCrew(serie_id)
            if (status == 200):
                status,backdrop,poster = self.getSerieImageUrl(serie_id)
                if (status == 200):
                    # Armar los objetos con todos los datos y devolverlos
                    serie = Serie(
                        serie_data["name"],
                        serie_id,
                        anio=serie_data["first_air_date"][0:4],
                        argumento=serie_data["overview"],
                        tagline=serie_data["tagline"],
                        imdb_id=imdb_id,
                        urlPoster=poster
                        )
                    
                    director = None # Los capitulos de las series tienen múltiples directores, no uno
                    actores = []
                    #personajes = []
                    if (cast):
                        for a in json.loads(cast):
                            actor = Actor (a["name"],a["character"])
                            #personaje = Personaje (a["character"])
                            actores.append(actor)
                            #personajes.append(personaje)

                    return status,serie,director,actores#,personajes    

    