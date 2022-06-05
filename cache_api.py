import json
import os
import os.path
import shutil
import sys
import glob

import boto3
import timeit
import pandas as pd
from pathlib import Path
import importlib
import urllib
import random
from enum import Enum

DEBUG = True

LOCAL_DATA_DIR = os.getenv('LOCAL_DATA_DIR', 'data/')
LOCAL_FUNCTION_DIR = os.getenv('LOCAL_FUNCTION_DIR', 'function/')

REMOTE_STORAGE = os.getenv('REMOTE_STORAGE', './data_fake_remote/')

AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_DATA_DIR = os.getenv('AWS_DATA_DIR')
AWS_FUNCTION_DIR = os.getenv('AWS_FUNCTION_DIR')

if __name__ != '__main__':
    assert len(AWS_BUCKET_NAME) != 0
    assert len(AWS_DATA_DIR) != 0
    assert len(AWS_FUNCTION_DIR) != 0


class StorageType(Enum):
    s3 = 1
    sd = 2


class FileType(Enum):
    json = 1
    parquet = 2
    bin = 3


class ReturnType(Enum):
    meta = 1
    data = 2


def make_deep_directory(string_path):
    path = Path(string_path)
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


def get_cache_item_from_remote_file(path, storage_type):
    destination = get_key(path, storage_type)
    make_deep_directory(destination)

    if storage_type == StorageType.s3.name:
        return get_cache_item_from_remote_file_s3(path, storage_type)
    elif storage_type == StorageType.sd.name:
        return get_cache_item_from_remote_file_sd(path, storage_type)
    else:
        print(f'{storage_type=} is not supported')
        return None


def get_cache_item_from_remote_file_sd(path, storage_type):
    destination = get_key(path, storage_type)
    start_time = timeit.default_timer()
    print(f'copy remote {REMOTE_STORAGE + path} to local {destination}')
    try:
        shutil.copy(REMOTE_STORAGE + path, destination)
        print(f'received from S drive: {destination} {access_time(start_time)}')
        return get_cache_item_from_local_file(destination)
    except Exception as e:
        print(f'exception {e}')
        return None


def get_cache_item_from_remote_file_s3(path, storage_type):
    destination = get_key(path, storage_type)
    start_time = timeit.default_timer()
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                          )
        print(f'copy s3://{AWS_BUCKET_NAME}/{AWS_DATA_DIR}{path} to local file {destination}')
        s3.download_file(AWS_BUCKET_NAME, AWS_DATA_DIR + path, destination)
        print(f'received from s3: {destination} {access_time(start_time)}')
        return get_cache_item_from_local_file(destination)
    except Exception as e:
        print(f'exception {e}')
        return None


def get_key(kwargs):
    path = kwargs.get('path')
    storage_type = kwargs.get('storage_type', StorageType['s3'].name)
    return get_key(path, storage_type)


def get_key(path, storage_type):
    return f'{LOCAL_DATA_DIR}{storage_type}/{path}'


def get_cache_item_from_local_file(destination):
    file_extension = Path(destination).suffix[1:]

    if file_extension == FileType.json.name:
        try:
            f = open(destination)
            file_content = json.load(f)
            cache_entry = {destination: file_content}
            return cache_entry
        except Exception as e:
            print(f'exception {e}')
            return None
    elif file_extension == FileType.parquet.name:
        try:
            file_content = pd.read_parquet(destination, engine='pyarrow')
            cache_entry = {destination: file_content}
            return cache_entry
        except Exception as e:
            print(f'exception {e}')
            return None
    elif file_extension == FileType.bin.name:
        try:
            with open(destination, mode='rb') as file:
                file_content = file.read()
                cache_entry = {destination: file_content}
                return cache_entry
        except Exception as e:
            print(f'exception {e}')
            return None


def validate_file_extension(path):
    if path is None or len(path) < 3:
        valid = False
        return_val = {'exception': f'bad path {path}'}
    else:
        valid = True
        return_val = None
    return valid, return_val


def validate_file_exists(destination):
    if os.path.isfile(destination):
        return True, None
    else:
        return False, f'file does not exist {destination}'


def evict_cache_entry(destination):
    del cache[destination]
    print(f'cache entry evicted {destination}')
    valid, return_val = validate_file_exists(destination)
    if valid:
        valid, return_val = delete_file(destination)
        if valid:
            print(f'file deleted {destination}')
        else:
            print(f'file not deleted {destination} {return_val}')
    else:
        print(f'{return_val}')
        return valid, return_val
    print(f'{return_val}')
    return valid, return_val


def delete_file(destination):
    try:
        os.remove(destination)
        return True, None
    except OSError as e:
        return False, f'error deleting file {destination} {e}'


def debug(valid, return_val):
    if DEBUG:
        print(f'valid:{valid} return_val:{return_val}')


def cache_delete(kwargs):
    path = kwargs.get('path')
    storage_type = kwargs.get('storage_type', StorageType['s3'].name)
    destination = get_key(path, storage_type)
    if destination in cache:
        valid, return_val = evict_cache_entry(destination)
    else:
        valid = False
        return_val = 'cache_item not found'
    if valid:
        return_val = {'cache_item deleted': destination}
        debug(valid, return_val)
    return return_val if valid else {'error': return_val}


def access_time(start_time):
    data_access_time = timeit.default_timer() - start_time
    format_float = "{:.12f}".format(data_access_time)
    expo_number = "{:e}".format(data_access_time)
    return f'{format_float} seconds ({expo_number})'


