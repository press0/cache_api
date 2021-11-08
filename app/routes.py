from functools import lru_cache
from flask import abort, jsonify

from app import app

files = [
    {
        'id': 1,
        'content': u'Buy groceries'
    },
    {
        'id': 2,
        'content': u'Learn Python'
    }
]


@app.route('/')
@app.route('/cache/')
@app.route('/index/')
def index():
    return "Hello from cache"


@app.route('/cache/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_cache(file_id):
    file = [file for file in files if file['id'] == file_id]
    if len(file) == 0:
        abort(404)
    return jsonify({'task': file[0]})


@lru_cache
def count_vowels(sentence):
    return sum(sentence.count(vowel) for vowel in 'AEIOUaeiou')


@app.route('/miguel/')
def miguel():
    return "Hello from Miguel's microblog!"
