import urllib
from contextlib import closing
import re
import os
import shutil
import time
from ftplib import FTP


class censusFtp():
    """This class is my first time working with python's ftplib - or ftp
    connections programatically at all. It's rough, and it's not pretty, but it
    does what it's supposed to do, and I learned my FTP basics by writing it.
    """
    def __init__(self):
        """self.sav_loc is the location where the geospatial data is to be
        stored once I've downloaded it.
        self.level is there to keep track of which directory level we're in on
        the USGS server.
        """
        self.save_loc = '/Users/tc/Documents/projects/geospatial_data/assets/2018_PL'
        self.dir_out = []
        self.level = 0
        self.dir_path_list = []
        self.file_path_list = []

    def ftp_callback(self, x):
        """If we give the function ftp.retrlines() the command 'LIST', it will
        retrieve a list of files and the information about those files
        (https://docs.python.org/3/library/ftplib.html). The default behavior is
        to print this list to sys.stdout. This callback replaces that behavior,
        instead appending the list of files/file information to self.dir_out.
        """
        self.dir_out.append(x)

    def back_one(self, ftp):
        """Moves the crawler back up one level in the server by removing the
        last directory from the ftp address we're querying.
        """
        print('Moving back up one level')
        self.level -= 1
        cur_dir = ftp.pwd()
        new_path = os.path.split(cur_dir)[0]
        print('Moving from directory: {}'.format(cur_dir))
        print('To directory: {}'.format(new_path))
        ftp.cwd(os.path.split(ftp.pwd())[0])
        print('Done.')
        return ftp

    def dir_or_file(self, i, ftp):
        """Input:
            i: a list in which i[1] is the name of either a directory or a file
                contained in the current directory, and i[0] indicates which it
                is. If i[0] is 2, i[1] is the name of a directory. if i[0] is 1,
                then i[1] is the name of a file, and we'll want to download it.
            ftp: an instance of the FTP() class

        This function checks file/directory indicated by i. If i[1] is the name
        of a directory, it passes i and the ftp instance to the dir_handler()
        function. If it is a file, it passes it to the file_handler() function
        so that its contents can be downloaded.
        """
        if i[0] == '2':
            return self.dir_handler(i, ftp)
        elif i[0] == '1':
            return self.file_handler(i, ftp)

    def dir_handler(self, i, ftp):
        """Input:
            i: a list in which i[1] is the name of an item in the current
                directory, and i[0] tells us wheether it is a directory or a
                file. Because this function receives i from the function
                dir_or_file(), the value of i[0] should always be 2, indicating
                a directory.
            ftp: an instance of the FTP() class

        This function will append the name of the directory contained in i[1] to
        self.dir_path_list, which is a list in which each item is a directory.
        These are in order, such that dir_path_list[0] is the first directory
        and so on. Each item in the list is a sub directory of the item
        preceeding it in the list.
        This function calls the directory_crawl() function which in turn calls
        this function again, making the behavior of the censusFTP() crawler
        recursive. It go through the directories and sub directories of the in a
        depth-first search, downloading all of the files contained in the FTP
        server directory we point it at (in this case TIGER2018PLtest).

        """
        print('Found sub directory: {}'.format(i[1]))
        self.dir_path_list.append(os.path.join(ftp.pwd(),i[1]))
        time.sleep(1.5)
        ftp = self.directory_crawl(i[1], ftp)
        ftp = self.back_one(ftp)
        return ftp

    def file_handler(self, i, ftp):
        print('Found file: {}'.format(i[1]))
        self.file_path_list.append(os.path.join(ftp.pwd(),i[1]))
        cmd = 'RETR {}'.format(i[1])
        dir_path = ftp.pwd().split('/')[4:]
        save_file = os.path.join(self.save_loc, *dir_path, i[1])
        split_dir = os.path.split(save_file)[0]
        if not os.path.isdir(split_dir):
            print('Making sub directory: {}'.format(split_dir))
            os.makedirs(split_dir)
        else:
            print('Sub directory exists.')
        if not os.path.exists(save_file):
            print('Saving file: {}'.format(save_file))
            ftp.retrbinary(cmd, open(save_file, 'wb').write)
            return ftp
        else:
            print('File {} already exists.'.format(save_file))
            return ftp



    def directory_crawl(self, sd, ftp):
        print('Current directory: {}'.format(ftp.pwd()))
        print('Entering sub directory {}'.format(sd))
        print('Level {}: '.format(self.level))
        try:
            ftp.cwd(sd)
            self.level += 1
        except:
            print("Could not change to directory: {}".format(sd))
        try:
            ftp.retrlines('LIST', self.ftp_callback)
        except:
            print("Could not retrieve page")
        file_types = [[re.split(' +',i)[j] for j in [1, -1]] for i in self.dir_out]
        self.dir_out = []
        for i in file_types:
            ftp = self.dir_or_file(i, ftp)
            # Pause before more querying, just to be courteous.
            time.sleep(1.5)
        return ftp

    def get_census_data(self, ftp):
        print('Connection established.')
        self.sub_dirs = ftp.nlst()
        for sd in self.sub_dirs[5:]:
            ftp = self.directory_crawl(sd, ftp)
            try:
                ftp.cwd('/geo/tiger/TIGER2018PLtest')
                # Pause before more querying, just to be courteous.
                time.sleep(3)
            except:
                print("Coult not connect to FTP server.")
                ftp.quit()

def main():
    ftp = FTP('ftp2.census.gov')
    ftp.login()
    ftp.cwd('geo/tiger/TIGER2018PLtest')
    cftp = censusFtp()
    cftp.get_census_data(ftp)


if __name__ == '__main__':
    main()
