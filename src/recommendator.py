import random
import traceback

from pydantic.tools import T
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR

from dbmanager import DBManager
from rich import print, inspect
from fastapi import status
from fastapi.encoders import jsonable_encoder
from psplogger import LogEntry, PSPLogger
from modelclasses import Tweet, Recommendation

logger = PSPLogger()

class Recommendator:
    tweet : Tweet = None
    db : DBManager = None

    def __init__ (self, db : DBManager, tweet : Tweet):
        self.tweet = tweet
        self.db = db

    def buildRandomResponse(self):
        if (len(self.tweet.request) > 1):
            req_type = random.choice(self.tweet.request)
            logger.debug(msg = "Multiple requests: Selecting one: "+req_type)
        else:
            req_type = self.tweet.request[0]
        req_type = req_type.lower()
        text  = ""
        mediaURL = ""
        try:
            salute, message = self.db.getRandomResponseMessage(req_type)
            salute = salute.format(user=self.tweet.user)
            logger.debug(msg = "Getting random salute: "+salute, tweetID=self.tweet.ID)
            logger.debug(msg = "Getting random response message: "+message, tweetID=self.tweet.ID)
            if req_type == "book":
                book = self.db.getRandomBook()
                # Reemplazar los tags por los contenidos
                text = message.format(recommendation=book["title"],year=book["published"],author=book["author"])
                mediaURL = book["mediaURL"]
                logger.debug(msg = "Getting random BOOK: {book}".format(book=book), tweetID=self.tweet.ID)
            elif req_type == "movie":
                movie = self.db.getRandomMovie()
                # Reemplazar los tags por los contenidos
                text = message.format(recommendation=movie["title"],year=movie["published"],author=movie["author"])
                mediaURL = movie["mediaURL"]
                logger.debug(msg = "Getting random MOVIE: {movie}".format(movie=movie), tweetID=self.tweet.ID)
            elif req_type == "series":
                serie = self.db.getRandomSerie()
                # Reemplazar los tags por los contenidos
                text = message.format(recommendation=serie["title"],year=serie["published"],author=serie["author"])
                mediaURL = serie["mediaURL"]
                logger.debug(msg = "Getting random SERIES: {serie}".format(serie=serie), tweetID=self.tweet.ID)
            else: #categorias no preocesadas "comic","game","music","magazine","illustration","website","channel"
                text = "Lo lamento {user}! Todavía estoy completando mi base de datos para poder recomendarte lo que me pedís.".format(user=self.tweet.user)
                mediaURL = "https://media.giphy.com/media/euCJCm6hKzbMc/giphy.gif"
                logger.debug(msg = "Request type not found: "+req_type, tweetID=self.tweet.ID)
                logger.debug(msg = "Returning default message: "+text, tweetID=self.tweet.ID)
                return text,mediaURL,HTTP_204_NO_CONTENT

            full_text = "{salute}, {text}".format(salute=salute,text=text)
            return full_text,mediaURL,HTTP_200_OK
        except Exception as e:
            logrecord = logger.error(tweetID=self.tweet.ID)
            return logrecord,"",HTTP_500_INTERNAL_SERVER_ERROR

    def getRecommendation(self):
        text,mediaURL,statusCode = self.buildRandomResponse()
        if statusCode == HTTP_200_OK or statusCode == HTTP_204_NO_CONTENT:
            recomendation = Recommendation(
                originID = self.tweet.ID, 
                text = text, 
                mediaURL = mediaURL
                )
            logger.info(msg="Got a recommendation",tweet=self.tweet,recommendation=text)        
            return {"recommendation":recomendation},statusCode
        else:
            return {"error":text},statusCode