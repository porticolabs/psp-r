# README.MD

## Environment Variables

The API uses environment variables to configure itself. All variables has default values.

```python
{
    "PB_DB_HOST" : "http://localhost",      # OrientDB Host
    "PB_DB_PORT" : "2480",                  # OrientDB Port
    "PB_DB_USER" : "admin",                 # OrientDB Username
    "PB_DB_PASS" : "admin",                 # OrientDB Password
    "PB_LISTENING_PORT" : "8000"            # UVICORN (Web server) Connection Port
}
```

## Endpoint

The API publishes only one endpoint by now

```http
POST /recommendation
```

The body for this request is

```json
{
    "tweet": {
        "ID":"754839457894237843587",
        "text": "Che @porticocba, que tal algo para leer? #quieroscifi",
        "user":"Lalo_Landa",
        "request": ["movie"]
    }
}
```

Full HTTP Request

```http
POST http://localhost:8000/recommendation HTTP/1.1

{
    "tweet": {
        "ID":"754839457894237843587",
        "text": "Che @porticocba, que tal algo para leer? #quieroscifi",
        "user":"Lalo_Landa",
        "request": ["movie"]
    }
}

```

## Documentation

The server generates the API documentation dinamically, on demand. The documentation is accesible by the URL

```
http://server/docs 
or 
http://server/redoc
```
>Example: http://localhost:8000/docs
