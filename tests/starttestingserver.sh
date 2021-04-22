#!/bin/sh -e 

cd ../src
exec uvicorn debug-server:app --host 0.0.0.0 --reload