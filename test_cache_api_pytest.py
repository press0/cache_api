import cache_api as c
import pandas as pd


def test_random_number_function_in_range():
    start = 1
    stop = 10
    return_val = c.run(function='random_number', start=start, stop=stop)
    print(return_val)
    assert start < return_val < stop


def test_echo_function():
    message = 'hello'
    return_val = c.run(function='echo', message=message)
    print(return_val)
    assert return_val == message


def test_cache_create_type_unsupported():
    return_val = c.run(function='cache_create', path='file1.snappy.parq')
    print(return_val)
    assert return_val == {'exception': 'file type .parq not yet supported'}


def test_cache_create_type_supported():
    return_val = c.run(function='cache_create', path='file1.snappy.parquet')
    print(return_val)
    assert return_val == {'result': 'success'}


def test_cache_read():
    c.run(function='cache_create', path='file1.snappy.parquet')
    return_val = c.run(function='cache_read', path='file1.snappy.parquet')
    assert return_val == {'result': 'success'}


def test_stats_cache_item():
    c.run(function='cache_create', path='file1.snappy.parquet')
    return_val = c.run(function='stats_cache_item', key='file1.snappy.parquet')
    assert return_val.startswith("<class 'pandas.core.frame.DataFrame'>")


def test_stats_cache():
    return_val = c.run(function='stats_cache')
    assert 'file1.json' in return_val
    assert 'file3.json' in return_val
