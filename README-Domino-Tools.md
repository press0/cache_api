# Domino Tools

User-defined data and function APIs

 - fast data access from Domino 
 - easy function deployment to Domino


## Data API
The Data API provides access to user-defined data, sub-second 

## Function API
The Function API deploys user-defined functions in one second

## Domino client
``````
python domino_client.py <JSON>
``````

### access AWS S3 data
```json
{ "function": "cache_read",   "path": "10MB.bin", "storage="s3"}
```
### access On Premise S: drive data
```json
{ "function": "cache_read",   "path": "10MB.bin", "storage="sd"}
```

### deploy functions 
```json
'{ "function":"function_create", "function_name":"holdings", "function_file":"function/holdings.py" } '
``````
### execute functions
```json
'{ "function":"holdings" } '
``````
### local testing
``````
python local_test_server.py
``````

