import json
import os
import os.path
import sys
import glob
import boto3
import timeit
import pandas as pd
from pathlib import Path
import importlib

DEBUG = False
LOCAL_DATA_DIR = 'data/'
LOCAL_FUNCTION_DIR = 'function/'

AWS_DATA_DIR = os.getenv('AWS_DATA_DIR')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_FUNCTION_DIR = os.getenv('AWS_FUNCTION_DIR')


def make_deep_directory(base_directory, string_path):
    path = Path(base_directory + '/' + string_path)
    parent = Path(path).parent

    if DEBUG:
        print(f'{path=}')
        print(f'{path.name=}')
        print(f'{path.exists()=}')
        print(f'{parent=}')
        print(f'{parent.name=}')
        print(f'{parent.exists()=}')

    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)

    if DEBUG:
        print(f'{parent=}')
        print(f'{parent.name=}')
        print(f'{parent.exists()=}')


def get_cache_item_from_remote_file(path):
    make_deep_directory(LOCAL_DATA_DIR, path)
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                          )
        print('copy remote object s3://' +
              f'{AWS_BUCKET_NAME + "/" + AWS_DATA_DIR + path}' +
              ' to local file ' + f'{LOCAL_DATA_DIR + path}')

        s3.download_file(AWS_BUCKET_NAME, AWS_DATA_DIR + path, LOCAL_DATA_DIR + path)

        return get_cache_item_from_local_file(path)
    except Exception as e:
        print(f'local file not found {path} {e}')
        return None


def get_function_from_remote_file(path):
    make_deep_directory(LOCAL_FUNCTION_DIR, path)
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                          )
        print('copy remote object s3://' +
              f'{AWS_BUCKET_NAME + "/" + AWS_FUNCTION_DIR + path}' +
              ' to local file ' + f'{LOCAL_FUNCTION_DIR + path}')

        s3.download_file(AWS_BUCKET_NAME, AWS_FUNCTION_DIR + path, LOCAL_FUNCTION_DIR + path)

        return True
    except Exception as e:
        print(f'local file not found {path} {e}')
        return False


def get_cache_item_from_local_file(path):
    """ :param path: relative path including file name under LOCAL_DATA_DIR """
    file_extension = Path(path).suffix
    # todo: size, date

    if file_extension == '.json':
        try:
            f = open(LOCAL_DATA_DIR + path)
            file_content = json.load(f)
            cache_entry = {path: file_content}
            return cache_entry
        except Exception as e:
            print(f'local file not found {path}')
            return None
    elif file_extension == '.parquet':
        try:
            file_content = pd.read_parquet(LOCAL_DATA_DIR + path, engine='pyarrow')
            cache_entry = {path: file_content}
            return cache_entry
        except Exception as e:
            print(f'local file not found {path} {e}')
            return None


def validate_file_extension(path):
    if path is None or len(path) < 3:
        valid = False
        return_val = {'exception': f'bad path {path}'}
    else:
        file_extension = Path(path).suffix
        if file_extension not in ['.json', '.parquet']:
            valid = False
            return_val = {'exception': f'file type {file_extension} not yet supported'}
        else:
            valid = True
            return_val = None
    return valid, return_val


def validate_file_exists(path):
    if os.path.isfile(LOCAL_DATA_DIR + path):
        return True, None
    else:
        return False, f'file does not exist {LOCAL_DATA_DIR + path}'


def delete_file(path):
    try:
        os.remove(LOCAL_DATA_DIR + path)
        return True, None
    except OSError as e:
        return False, f'error deleting file {LOCAL_DATA_DIR + path} {e}'


def evict_cache_entry(path):
    del cache[path]
    print(f'cache entry evicted {path}')
    valid, return_val = validate_file_exists(path)
    if valid:
        valid, return_val = delete_file(path)
        if valid:
            print(f'file deleted {path}')
        else:
            print(f'file not deleted {path} {return_val}')
    else:
        print(f'{return_val}')
        return valid, return_val
    print(f'{return_val}')
    return valid, return_val


def debug(valid, return_val):
    if DEBUG:
        print(f'valid:{valid} return_val:{return_val}')


def cache_delete(path):
    if path in cache:
        valid, return_val = evict_cache_entry(path)
    else:
        valid = False
        return_val = 'cache_item not found'
    if valid:
        return_val = {'cache_item deleted': path}
        debug(valid, return_val)
    return return_val if valid else {'error': return_val}


def cache_hit(path):
    start_time = timeit.default_timer()
    return_val = cache.get(path)
    data_access_time = timeit.default_timer() - start_time
    format_float = "{:.12f}".format(data_access_time)
    expo_number = "{:e}".format(data_access_time)
    access_time = f'{format_float} seconds ({expo_number})'
    print('cache hit, key:' + f'{path}, time: {access_time} ')
    return return_val


