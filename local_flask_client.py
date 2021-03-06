#!/usr/bin/env python3
import requests
import json
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
endpoint = 'http://127.0.0.1:5000/cache/api/v1.0/'

if __name__ == "__main__":
    cli_input = json.loads(sys.argv[1])
    print(f'{cli_input=}')

    if cli_input['function'] == 'function_create':
        function_file_name = cli_input["function_file"]
        print(f'{function_file_name=}')
        function_file = open(function_file_name, "r")
        print(f'{function_file=}')
        function_file_data = function_file.read()
        function_file.close()
        function_body = requests.utils.quote(function_file_data)
        print(f'{function_file_data=}')
        print(f'{function_body=}')
        cli_input.pop('function_file')
        cli_input['function_body'] = function_body
        print(f'{cli_input=}')

    response = requests.get(endpoint, params=cli_input)

    print(f'{response.status_code=}')
    print(f'{response.headers=}')
    # print(f'{response.text=}')
    print(f'========>{response.json()=}')
    # print(f'{response.json()["value"]["value"]=}')

# todo: add cache param
# todo: compile(code_str, 'test.py', 'exec')

'''
examples
    '{ "function":"function_create", "function_name":"filelist", "function_file":"function/filelist.py" } '
    '{ "function":"function_create", "function_name":"test3", "function_file":"function/test.py" } '
    '{ "function":"echo",            "message":"hello" } '
    '{ "function":"test2",           "q":"123" } '
    '{ "function":"random_number",   "start":"1", "stop":"100" } '
    '{ "function":"data_read", "path":"test/1MB.bin"} '
    

    function_file_name = cli_input["function_file"]
    function_file = open(function_file_name, "r")
    response = requests.post(endpoint, files={"function_file": function_file})

'''
