# this python script is to import the retrosheet files
from os import path, mkdir, remove
import urllib.request
from zipfile import ZipFile as zf
import global_variables as gv
import sys

# if len(sys.argv) > 1:
def import_data(year):

    # create import folder if not available
    if path.exists(gv.data_dir):
        pass
    else:
        mkdir(gv.data_dir)

    # create landing folder if not available
    if path.exists(gv.data_dir + '/landing'):
        pass
    else:
        mkdir(gv.data_dir + '/landing')

    # download file into import/landing folder
    url = 'https://www.retrosheet.org/events/'
    # year = sys.argv[1]
    zip_file = year + 'eve.zip'
    urllib.request.urlretrieve(url+zip_file, gv.data_dir + '/landing/'+zip_file)

    # create new folder for the unzipped contents
    if path.exists(gv.data_dir + '/' + year):
        pass
    else:
        mkdir(gv.data_dir + '/' + year)

    # unzip contents to the year folder
    with zf(gv.data_dir + '/landing/'+zip_file) as unzip:
        unzip.extractall(gv.data_dir + '/' + year)

    # remove landing file
    if path.exists(gv.data_dir + '/landing/' + zip_file):
        remove(gv.data_dir + '/landing/' + zip_file)
