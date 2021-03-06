import cache_api as sut
import os
import random
import urllib


def test_random_number_function_in_range():
    start = 1
    stop = 10
    return_val = sut.run(function='random_number', start=start, stop=stop)
    print(return_val)
    assert start < return_val < stop


def test_echo_function():
    message = 'hello'
    return_val = sut.run(function='echo', message=message)
    print(return_val)
    assert return_val == message


def test_cache_create_type_unsupported():
    return_val = sut.run(function='cache_create', path='file1.snappy.parq')
    print(return_val)
    assert return_val == {'exception': 'file type .parq not yet supported'}


def test_cache_create_type_supported():
    return_val = sut.run(function='cache_create', path='file1.snappy.parquet')
    print(return_val)
    assert return_val == {'result': 'success'}


def test_data_read():
    sut.run(function='cache_create', path='file1.snappy.parquet')
    return_val = sut.run(function='data_read', path='file1.snappy.parquet')
    assert return_val == {'result': 'success'}


def test_stats_cache_item():
    sut.run(function='cache_create', path='file1.snappy.parquet')
    return_val = sut.run(function='stats_cache_item', key='file1.snappy.parquet')
    assert return_val.startswith("<class 'pandas.core.frame.DataFrame'>")


def test_stats_cache():
    return_val = sut.run(function='stats_cache')
    assert 'file1.json' in return_val
    assert 'file3.json' in return_val


def test_function_create_and_invoke():
    # assemble
    sut_function_name = 'test' + str(random.randint(10, 20))
    sut_function_file = sut.LOCAL_FUNCTION_DIR + sut_function_name + '.py'

    template_file_name = sut.LOCAL_FUNCTION_DIR + 'test.py'
    print(f'{template_file_name=}')
    template_file = open(template_file_name, "r")
    print(f'{template_file=}')
    template_file_data = template_file.read()
    # template_file_data = 'def%20main%28cache%2C%20q%2C%20w%29%3A%0A%20%20%20x%3D2%0A%20%20%20return%20q'
    template_file.close()
    function_body = urllib.parse.unquote(template_file_data)

    # act
    result_val = sut.run(function='function_create', function_name=sut_function_name, function_body=function_body)

    # assert
    assert result_val

    # act
    result_val = sut.run(function=sut_function_name, q='q says hello', w='w says hello')

    # assert
    assert result_val == 'q says hello'

    if os.path.exists(sut_function_file):
        os.remove(sut_function_file)

    # act
    result_val = sut.run(function='test123', q='q says hello', w='w says hello')

    # assert
    assert not result_val
