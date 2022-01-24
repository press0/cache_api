# cache api

[Cache-Aside](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside) resources from a System of Record such as AWS.



![cache_api](cache_api.png?raw=true "cache_api" )

### nomenclature
``````
system of record (SOR) - primary data source
cache - fast access copy of SOR data
data locality - co-location of data and compute resources. shared memory.
``````

### env vars
``````
LOCAL_DATA_DIR   # cache root path in a container or development machine  
AWS_BUCKET_NAME  # System of Record AWS S3 bucket 
AWS_DATA_DIR     # System of Record AWS root path 
AWS ACCESS KEYS  # System of Record AWS IAM keys 
``````

### run api server
``````
python cache_api_flask_rest_server.py
``````

### create cache from S3 objects
``````
curl  http://127.0.0.1:5000/cache/api/v1.0/?command=create\&path=file1.snappy.parquet

{
    "return": {
        "uri": "/cache/api/v1.0/",
        "path": "file1.snappy.parquet",
        "value": "{'result': 'success'}"
    }
}

``````
### create functions
``````python
def main(cache, **args, **kwargs):
``````

### run functions on the cache
``````
time curl  http://127.0.0.1:5000/cache/api/v1.0/?function=cache_item_stats\&key=file1.snappy.parquet | sed 's/\\n/\n/g'

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   513  100   513    0     0  19730      0 --:--:-- --:--:-- --:--:-- 19730
{
    "return": {
        "uri": "/cache/api/v1.0/",
        "value": "(                   cusip  price  security_type trade_date
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

[781 rows x 4 columns], \"<class 'pandas.core.frame.DataFrame'>\
RangeIndex: 781 entries, 0 to 780\
Data columns (total 4 columns):\
 #   Column         Non-Null Count  Dtype  \
---  ------         --------------  -----  \
 0   cusip          781 non-null    object \
 1   price          777 non-null    float64\
 2   security_type  0 non-null      float64\
 3   trade_date     0 non-null      object \
dtypes: float64(2), object(2)\
memory usage: 24.5+ KB\

``````


### GET parameters
``````
# cache management commands
create     same as read
read       command=read\&path=file1.json
update     same as delete + read   
delete     command=delete\&path=file1.json
head       command=head\&path=file1.json

# function execution
function   function=custom_function
parameters custom_parameter=custom_value
``````

### POST form
``````
{
    "data": {
    "command" = "read",
    "path" = "file1.json"
    }
}

{
    "data": {
    "function" = "function_name",
    "parameter_name" = "parameter_value"
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
