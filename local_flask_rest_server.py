#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()
import cache_api
import urllib

from flask import Flask, request
from flask_restful import Api, Resource, fields, marshal

app = Flask(__name__, static_url_path="")
api = Api(app)
DEBUG = True


def return_helper(path, return_value):
    cache_item = {'path': path, 'value': return_value}
    cache_item_fields = {
        'uri': fields.Url('cache_item'),
        'path': fields.String,
        'value': fields.String
    }
    return cache_item, cache_item_fields


class CacheAPI(Resource):
    def __init__(self):
        super(CacheAPI, self).__init__()

    def get(self):
        function = request.args.get('function', 'read')
        path = request.args.get('path', None)
        if DEBUG: print(f'===> flask {function=} {request.args=}')
        kwargs = dict(request.args)

        if function in ['data_read', 'cache_create', 'cache_delete', 'cache_head']:
            ...

        elif function in ['function_create']:
            function_body_1 = request.args.get('function_body', 'None')
            function_body = urllib.parse.unquote(function_body_1)
            kwargs['function_body'] = function_body
        else:
            if function.startswith('echo'):
                ...
            elif function == 'random_number':
                kwargs['start'] = int(request.args.get('start', 1))
                kwargs['stop'] = int(request.args.get('stop', 100))
            elif function.startswith('test'):
                ...
            elif function == 'filelist':
                ...
            elif function == 'stats_cache_item':
                ...
            elif function == 'stats_cache':
                ...
            elif function == 'pi':
                ...
            else:
                return f'unknown function: {function}'

        return_value = cache_api.function_router(**kwargs)
        cache_item, cache_item_fields = return_helper(path, return_value)
        valid = True  # todo
        return {'return': marshal(cache_item, cache_item_fields)} if valid else {'error': return_value}


api.add_resource(CacheAPI, '/cache/api/v1.0/', endpoint='cache_item')

if __name__ == '__main__':
    app.run(debug=True)
