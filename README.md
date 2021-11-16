# cache api

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
### REST

![cache_api](cache_api.png?raw=true "cache_api" )

