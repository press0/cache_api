import cache_api
import urllib

from flask import Flask, request
from flask_restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__, static_url_path="")
api = Api(app)


'''
cannot handle new functions 
'''
class CacheAPI(Resource):
    def __init__(self):
        super(CacheAPI, self).__init__()

    def get(self):
        function = request.args.get('function', 'read')
        path = request.args.get('path', None)
        options = request.args.get('options', None)
        message = request.args.get('message', None)
        start = int(request.args.get('start', 1))
        stop = int(request.args.get('stop', 100))
        key = request.args.get('key', None)
        function_name = request.args.get('function_name', 'None')
        function_body_1 = request.args.get('function_body', 'None')
        function_body = urllib.parse.unquote(function_body_1)
        print('------')
        print(f'{function=} {path=} {function_name=}')
        print(f'{options=} {message=} {start=} {stop=} {key=}')
        print(f'{function_body_1=}')
        print(f'{function_body=}')
        print('------')
        if function in ['cache_read', 'cache_create', 'cache_delete', 'cache_head', 'function_create']:
            return_value = cache_api.function_router(function=function, path=path, options=options,
                                                     function_name=function_name, function_body=function_body)
            cache_item = {'path': path, 'value': return_value}
            cache_item_fields = {
                'uri': fields.Url('cache_item'),
                'path': fields.String,
                'value': fields.String
            }
        else:
            return_value = None
            if function == 'random_number':
                return_value = cache_api.function_router(function, start, stop)
            elif function in ['echo', 'echo1', 'echo2']:
                return_value = cache_api.function_router(function, message)
            elif function == 'stats_cache_item':
                return_value = cache_api.function_router(function, key)
            elif function == 'stats_cache':
                return_value = cache_api.function_router(function)
            cache_item = {'value': return_value}
            cache_item_fields = {
                'uri': fields.Url('cache_item'),
                'value': fields.String
            }

        valid = True  # todo: ???
        return {'return': marshal(cache_item, cache_item_fields)} if valid else {'error': return_value}


api.add_resource(CacheAPI, '/cache/api/v1.0/', endpoint='cache_item')

if __name__ == '__main__':
    app.run(debug=True)
