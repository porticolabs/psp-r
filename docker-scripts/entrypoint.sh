#!/bin/sh -e 

cd ${APP_DIR}

. ./venv/bin/activate

exec uvicorn psp-r-server:app --host 0.0.0.0