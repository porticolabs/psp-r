import logging
import sys
import linecache
import datetime
from typing import List
from modelclasses import Tweet
from fastapi.encoders import jsonable_encoder

class LogEntry:
    level : str = ""
    msg : str = ""
    recommendation : str = ""
    time : str = ""
    tweetID : str = ""
    tweetRequestTypes : List = None
    tweetText : str = ""
    tweetUser : str = ""
    def __init__ (self, msg : str, level: str = "debug", tweetID : str = "", tweet : Tweet = None,  recommendation : str = ""):
        self.level = level
        self.msg = msg
        self.recommendation = recommendation
        self.time = datetime.datetime.utcnow().isoformat() + 'Z'
        if tweet:
            self.tweetID = str(tweet.ID)
            self.tweetRequestTypes = tweet.request
            self.tweetText = tweet.text
            self.tweetUser = tweet.user
        else:
            self.tweetID = str(tweetID)

class ErrorEntry:
    level : str = ""
    location : str = ""
    errormsg : str = ""
    time : str = ""
    tweetID : str = ""
    def __init__ (self, errormsg : str, level: str = "error", location : str = "", tweetID : str = ""):
        self.level = level
        self.location = location
        self.errormsg = errormsg
        self.time = datetime.datetime.utcnow().isoformat() + 'Z'
        self.tweetID = str(tweetID)

class PSPLogger:
    def getLogger(self):
        logger = logging.getLogger('psp-r')
        if not len(logger.handlers):
            logger.setLevel(level=logging.DEBUG)
            formatter = logging.Formatter("%(message)s")
            console = logging.StreamHandler();
            console.setFormatter(formatter)
            logger.addHandler(console) 
        return logger

    def getCurrentException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        location = "FILE: {file} (line: {line})".format(file=filename,line=lineno)
        return location, str(exc_obj)

    def debug(self, msg: str, tweetID: str="", tweet: Tweet=None, recommendation: str=""):
        logger = self.getLogger()
        logrecord = jsonable_encoder (LogEntry(msg=msg, level="debug", tweetID=tweetID, tweet=tweet, recommendation=recommendation))
        logger.debug(logrecord)

    def info(self, msg: str, tweetID: str="", tweet: Tweet=None, recommendation: str=""):
        logger = self.getLogger()
        logrecord = jsonable_encoder (LogEntry(msg=msg, level="debug", tweetID=tweetID, tweet=tweet, recommendation=recommendation))
        logger.info(logrecord)

    def error(self, errormsg: str="", location: str="", tweetID: str=""):
        logger = self.getLogger()
        # Si no viene mensaje de error obtener los datos automaticamente
        if not errormsg:
            location, error = self.getCurrentException()
            errormsg = error
        logrecord = jsonable_encoder (ErrorEntry(errormsg=errormsg, level="error", location=location, tweetID=tweetID))
        logger.error(logrecord)
        return logrecord
