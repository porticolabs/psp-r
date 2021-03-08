#!/bin/sh
echo "Iniciando servidor PSP-R"

uvicorn psp-r-server:app --reload 