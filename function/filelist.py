from os import listdir
from os.path import isfile, join

def main(cache):
	mypath = 'function'
	files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	return files

