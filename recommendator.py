import random
from typing import List, Optional
from pydantic import BaseModel
from dbmanager import DBManager

# Define las clases para pedir recomendaciones y para enviarlas
class Tweet (BaseModel):
    ID : int
    text : str
    user : str
    request : List

class Recommendation (BaseModel):
    originID : str
    text : str
    mediaURL : str
    
class Recommendator:
    tweet : Tweet = None
    db : DBManager = None

    def __init__ (self, db : DBManager, tweet : Tweet):
        self.tweet = tweet
        self.db = db

    def buildRandomResponse(self):
        print (self.tweet.request)
        if (len(self.tweet.request) > 1):
            req_type = random.choice(self.tweet.request)
        else:
            req_type = self.tweet.request[0]
        req_type = req_type.lower()
        text  = ""
        mediaURL = ""
        salute, message = self.db.getRandomResponseMessage(req_type)
        salute = salute.format(user=self.tweet.user)
        req_found = True
        if req_type == "book":
            book = self.db.getRandomBook()
            # Reemplazar los tags por los contenidos
            text = message.format(recommendation=book["title"],year=book["published"],author=book["author"])
            mediaURL = book["mediaURL"]
        elif req_type == "movie":
            movie = self.db.getRandomMovie()
            # Reemplazar los tags por los contenidos
            text = message.format(recommendation=movie["title"],year=movie["published"],author=movie["author"])
            mediaURL = movie["mediaURL"]
        elif req_type == "series":
            serie = self.db.getRandomSerie()
            # Reemplazar los tags por los contenidos
            text = message.format(recommendation=serie["title"],year=serie["published"],author=serie["author"])
            mediaURL = serie["mediaURL"]
        else: #categorias no preocesadas "comic","game","music","magazine","illustration","website","channel"
            text = "Lo lamento {user}! Todavía estoy completando mi base de datos para poder recomendarte lo que me pedís.".format(user=self.tweet.user)
            mediaURL = "https://media.giphy.com/media/euCJCm6hKzbMc/giphy.gif"
            return text,mediaURL

        full_text = "{salute}, {text}".format(salute=salute,text=text)
        return full_text,mediaURL

    def getRecommendation(self):
        text,mediaURL = self.buildRandomResponse()
        recomendation = Recommendation(
            originID = self.tweet.ID, 
            text = text, 
            mediaURL = mediaURL
            )

        return {"recommendation":recomendation}