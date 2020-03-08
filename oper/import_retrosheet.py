# this python script is to import the retrosheet files
from os import path, mkdir, remove
import urllib.request
from zipfile import ZipFile as zf
import sys

if len(sys.argv) > 1:

    # create import folder if not available
    if path.exists('import'):
        pass
    else:
        mkdir('import')

    # create landing folder if not available
    if path.exists('import/landing'):
        pass
    else:
        mkdir('import/landing')

    # download file into import/landing folder
    url = 'https://www.retrosheet.org/events/'
    year = sys.argv[1]
    zip_file = year + 'eve.zip'
    urllib.request.urlretrieve(url+zip_file, 'import/landing/'+zip_file)

    # create new folder for the unzipped contents
    if path.exists('import/'+year):
        pass
    else:
        mkdir('import/'+year)

    # unzip contents to the year folder
    with zf('import/landing/'+zip_file) as unzip:
        unzip.extractall('import/'+year)

    # remove landing file
    if path.exists('import/landing/'+zip_file):
        remove('import/landing/'+zip_file)
