# cache api

[Cache-Aside](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside) resources from a System of Record such as AWS.



![cache_api](cache_api.png?raw=true "cache_api" )

### nomenclature
``````
data locality - co-location of data and compute resources. shared memory.
system of record (SOR) - primary data source
cache - fast access copy of SOR data
data locality optimized copy of SOR data  
``````

### env vars
``````
LOCAL_DATA_DIR   # cache root path in a container or development machine  
AWS_BUCKET_NAME  # System of Record AWS S3 bucket 
AWS_DATA_DIR     # System of Record AWS root path 
AWS ACCESS KEYS  # System of Record AWS IAM keys 
``````

### run
``````
python cache_api_flask_rest_server.py
``````

### test
``````
curl  http://127.0.0.1:5000/cache/api/v1.0/?path=2/file1.snappy.parquet

cache hit, key:2/file1.snappy.parquet, time: 0.000000754138 seconds (7.541385e-07) 
valid:True return_val:                   cusip  price  security_type trade_date
0                  Unit:    NaN            NaN       None
1            Multiplier:   1.00            NaN       None
2              Currency:    NaN            NaN       None
3    Unique Identifier:     NaN            NaN       None
4            Time Period    NaN            NaN       None
..                   ...    ...            ...        ...
776              2017-07   2.32            NaN       None
777              2017-08   2.21            NaN       None
778              2017-09   2.20            NaN       None
779              2017-10   2.36            NaN       None
780              2017-11   2.35            NaN       None

``````

``````
curl  http://127.0.0.1:5000/cache/api/v1.0/?path=2/file1.snappy.parquet\&
``````


### GET parameters
``````

create  same as Read
read    ?command=read\&path=file1.json
update  same as delete then read   
delete  ?command=delete\&path=file1.json
head    ?command=head\&path=file1.json
``````

### POST form
``````
{
    "data": {
    "command" = "read",
    "path" = "file1.json"
    }
}
``````

### use case

![use case](cache-usecase-diagram.png?raw=true "cache_api" )


### roadmap cache futures

- delete method
- thread_pool 
- @compute_result, @athena_result, @sql_result
- @lru_cache
- eviction policy
