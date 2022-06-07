# Domino Tools

User-defined data and function APIs

 - fast data access 
 - easy function deployment

Data is accessible from either:
 - external Domino APIs
 - internal user-defined functions


## Data API
The Data API provides access to user-defined data, sub-second 

 - storage types: AWS S3; on-premise S: drive folder
 - file types: parquet, json, binary
 - options: caching, timing

## Function API
The Function API deploys user-defined functions in seconds

## Domino local client
``````
python domino_client.py ' <JSON> '
``````
 - required module: requests

## AWS S3 data access 
```
Domino API: { "function": "read",   "path": "10MB.bin", "storage="s3"}
```
```
Function API: read(path="10MB.bin", storage="s3")
```


## On-Premise S: Drive data access 
```
Domino API:{ "function": "read",   "path": "10MB.bin", "storage="sd"}
```
```
Function API: read(path="10MB.bin", storage="sd")
```
S: drive access requires a SNOW ticket 
## deploy user-defined functions 
```
{ "function":"function_create", "name":"user_defined_function", "file":"user_defined_function.py" } 
``````

## execute user-defined functions
```
Domino API: { "function":"user_defined_function" ...parameters}
``````
```
Function API: user_defined_function(...parameters)
```

## local testing
``````
python local_server.py
``````

## Examples

## Performance Tests
