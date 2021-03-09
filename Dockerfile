###################
### Python Base ###
###################
FROM python:3.7-alpine3.12 as virtualenv

# Set src dirs
ENV APP_DIR=/srv/app
ENV WHEEL_DIR=${APP_DIR}/venv/wheels

    # Create a local user and group to run the app
RUN mkdir -p ${APP_DIR} \
 && apk add --update --no-cache build-base \
 && pip install virtualenv \
 && cd ${APP_DIR} && virtualenv --symlinks -p /usr/local/bin/python venv

COPY ./src /srv/app

WORKDIR /srv/app

RUN . ./venv/bin/activate \
 && ${APP_DIR}/venv/bin/pip wheel --wheel-dir=${WHEEL_DIR} -r requirements.txt \
 && find / -type f \( -name *.c -o -name *.pxd -o -name *.pyd \) -exec rm -rf {} \;

FROM python:3.7-alpine3.12

LABEL maintainer="labs@portico.net.ar"
# Set src dirs
ENV APP_DIR=/srv/app 
ENV WHEEL_DIR=${APP_DIR}/venv/wheels

ENV PB_DB_HOST=http://localhost \
    PB_DB_PORT=2480 \
    PB_DB_USER=admin \
    PB_DB_PASS=admin \
    PB_LISTENING_PORT=8000

COPY --from=virtualenv ${APP_DIR} ${APP_DIR}
COPY docker-scripts/entrypoint.sh /

WORKDIR /

RUN addgroup -g 1001 -S portico \
 && adduser -u 1001 -h ${APP_DIR} -H -D -S -G portico portico \
 && mkdir -p ${APP_DIR} \
 && chown -R 1001:1001 ${APP_DIR}

USER 1001

RUN cd ${APP_DIR} \
 && . ./venv/bin/activate \
 && ${APP_DIR}/venv/bin/pip install --no-index --find-links=${WHEEL_DIR} -r requirements.txt

EXPOSE 2480

ENTRYPOINT ["/entrypoint.sh"]