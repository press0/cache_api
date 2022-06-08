import timeit

from cache_api import data_read, access_time


def main(cache):
    '''
    Read 3 files from 2 storage locations, S3 and the S: drive; that's 6 reads
    Each file is read twice, the second read is cached; that's 12 reads total
    '''
    print(f'{cache.keys()=}')

    for storage_class in ['s3', 'sd']:

        for file in ['1MB.bin', '10MB.bin', '100MB.bin']:

            for cached in [False, True]:
                start_time = timeit.default_timer()
                data_read(path=file, storage=storage_class)
                print(f'{file=} {storage_class=} {cached=} {access_time(start_time)=}')
