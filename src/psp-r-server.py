'''
Server Web que implementará la API de PSP.
Por el momento es simplemente un sandbox para hacer algunas
pruebas de las librerías de Python y otros conceptos.
'''
import logging
import uvicorn
import os

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse
from rich import inspect, print
from dbmanager import DBManager
from recommendator import Tweet, Recommendation, Recommendator

logging.basicConfig(level=logging.INFO)

db = DBManager(
    host=os.getenv('PB_DB_HOST','http://localhost'),       # HOST
    port=os.getenv('PB_DB_PORT',2480),              # PORT
    user=os.getenv('PB_DB_USER','admin'),           # USER
    password=os.getenv('PB_DB_PASS','admin')        # PASSWORD
    )
app = FastAPI()

@app.post("/recommendation",response_class=JSONResponse)
async def getRecommendation(tweet : Tweet = Body(..., embed=True)) -> Recommendation:
    recomendator = Recommendator(db=db,tweet=tweet)
    return recomendator.getRecommendation()

    

if __name__ == "__main__":
    uvicorn.run("psp-r-server:app", host="0.0.0.0", port=int(os.getenv('PB_LISTENING_PORT',8000)), reload=True)