def read(kwargs):
    cache_read(kwargs)
    destination = get_key(kwargs)
    return cache.get(destination)


def to_bool(string_bool):
    return True if string_bool.lower() == 'true' else False


def cache_read(kwargs):
    path = kwargs.get('path')
    storage_type = kwargs.get('storage', StorageType['s3'].name)
    return_type = kwargs.get('return', ReturnType['meta'].name)
    cache_option = to_bool(kwargs.get('cache', 'true'))
    time_option = to_bool(kwargs.get('time', 'true'))
    destination = get_key(path, storage_type)
    file_type = Path(destination).suffix[1:]
    start_time = timeit.default_timer()
    valid = True

    if storage_type not in [e.name for e in StorageType]:
        valid = False
        return_val = {'error': f'{storage_type=} is not a supported storage storage_type: {[e.name for e in StorageType]}'}

    if return_type not in [e.name for e in ReturnType]:
        valid = False
        return_val = {'error': f'{return_type=} is not a supported return type: {[e.name for e in ReturnType]}'}

    if file_type not in [e.name for e in FileType]:
        valid = False
        return_val = {'error': f'{file_type=} is not a supported file type: {[e.name for e in FileType]}'}

    if valid and destination in cache:
        return_val = cache.get(destination)
        print('cache hit, key:' + f'{destination}, time: {access_time(start_time)} ')
    elif valid:
        cache_item = get_cache_item_from_local_file(destination)
        if cache_item is not None:
            cache.update(cache_item)
            return_val = cache.get(destination)
            print(f'cache updated from local file, key: {destination} {access_time(start_time)}')
        else:
            cache_item = get_cache_item_from_remote_file(path, storage_type)
            if cache_item is not None:
                cache.update(cache_item)
                return_val = cache.get(destination)
            else:
                valid = False
                return_val = {'Error: ' + f'{destination}'}
    debug(valid, return_val)

    if valid and return_type == 'meta' and time_option:
        return_val = {'result': 'success ' + access_time(start_time)}
    elif valid and return_type == 'meta':
        return_val = {'result': 'success'}

    return return_val


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


def builtin_functions(function, kwargs):
    if DEBUG: print(f'===> builtin_functions {function=} {kwargs=}')
    if function in ['cache_read', 'cache_create', 'cache_delete']:
        return_val = globals()[function](kwargs)
    elif function in ['function_create']:
        return_val = globals()[function](kwargs.get('function_name'), kwargs.get('function_body'))
    elif function in ['cache_head']:
        return_val = globals()[function](kwargs.get('path'), kwargs.get('options'))
    return return_val


def custom_functions(function, args):
    if DEBUG: print(f'===> custom_functions {function=} {args=}')
    full_module_name = 'function.' + function
    return_val = False
    try:
        module = importlib.import_module(full_module_name)
        function_ref = getattr(module, 'main')
        return_val = function_ref(cache, *args)
    except Exception as e:
        print(f'Exception: {function=} {e}')

    return return_val


def function_router(function, *args, **kwargs):
    if DEBUG: print(f'===> function_router {function=} {args=} {kwargs=}')
    if function in ['cache_read', 'cache_create', 'cache_delete', 'cache_head', 'function_create']:
        return_val = builtin_functions(function, kwargs)
    else:
        return_val = custom_functions(function, args)
    print(f'<=== {return_val=}')
    print(f'')
    return return_val


def test(function, *args, **kwargs):
    return function_router(function, *args, **kwargs)


def function_create(function_name, function_body):
    if DEBUG: print(f'===> function_create {function_name=} {function_body=}')

    try:
        compile(function_body, f'{function_name}.py', 'exec')
    except Exception as e:
        print(f'Exception {e=}')
        return False
    with open(LOCAL_FUNCTION_DIR + f'{function_name}.py', 'w') as file:
        file.write(function_body)
    return True


dummy_content1 = {'foo': 'bar', 'foobar': 1}
dummy_content2 = {'foo': 'bar', 'nested': dummy_content1}
cache = {'file1.json': dummy_content1, 'file3.json': {'foo': 'bar', 'nested': dummy_content2}}

if __name__ == '__main__':

    AWS_DATA_DIR = 'json/'
    AWS_BUCKET_NAME = 'press0-test'
    AWS_FUNCTION_DIR = 'json/'

    test('random_number', 1, 100)
    test('echo', 'hello world')

    quit()

    run(function='cache_create', path='file1.snappy.parq')
    run(function='cache_create', path='file1.snappy.parquet')
    run(function='cache_read', path='file1.snappy.parquet')
    run(function='stats_cache_item', key='file1.snappy.parquet')
    run(function='stats_cache')
    #### run(function='cache_delete', path='file1.snappy.parquet')
    function_name = 'test' + str(random.randint(10, 20))
    test_local_python_function_file = LOCAL_FUNCTION_DIR + function_name + '.py'
    quoted_function_body = 'def%20main%28cache%2C%20q%2C%20w%29%3A%0A%20%20%20x%3D2%0A%20%20%20return%20q'
    function_body = urllib.parse.unquote(quoted_function_body)
    run(function='function_create', function_name=function_name, function_body=function_body)
    result_val = run(function='test', q='q says hello', w='w says hello')
    assert result_val == 'q says hello'
    if os.path.exists(test_local_python_function_file):
        os.remove(test_local_python_function_file)
    result_val = run(function='test123', q='q says hello', w='w says hello')
    assert not result_val
