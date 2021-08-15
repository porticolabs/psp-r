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
            recomendation_item = None
            if req_type == "book":
                recomendation_item = self.db.getRandomBook()
                logger.debug(msg = "Getting random BOOK: {book}".format(book=recomendation_item), tweetID=self.tweet.ID)
            elif req_type == "movie":
                recomendation_item = self.db.getRandomMovie()
                
                logger.debug(msg = "Getting random MOVIE: {movie}".format(movie=recomendation_item), tweetID=self.tweet.ID)
            elif req_type == "series":
                recomendation_item = self.db.getRandomSerie()
                logger.debug(msg = "Getting random SERIES: {serie}".format(serie=recomendation_item), tweetID=self.tweet.ID)
            else: #categorias no preocesadas "comic","game","music","magazine","illustration","website","channel"
                text = "Lo lamento {user}! Todavía estoy completando mi base de datos para poder recomendarte lo que me pedís.".format(user=self.tweet.user)
                mediaURL = "https://media.giphy.com/media/euCJCm6hKzbMc/giphy.gif"
                logger.debug(msg = "Request type not found: "+req_type, tweetID=self.tweet.ID)
                logger.debug(msg = "Returning default message: "+text, tweetID=self.tweet.ID)
                return text,mediaURL,HTTP_204_NO_CONTENT

            text = message.format(recommendation=recomendation_item["title"],year=recomendation_item["published"],author=recomendation_item["author"])
            mediaURL = recomendation_item["mediaURL"]
            full_text = "{salute}, {text}".format(salute=salute,text=text)
            return full_text,mediaURL,recomendation_item,HTTP_200_OK
        except Exception as e:
            logrecord = logger.error(tweetID=self.tweet.ID)
            return {"location":logrecord["location"],"module":logrecord["module"],"error":logrecord["errormsg"]},"",None,HTTP_500_INTERNAL_SERVER_ERROR

    def getRecommendation(self):
        text,mediaURL,recomendation_item,statusCode = self.buildRandomResponse()
        if statusCode == HTTP_200_OK or statusCode == HTTP_204_NO_CONTENT:
            recomendation = Recommendation(
                originID = self.tweet.ID, 
                text = text, 
                mediaURL = mediaURL,
                title = recomendation_item["title"],
                published = recomendation_item["published"],
                author = recomendation_item["author"]
                )
            logger.info(msg="Got a recommendation",tweet=self.tweet,recommendation=text)        
            return {"recommendation":recomendation},statusCode
        else:
            return {"error":text},statusCode