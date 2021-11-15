import cache_api

from flask import Flask, request
from flask_restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__, static_url_path="")
api = Api(app)


class CacheAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('path', type=str, location='json')
        self.reqparse.add_argument('command', type=str, location='json')
        self.reqparse.add_argument('content', type=str, location='json')
        super(CacheAPI, self).__init__()


    def get(self):
        path = request.args.get('path', None)
        command = request.args.get('command', 'read')
        options = request.args.get('options', None)
        return_val = cache_api.get(path, command, options)

        cache_item = {'path': path, 'content': return_val}
        valid = True  # todo: ???
        return {'cache_item': marshal(cache_item, cache_item_fields)} if valid else {'error': return_val}

cache_item_fields = {
    'uri': fields.Url('cache_item'),
    'path': fields.String,
    'content': fields.String
}

api.add_resource(CacheAPI, '/cache/api/v1.0/', endpoint='cache_item')

if __name__ == '__main__':
    app.run(debug=True)
