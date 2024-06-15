# Domino Tools


[**The Domino Model API** serves code as a low-latency web service.
](https://dominodatalab.github.io/api-docs/)

Enable business teams to share data and functionality as a WebService API in seconds.

Table of Contents

1. Data API, fast data access
2. Function API, fast function deployment
3. Examples

## 1 Data API
The Data API provides sub-second access to user-defined data 

 - storage types: AWS S3 and Microsoft Windows Network Drives 
 - file types: parquet, json, binary
 - options: caching, performance


## 1.1 AWS S3
Read data from a configured AWS bucket and prefix

Domino Model API: 
```
{ "function":"data_read", "path":"10MB.bin", "storage:"s3" }
```
Function API: 
```
data_read( {"path":"10MB.bin", "storage:"s3"} )
```

## 1.2  Microsoft Windows 
Read data from a Microsoft Windows Network Drive 

Domino Model API: 
```
{ "function":"data_read", "path":"10MB.bin", "storage:"sd" }
```
Function API: 
```
data_read( {"path":"10MB.bin", "storage:"sd"} )
```


## 2 Function API
The Function API deploys user-defined functions.

 - immediate live load deployment
 - no Model API server restarts, downtime, lost memory

## 2.1 user-defined functions 

User-defined function files should include a main function
```
def main(cache, kwargs):
```


## 2.2 deploy user-defined functions 

Domino Model API: 
```
{ "function":"function_create", "function_name":"udf", "function_file":"udf.py" } 
```
Function API: 
```
function_create( {"function_name":"udf", "function_file":"udf.py"} )
```


## 2.3 call user-defined functions

Domino Model API: 
```
{ "function":"udf", kwargs }
```
Function API: 
```
udf(kwargs)
```

## 3 Examples
The above APIs are demonstrated below use the Domino client [domino_client.py](domino_client.py).
### Domino client
``````
domino_client.py '{Domino_API_JSON}'
`````` 
Note: The Domino client requires:
 - 'requests' module installed
 - DOMINO_ENDPOINT environment variable
 
### 3.1 read AWS S3 data
This example shows a WebService reading user-defined data from AWS S3

``````
domino_client.py '{ "function": "data_read", "path":"test/1MB.bin", "storage":"s3" }'
`````` 
### 3.2 read Microsoft Network drive data
This example shows a WebService reading user-defined data from a Windows Network Drive

``````
domino_client.py '{ "function": "data_read", "path":"test/1MB.bin", "storage":"sd" }'
`````` 
### 3.3 [random number generator](function/random_number.py)
This example shows off deploying a user-defined function and calling it as a WebService.

``````
domino_client.py '{ "function":"function_create", "function_name":"random_number", "function_file":"function/random_number.py" }'
domino_client.py '{ "function":"random_number",   "start":1, "stop":100 }'
`````` 
### 3.4 [π calculator](function/pi.py)
This example shows off deploying a complex user-defined function and calling it as a WebService.

``````
domino_client.py '{ "function":"function_create", "function_name":"pi", "function_file":"function/pi.py" }'
domino_client.py '{ "function":"pi", "significant_digits":'9' }'
`````` 
### 3.5 [performance tester](function/performance_test.py)
This example shows off deploying a complex user-defined function consuming user-defined data and calling it as a WebService.

``````
domino_client.py '{ "function":"function_create", "function_name":"performance_test", "function_file":"function/performance_test.py" }' 
domino_client.py '{ "function":"performance_test" }'
`````` 

| Storage Type            | 1 MB file      | 10 MB file      | 100 MB file |
|-------------------------|----------------|-----------------|-----------|
| Microsoft Network drive | 0.6 seconds           | 0.8 seconds     | 7 seconds |
| AWS S3                  | 5.7 seconds    | 12 seconds      | 13 seconds |
| Cache                   | 0.0001 seconds | 0.0001  seconds | 0.0001 seconds |

WebService data access times