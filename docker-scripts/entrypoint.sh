#!/bin/sh -e 

cd ${APP_DIR}

. ./venv/bin/activate

exec uvicorn psp-r-server:app