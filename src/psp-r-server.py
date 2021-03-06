'''
Server Web que implementará la API de PSP.
Por el momento es simplemente un sandbox para hacer algunas
pruebas de las librerías de Python y otros conceptos.
'''
import asyncio
import logging
import signal
import uvicorn
import os
import multiprocessing

from multiprocessing import Process
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from rich import inspect, print
from dbmanager import DBManager
from recommendator import Tweet, Recommendation, Recommendator

# global process variable
proc = None

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
    recommendator = Recommendator(db=db,tweet=tweet)
    recommendation,statusCode = recommendator.getRecommendation()
    response = JSONResponse(content=jsonable_encoder(recommendation),status_code=statusCode)
    
    return response

def run(): 
    """
    This function to run configured uvicorn server.
    """
    uvicorn.run("debug-server:app", 
        host=os.getenv('PB_LISTENING_IP',"0.0.0.0"), 
        port=int(os.getenv('PB_LISTENING_PORT',8000)), 
        reload=True,
        log_config = None
        )

def start():
    """
    This function to start a new process (start the server).
    """
    global proc
    # create process instance and set the target to run function.
    # use daemon mode to stop the process whenever the program stopped.
    proc = Process(target=run, args=(), daemon=True)
    proc.start()


def stop(): 
    """
    This function to join (stop) the process (stop the server).
    """
    global proc
    # check if the process is not None
    if proc: 
        # join (stop) the process with a timeout setten to 0.25 seconds.
        # using timeout (the optional arg) is too important in order to
        # enforce the server to stop.
        proc.join(0.25)

if __name__ == "__main__":
    # La siguiente linea la sugieren para poder depurar interactivamente desde vscode
    # multiprocessing.set_start_method('spawn', True)
    
    # to start the server call start function.
    start()
    
    # to stop the server call stop function.
    loop = asyncio.get_event_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(stop())
        )