import json
import os
import os.path
import sys
import glob
import boto3
import pandas as pd
from pathlib import Path
from pathlib import PurePosixPath

DEBUG = True

LOCAL_DATA_DIR = os.getenv('LOCAL_DATA_DIR')
AWS_DATA_DIR = os.getenv('AWS_DATA_DIR')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')


def get_cache_item_from_remote_file(string_path):
    """ :param string_path: relative path including file name under LOCAL_DATA_DIR """

    path = Path(LOCAL_DATA_DIR + '/' + string_path)

    print(f'{path=}')
    print(f'{path.name=}')
    print(f'{path.exists()=}')

    parent = Path(path).parent
    print(f'{parent=}')
    print(f'{parent.name=}')
    print(f'{parent.exists()=}')

    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)

    print(f'{parent=}')
    print(f'{parent.name=}')
    print(f'{parent.exists()=}')

    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                          )
        print('copy remote object s3://' +
              f'{AWS_BUCKET_NAME + "/" + AWS_DATA_DIR + string_path}' +
              ' to local file ' + f'{LOCAL_DATA_DIR + string_path}')

        s3.download_file(AWS_BUCKET_NAME, AWS_DATA_DIR + string_path, LOCAL_DATA_DIR + string_path)

        return get_cache_item_from_local_file(string_path)
    except Exception as e:
        print(f'local file not found {string_path} {e}')
        return None


def get_cache_item_from_local_file(path):
    """ :param path: relative path including file name under LOCAL_DATA_DIR """
    file_name, file_extension = os.path.splitext(path)
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
    valid = False
    return_val = ''
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
    del s3cache[path]
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


def debug(valid, return_val):
    if DEBUG:
        print(f'valid:{valid} return_val:{return_val}')


def delete(path):
    if path in s3cache:
        valid, return_val = evict_cache_entry(path)
    else:
        valid = False
        return_val = 'cache_item not found'
    if valid:
        return_val = {'cache_item deleted': path}
        debug(valid, return_val)
        return return_val if valid else {'error': return_val}


def read(path):
    if path in s3cache:
        valid = True
        return_val = s3cache.get(path)
        print('cache hit, key=' + f'{path}')
    else:
        cache_item = get_cache_item_from_local_file(path)
        if cache_item is not None:
            s3cache.update(cache_item)
            valid = True
            return_val = s3cache.get(path)
            print('cache update from local, key=' + f'{LOCAL_DATA_DIR + path}')
        else:
            cache_item = get_cache_item_from_remote_file(path)
            if cache_item is not None:
                s3cache.update(cache_item)
                valid = True
                return_val = s3cache.get(path)
                print('cache update from remote, key=' + f'{AWS_DATA_DIR + path}')
            else:
                valid = False
                return_val = 'remote file not found ' + f'{AWS_DATA_DIR + path}'
                print(return_val)
    debug(valid, return_val)
    if valid and Path(path).suffix == '.json':
        return return_val.to_json()
    else:
        return return_val if valid else {'error': return_val}


def head(path, options):
    telemetry_path = os.path.join(os.getcwd(), '') if path is None else os.path.join(path, '')  # trailing slash
    telemetry_recursive_option = False if options is None else True
    return_val = {}
    cache = []
    local_data_files = []
    telemetry = []
    for key in s3cache.keys():
        cache.append(key)
    return_val['cache'] = cache
    return_val['memory'] = sys.getsizeof(s3cache)
    for filename in glob.iglob(LOCAL_DATA_DIR + '**', recursive=True):
        local_data_files.append(filename)
    return_val['local_data_files'] = local_data_files
    for filename in glob.iglob(telemetry_path + '**', recursive=telemetry_recursive_option):
        telemetry.append(filename)
    return_val['telemetry'] = telemetry
    return return_val


def get(path=None, command='read', options=None):
    print(f'{path=} {command=} {options=}')
    if command == 'head':
        return head(path, options)
    valid, return_val = validate_file_extension(path)
    print(f'valid {valid} path {path} command {command} options {options}')
    if not valid:
        return return_val
    if command == 'read':
        return read(path)
    if command == 'delete':
        return delete(path)


dummy_content1 = {'foo': 'bar', 'foobar': 1}
dummy_content2 = {'foo': 'bar', 'nested': dummy_content1}
s3cache = {'file1.json': dummy_content1, 'file3.json': {'foo': 'bar', 'nested': dummy_content2}}

if __name__ == '__main__':
    if len(sys.argv) == 2:
        get(sys.argv[1])
elif len(sys.argv) == 3:
    get(sys.argv[1], sys.argv[2])
else:
    print('unexpected')
