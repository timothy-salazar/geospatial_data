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
    def __init__(self, save_loc='../assets/2018_PL',
                ftp_dir='geo/tiger/TIGER2018PLtest'):
        """Inputs:
            save_loc: string - the path to the location where the user wants the
                geospatial data to be saved.
            ftp_dir: string - the path to the directory within the USGS FTP
                server which the user would like to save data from

        Other:
            self.dir_out: list - this is used to capture the output of the
                ftp.retrlines() function, which is invoked in the
                directory_crawl() method.

            self.level: int - this is used to keep track of which directory
                level within the USGS FTP server our program is in. It gets
                printed out, but it isn't used by any of the methods. It's
                there for debugging purposes.

            self.dir_path_list: list - when our crawler finds a sub-directory,
                the dir_handler() method appends the path to the directory to
                this list.

            self.file_path_list: list - when our crawler finds a file, the
                file_handler() method appends the path to the file to this list.
        """
        self.save_loc = sav_loc
        self.ftp_dir = ftp_dir
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

        This method checks file/directory indicated by i. If i[1] is the name
        of a directory, it passes i and the ftp instance to the dir_handler()
        method. If it is a file, it passes it to the file_handler() method
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
                file. Because this method receives i from the method
                dir_or_file(), the value of i[0] should always be 2, indicating
                a directory.
            ftp: an instance of the FTP() class

        This method will append the name of the directory contained in i[1] to
        self.dir_path_list, which is a list in which each item is a directory.
        These are in order, such that dir_path_list[0] is the first directory
        and so on. Each item in the list is a sub directory of the item
        preceeding it in the list.
        This method calls the directory_crawl() method which in turn calls
        this method again, making the behavior of the censusFTP() crawler
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
        """Input:
            i: a list in which i[1] is the name of an item in the current
                directory, and i[0] tells us wheether it is a directory or a
                file. Because this method receives i from the method
                dir_or_file(), the value of i[0] should always be 1, indicating
                a file that we will want to download.
            ftp: an instance of the FTP() class

        This method will take the name of a file in the current FTP directory
        from i, append it to the current ftp file path, and then pass the
        resulting address to the ftp.retrbinary() function.

        It copies the directory structure that it finds on the FTP server to the
        local self.save_loc location, and gives the file the same name given in
        the FTP server. It checks to see if the save location exists, and if
        it doesn't it will create the directory.
        """
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
        """Input:
            sd: the name of a sub directory which is accessible from the
                directory which the ftp object is currently pointed to, so that
                a simple ftp.cwd(sd) will change to the new directory.
            ftp: an instance of the FTP() class

        Given a sub directory sd, this method will change to the sub directory,
        use the ftp.retrlines() function to retrieve a list of entities in the
        new sub directory, and then parse the output of this function -
        splitting each line into a name and type (file or directory). The
        resulting list [name, type] is then appended to self.file_types.

        Once self.file_types has been populated, this method goes through the
        list and passes each [name, type] sub-list to the dir_or_file() method.
        """
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
            print("Could not retrieve contents")
        file_types = [[re.split(' +',i)[j] for j in [1, -1]] for i in self.dir_out]
        self.dir_out = []
        for i in file_types:
            ftp = self.dir_or_file(i, ftp)
            # Pause before more querying, just to be courteous.
            time.sleep(1.5)
        return ftp

    def get_census_data(self, ftp):
        """Input:
            ftp: an instance of the FTP() class

        This method gets a list of sub-directories within the initial directory
        and passes them to the directory_crawl() method.
        """
        print('Connection established.')
        self.sub_dirs = ftp.nlst()
        for sd in self.sub_dirs:
            ftp = self.directory_crawl(sd, ftp)
            try:
                ftp.cwd(self.ftp_dir)
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
