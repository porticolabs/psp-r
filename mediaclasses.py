

class Libro:
    paginas : int = None
    publicado : int = None
    sinopsis : str = None
    titulo : str = None
    urlDownload : str = None
    urlPortada : str = None
    def __init__ (self,titulo,paginas=None,publicado=None,sinopsis=None,urlDownload=None,urlPortada=None):
        self.titulo = titulo
        self.paginas = paginas
        self.publicado = publicado
        self.sinopsis = sinopsis
        self.titulo = titulo
        self.urlDownload = urlDownload
        self.urlPortada = urlPortada

class Autor:
    nombre : str = None
    urlEpubLibre : str = None
    def __init__ (self, nombre, urlEpubLibre=None):
        self.nombre = nombre
        self.urlEpubLibre = urlEpubLibre

class Pelicula:
    titulo : str = None
    anio : str = None
    argumento : str = None
    id : str = None
    imdb_id : str = None
    tagline : str = None
    urlPoster : str = None
    def __init__ (self,titulo,id,anio=None,argumento=None,tagline=None,imdb_id=None,urlPoster=None):
        self.titulo = titulo
        self.id = id
        self.anio = anio
        self.argumento = argumento
        self.tagline = tagline
        self.imdb_id = imdb_id
        self.urlPoster = urlPoster

class Serie:
    titulo : str = None
    anio : str = None
    argumento : str = None
    id : str = None
    imdb_id : str = None
    tagline : str = None
    urlPoster : str = None
    def __init__ (self,titulo,id,anio=None,argumento=None,tagline=None,imdb_id=None,urlPoster=None):
        self.titulo = titulo
        self.id = id
        self.anio = anio
        self.argumento = argumento
        self.tagline = tagline
        self.imdb_id = imdb_id
        self.urlPoster = urlPoster

# TODO: Posiblemente película y serie deban heredar de una clase comun

class Actor:
    nombre : str = None
    personaje : str = None
    def __init__ (self,nombre,personaje:str=None):
        self.nombre = nombre
        self.personaje = personaje

class Cita:
    pass

class Director:
    nombre : str = None
    def __init__ (self,nombre):
        self.nombre = nombre

class Genero:
    pass

class Personaje:
    nombre : str = None
    def __init__ (self,nombre):
        self.nombre = nombre


