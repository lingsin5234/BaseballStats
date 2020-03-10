# this python script is to import the retrosheet files
from os import path, mkdir, remove
import urllib.request
from zipfile import ZipFile as zf
import sys

# if len(sys.argv) > 1:
def import_data(year):

    # create import folder if not available
    if path.exists('baseball/import'):
        pass
    else:
        mkdir('baseball/import')

    # create landing folder if not available
    if path.exists('baseball/import/landing'):
        pass
    else:
        mkdir('baseball/import/landing')

    # download file into import/landing folder
    url = 'https://www.retrosheet.org/events/'
    # year = sys.argv[1]
    zip_file = year + 'eve.zip'
    urllib.request.urlretrieve(url+zip_file, 'baseball/import/landing/'+zip_file)

    # create new folder for the unzipped contents
    if path.exists('baseball/import/'+year):
        pass
    else:
        mkdir('baseball/import/'+year)

    # unzip contents to the year folder
    with zf('baseball/import/landing/'+zip_file) as unzip:
        unzip.extractall('baseball/import/'+year)

    # remove landing file
    if path.exists('baseball/import/landing/'+zip_file):
        remove('baseball/import/landing/'+zip_file)
