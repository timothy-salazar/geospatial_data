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
        """this function is fed to ftp.retrlines() when our directory_crawl()
        function wants to know what the ftp server is telling us is in a
        specific directory. Appends the results to self.dir_out.
        """
        self.dir_out.append(x)

    def back_one(self, ftp):
        """Moves our crawler back up one level in the server by removing the
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
            i: a list in which i[1] is an address, and i[0] tells us what the
                address is. If i[0] is 2, the address points to another
                directory. if i[0] is 1, the address points to a file, and
                we'll want to download it.
            ftp: an instance of the FTP() class

        This function checks the address in i. If it is a directory, it passes i
        and the ftp instance to the dir_handler() function. If it is a file,
        it passes it to the file_handler() function so that its contents can
        be downloaded. 
        """
        if i[0] == '2':
            return self.dir_handler(i, ftp)
        elif i[0] == '1':
            return self.file_handler(i, ftp)

    def dir_handler(self, i, ftp):
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
