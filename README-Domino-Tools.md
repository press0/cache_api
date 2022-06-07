# Domino Tools

User-defined data and function APIs

 - fast data access 
 - easy function deployment

Data is accessible from either:
 - external Domino APIs
 - internal user-defined functions
 

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#Data API">Data API</a></li>
     <li><a href="#Function API">Function API</a></li>
     <li><a href="#Domino local client">Domino local client</a></li>
     <li><a href="#AWS S3 data access">AWS S3 data access</a></li>
     <li><a href="#On-Premise S: Drive data access">On-Premise S: Drive data access</a></li>
    <li><a href="#Deploy user-defined functions">Deploy user-defined functions</a></li>
    <li><a href="#Execute user-defined functions">Execute user-defined functions</a></li>
    <li><a href="#Local testing">Local testing</a></li>
    <li><a href="#Examples">Examples</a></li>
  </ol>
</details>

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
```json
Domino API: { "function": "read",   "path": "10MB.bin", "storage="s3"}
```
```python
Function API: read(path="10MB.bin", storage="s3")
```


## On-Premise S: Drive data access 
```json
Domino API:{ "function": "read",   "path": "10MB.bin", "storage="sd"}
```
```python
Function API: read(path="10MB.bin", storage="sd")
```
S: drive access requires a SNOW ticket 
## deploy user-defined functions 
```json
{ "function":"function_create", "name":"user_defined_function", "file":"user_defined_function.py" } 
``````

## execute user-defined functions
```json
Domino API: { "function":"user_defined_function" ...parameters}
``````
```python
Function API: user_defined_function(...parameters)
```

## local testing
``````
python local_server.py
``````

## Examples

## Perf Test Suite
