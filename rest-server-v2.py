import json
import os
import string
from typing import TextIO

import boto3

from flask import Flask, abort, request
from flask_restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__, static_url_path="")
api = Api(app)

LOCAL_DATA_DIR = os.getenv('LOCAL_DATA_DIR')
AWS_DATA_DIR = os.getenv('AWS_DATA_DIR')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')


def get_cache_item_from_remote_file(path):
    """ :param path: relative path including file name under LOCAL_DATA_DIR    """

    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                      )
    print('copy remote object s3://' +
          f'{AWS_BUCKET_NAME + "/" + AWS_DATA_DIR + path}' +
          ' to local file ' + f'{LOCAL_DATA_DIR + path}')
    s3.download_file(AWS_BUCKET_NAME, AWS_DATA_DIR + path, LOCAL_DATA_DIR + path)
    return get_cache_item_from_local_file(path)


def get_cache_item_from_local_file(path: string):
    """ :param path: relative path including file name under LOCAL_DATA_DIR    """

    try:
        f: TextIO = open(LOCAL_DATA_DIR + path)
        file_content = json.load(f)
        file_item = {'path': path, 'content': file_content}
        return file_item
    except Exception as e:
        print(f'file not found {path}')
        return ''


class CacheAPI(Resource):
    cache_hits = 0
    cache_misses = 0

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('path', type=str, location='json')
        self.reqparse.add_argument('content', type=str, location='json')
        super(CacheAPI, self).__init__()

    def get(self):
        path = request.args.get('path')
        file_name, file_extension = os.path.splitext(path)
        if file_extension != '.json':
            print(f'file type not yet supported {file_extension=}')
            abort(404)
        cache_item = [cache_item for cache_item in s3cache if cache_item['path'] == path]
        if len(cache_item) != 0:
            print('cache hit, key=' + f'{path}')
            return {'cache_item': marshal(cache_item[0], cache_item_fields)}
        else:
            cache_item = get_cache_item_from_local_file(path)
            if len(cache_item) != 0:
                s3cache.append(cache_item)
                print('cache update from local, key=' + f'{LOCAL_DATA_DIR + path}')
                return {'cache_item': marshal(cache_item, cache_item_fields)}
            else:
                cache_item = get_cache_item_from_remote_file(path)
                if len(cache_item) != 0:
                    print('cache update from remote, key=' + f'{AWS_DATA_DIR + path}')
                    s3cache.append(cache_item)
                    return {'cache_item': marshal(cache_item, cache_item_fields)}
                else:
                    print('remote file not found ' + f'{AWS_DATA_DIR + path}')
                    abort(404)

    def delete(self):
        path = request.args.get('path')
        cache_item = [cache_item for cache_item in s3cache if cache_item['path'] == path]
        if len(cache_item) == 0:
            abort(404)
        s3cache.remove(cache_item[0])
        print(f"cache invalidated, key={cache_item[0]['path']}")
        return {'result': True}


cache_item_fields = {
    'uri': fields.Url('cache_item'),
    'path': fields.String,
    'content': fields.String
}

api.add_resource(CacheAPI, '/cache/api/v1.0/s3', endpoint='cache_item')

dummy_content1 = {'foo': 'bar', 'foobar': 1}
dummy_content2 = {'foo': 'bar', 'nested': dummy_content1}
s3cache = [
    {
        'path': 'file1.json',
        'content': dummy_content1
    },
    {
        'path': 'file2.json',
        'content': {'foo': 'bar', 'nested': dummy_content1}
    }
]

if __name__ == '__main__':
    app.run(debug=True)