def cache_read(path):
    if path in cache:
        valid = True
        return_val = cache_hit(path)
    else:
        cache_item = get_cache_item_from_local_file(path)
        if cache_item is not None:
            cache.update(cache_item)
            valid = True
            return_val = cache.get(path)
            print('cache update from local, key:' + f'{LOCAL_DATA_DIR + path}')
        else:
            cache_item = get_cache_item_from_remote_file(path)
            if cache_item is not None:
                cache.update(cache_item)
                valid = True
                return_val = cache.get(path)
                print('cache update from remote, key:' + f'{AWS_DATA_DIR + path}')
            else:
                valid = False
                return_val = 'remote file not found ' + f'{AWS_DATA_DIR + path}'
                print(return_val)
    debug(valid, return_val)
    return {'result': 'success'} if valid else {'error': return_val}


def cache_create(path):
    return cache_read(path)


def cache_head(path=None, options=None):
    telemetry_path = os.path.join(os.getcwd(), '') if path is None else os.path.join(path, '')  # trailing slash
    telemetry_recursive_option = False if options is None else True
    return_val = {}
    tmp_cache = []
    local_data_files = []
    telemetry = []
    for key in cache.keys():
        tmp_cache.append(key)
    return_val['cache'] = tmp_cache
    return_val['memory'] = sys.getsizeof(cache)
    for filename in glob.iglob(LOCAL_DATA_DIR + '**', recursive=True):
        local_data_files.append(filename)
    return_val['local_data_files'] = local_data_files
    for filename in glob.iglob(telemetry_path + '**', recursive=telemetry_recursive_option):
        telemetry.append(filename)
    return_val['telemetry'] = telemetry
    return return_val


def function_register(path):
    """
    :param path: remote path to python function to register
    :return success or failure

    #1 aws s3 cp function_path f's3://{AWS_BUCKET_NAME}/{AWS_FUNCTION_DIR}{path}'
    #2 curl function=function_register, path=function_path
    #3 this function - aws s3 cp s3://{AWS_BUCKET_NAME}/{AWS_FUNCTION_DIR}{path}

    aws s3 cp ~/echo1.py  s3://{AWS_BUCKET_NAME}/json/echo2.py
    curl  http://127.0.0.1:5000/cache/api/v1.0/?function=function_register\&path=echo2.py
    curl  http://127.0.0.1:5000/cache/api/v1.0/?function=echo2\&message=hello_world
    """

    return get_function_from_remote_file(path)


def builtin_functions(function, kwargs):
    path = kwargs.get('path')
    options = kwargs.get('options')
    if function in ['cache_read', 'cache_create', 'cache_delete']:
        valid, return_val = validate_file_extension(path)
        if valid:
            return_val = globals()[function](path)
        else:
            print(f'invalid path {path} ')
    elif function in ['cache_head']:
        return_val = globals()[function](path, options)
    elif function in ['function_register']:
        return_val = globals()[function](path)
    return return_val


def custom_functions(function, args, kwargs):
    full_module_name = 'function.' + function
    # todo: timeit
    return_val = False
    try:
        module = importlib.import_module(full_module_name)
        function_ref = getattr(module, 'main')
        return_val = function_ref(cache, *args, **kwargs)
    except Exception as e:
        print(f'function not found: {function=} {e}')

    return return_val


def function_router(function, *args, **kwargs):
    print(f'===> {function=} {args=} {kwargs=}')
    if DEBUG: print(f'beginning {cache.keys()=}')
    if function in ['cache_read', 'cache_create', 'cache_delete', 'cache_head', 'function_register']:
        return_val = builtin_functions(function, kwargs)
    else:
        return_val = custom_functions(function, args, kwargs)
    if DEBUG: print(f'ending {cache.keys()=}')
    print(f'<=== {return_val=}')
    print(f'')
    return return_val


def run(function, *args, **kwargs):
    return function_router(function, *args, **kwargs)


dummy_content1 = {'foo': 'bar', 'foobar': 1}
dummy_content2 = {'foo': 'bar', 'nested': dummy_content1}
cache = {'file1.json': dummy_content1, 'file3.json': {'foo': 'bar', 'nested': dummy_content2}}

if __name__ == '__main__':
    from local_config import *

    run(function='random_number', start=1, stop=10)
    run(function='echo', message='hello world')
    run(function='cache_create', path='file1.snappy.parq')
    run(function='cache_create', path='file1.snappy.parquet')
    run(function='cache_read', path='file1.snappy.parquet')
    run(function='stats_cache_item', key='file1.snappy.parquet')
    # run(function='cache_delete', path='file1.snappy.parquet')
    run(function='stats_cache')
    run(function='echo1', message='hello - I am not registered')
    run(function='function_register', path='echo1.py')
    run(function='echo1', message='hello - i am registered now')
