import cache_api

from flask import Flask, request
from flask_restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__, static_url_path="")
api = Api(app)


class CacheAPI(Resource):
    def __init__(self):
        super(CacheAPI, self).__init__()

    def get(self):
        path = request.args.get('path', None)
        command = request.args.get('command', 'read')
        options = request.args.get('options', None)
        function = request.args.get('function', None)
        message = request.args.get('message', "hello world")
        start = int(request.args.get('start', 1))
        stop = int(request.args.get('stop', 100))
        key = request.args.get('key', None)
        print('------')
        print(f'{path=}')
        print(f'{command=}')
        print(f'{options=}')
        print(f'{function=}')
        print(f'{message=}')
        print(f'{start=}')
        print(f'{stop=}')
        print(f'{key=}')
        print('------')

        if function is None:
            if command in ['read', 'create', 'delete', 'head']:
                return_value = cache_api.function_router(module_name=command, path=path, options=options)

            cache_item = {'path': path, 'value': return_value}
            cache_item_fields = {
                'uri': fields.Url('cache_item'),
                'path': fields.String,
                'value': fields.String
            }

        else:
            if function == 'random_number':
                return_value = cache_api.function_router(function, start, stop)
            elif function == 'say_hello':
                return_value = cache_api.function_router(function, message)
            elif function == 'cache_item_stats':
                return_value = cache_api.function_router(function, key)
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
