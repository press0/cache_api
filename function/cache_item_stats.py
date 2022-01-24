from io import StringIO
import sys


def main(cache, key):
    if key is None:
        # handle all cache keys
        pass

    file_extension = key[key.rindex("."):]
    print(f'{key=}')
    print(f'{file_extension=}')
    print(f'{cache=}')
    item = cache[key]

    if file_extension == '.json':
        print(f'{item=}')
        return item

    if file_extension == '.parquet':
        old_stdout = sys.stdout
        sys.stdout = my_stdout = StringIO()
        item.info()
        sys.stdout = old_stdout
        item_info = my_stdout.getvalue()
        formatted_item_info = item_info.split(sep='\n')
        print('formatted_item_info')
        for s in formatted_item_info:
            print(s)
        return item_info
