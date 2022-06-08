# Domino Tools

Data and Function APIs

 - fast data access 
 - fast function deployment

Kick-starter use case: develop fast data and functions 

## 1 Data API
The Data API provides access to user-defined data, sub-second 

 - storage types: AWS S3; on-premise S: drive 
 - file types: parquet, json, binary
 - options: caching, timing

Data is accessible from either:
 - standard Domino API
 - Function API (user-defined functions)


## 1.1 AWS S3 data access 
Read data from a configured AWS bucket and prefix

Domino API: 
```
{ "function": "data_read",   "path": "10MB.bin", "storage="s3"}
```
Function API: 
```
data_read(path="10MB.bin", storage="s3")
```

## 1.2 S: Drive data access 
Read data from an S: Drive configured folder

Domino API: 
```
{ "function": "data_read",   "path": "10MB.bin", "storage="sd"}
```
Function API: 
```
data_read(path="10MB.bin", storage="sd")
```
Note: S: drive access requires a SNOW ticket 

## 2 Function API
The Function API deploys user-defined functions in seconds

## 2.1 user-defined functions 

User-defined functions must include a main function
```
def main(cache, args):
```


## 2.2 deploy user-defined functions 

Domino API: 
```
{ "function":"function_create", "function_name":"udf", "function_file":"udf.py" } 
```
Function API: 
```
function_create(function_name, function_file)
```


## 2.3 call user-defined functions

Domino API: 
```
{ "function":"udf", kwargs}
```
Function API: 
```
udf(args)
```

## 3 Examples
The above APIs are demonstrated below.
### Domino client
``````
domino_client.py ' <Domino_API_JSON> '
`````` 
Note: The Domino client requires:
 - 'requests' module
 - domino_endpoint 
 
### 3.1 read AWS S3 data
``````
domino_client.py '{ "function": "cache_read", "path": "10MB.bin" storage="s3") '
`````` 
### 3.2 read S: drive data
``````
domino_client.py '{ "function": "cache_read", "path": "10MB.bin" storage="sd") '
`````` 
### 3.3 random generator
``````
domino_client.py '{ "function":"function_create", "function_name":"random_number", "function_file":"random_number.py" } '
domino_client.py '{ "function":"random_number",   "start":1, "stop":100 } ' 
`````` 
### 3.4 π calculator 
``````
domino_client.py '{ "function":"function_create", "function_name":"pi", "function_file":"pi.py" } '
domino_client.py '{ "function":"pi", "significant_digits":'9' } '
`````` 
### 3.5 performance tester 
The time it takes Domino to read data into memory is measured
``````
domino_client.py '{ "function":"function_create", "function_name":"performance_test", "function_file":"performance_test.py" } '
domino_client.py '{ "function":"performance_test"} '
`````` 

