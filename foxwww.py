# -*- coding: utf-8 -*-

'''Converts VFP9 data for the web and display them in grid (or grids with links for foreign keys).
Uses VFP9 code in 1st phase to convert data structures
    (and for case of cz-Kamenicky and pl-Mazovia to get the python/dbfread supported codepage).
With regard to source (vfp) data this is developed and tested on the Windows platform.

Change fox\src\myconversion\myconversion.exe and use your own licensed vfp9 to build the fox\bin\foxwww.exe.
If you have to use different vfp version, replace fox\bin with your vfp runtimes too.
In most worse case create converted dbf's (with field id int unique) in data/fox anyway
    and comment the ..'fox\bin\foxwww.exe'.. command in this (foxwww.py) file bellow.

You can make import-post-actions in python: find import-post-actions in this file bellow.   

Requirements and customizing:
1. install python 2.7.9+ Windows 32bit binary, from www.python.org to c:\Python27 (not recommended 64bit; not written/tested for 3.x)
2. check if c:\Python27 and c:\Python27\Scripts were added to the path or add them manually (somewhere in Control Panels, System, Details(?)) 
3. command line: pip install dbfread
4. copy web2py sources from www.web2py.com as c:\Python27\lib\site-packages\web2py
5. check that (cd c:\Python27\lib\site-packages\web2py ; python web2py.py -a "somepassword" ; http://localhost:8000) starts the web2py server; then Ctrl-C to stop them
6. copy applications\viewer from this project as c:\Python27\lib\site-packages\web2py\applications\viewer
7. change applications\viewer\modules\db_model, function get_model(): define same tables and fields (but in lowercase and except of field id) as in vfp tables generated in next step(s) 
8. in vfp9 do (cd fox\src ; modify project foxwww) and make your own myconversion\myconversion.prg where you should:
    - create 1250 target dbf(s) with field (id int unique)
    - copy data to this/these target dbf(s) (this can be near 1:1 or more complex conversion)
9. from vfp9 project build: fox\bin\foxwww.exe
10. command line (cd <root_of_this_project>): python foxwww.py <src_data_path>
11. check if generated data\fox\.. tables are Ok --if no, repair the vfp9 code
12. check that (cd c:\Python27\lib\site-packages\web2py ; python web2py.py -a "somepassword" ; http://localhost:8000/viewer) works well; then Ctrl-C to stop server
13. build the web2py hosting: www.web2py.com/book, chapter Deployment recipes; get their ftp credentials
14. update the foxwww.bat batch: cd <root_of_this_project> ; python foxwww.py <src_data_path> <deploy_command>

Usage: call foxwww.bat
'''

import argparse
from glob import glob
import os
import sys

from dbfread import DBF

web2py_path = r'C:\Python27\Lib\site-packages\web2py'
if not web2py_path in sys.path:
    sys.path.append(web2py_path)
from gluon import DAL, Field   # requires: web2py (from web2py.com, download, sources) in <web2py_path> dir 
from applications.viewer.modules.db_model import get_model


DATA_FOX = r'data\fox'
DATA_SQLITE = r'data\sqlite'


class BadDirError(ValueError):
    pass

def run_as_script():
    '''this runs the whole conversion and includes command line parsing
    if used as imported module then call run() directly
    '''

    try:
        srcdata, deploy_command = parsed_args()
    except BadDirError as err:
        print err.message
        return
    run(srcdata, deploy_command)
                                                                                            
def run(srcdata, deploy_command=None):
    '''this is the main method - the whole conversion
     
    1. Create a cp1250 converted copy of dbf data
    2. Import into SQLite Web2py database
    3. Transfer the SQLite database to the hosting with FTP (if deploy_command)
    '''

    sure_empty_dir(DATA_FOX)
    sure_empty_dir(DATA_SQLITE)
    
    print "Creating a cp1250 converted copy of dbf data [using vfp] ..."
    os.system(r'fox\bin\foxwww.exe %s' % srcdata)
     
    print "Importing into SQLite Web2py database ..."
    dbf2sqlite()

    if deploy_command:
        print "Uploading to the server ..."
        os.system(' '.join(deploy_command))

def parsed_args():
    '''parses command line arguments of this script
    '''
    parser = argparse.ArgumentParser(
                description='Will prepare fox data for the web browsing.')
    parser.add_argument(
                'src_data_path', type=str, help='directory with *.dbf files')
    parser.add_argument(
                'deploy_command', type=str, nargs='*',
                help='command to upload to the server (if FTP, ftp/ncftpput.exe... is recommended, for params see: ftp/ncftpput -h)')
    args = parser.parse_args()
    if not os.path.isdir(args.src_data_path):
        raise BadDirError('bad parameter src_data_path, see: foxwww.py --help' % paramname)
    return args.src_data_path, args.deploy_command 

def dbf2sqlite():
    db = DAL('sqlite://upload.sqlite',
            pool_size=1, check_reserved=['sqlite'], folder=DATA_SQLITE)
    db = get_model(db)
    for table in db.tables: 
        print '  table', table,
        for row_upper_names in DBF(os.path.join(DATA_FOX, '%s.dbf' % table)):
            something = False
            row_lower_names = {}     # table definitions in applications/viewer/modules/db_model.py and in fox/src/myconversion/myconversion.prg must be the same
            for k, v in row_upper_names.iteritems():
                k = k.lower()
                if v is not None: # k != 'id':
                    something = True
                    row_lower_names[k.lower()] = v   # but fox thurn fields to uppercase and we preffer lowercase
            if something:
                db[table].insert(**row_lower_names)
        db.commit() 
        print ' - done'

    try:                                       # are some import-post-actions defined?
        from myconversion import myconversion  # ./myconversion.py : def myconversion(db): 
        print '  additional data conversion',
        myconversion(db)                       # see www.web2py.com/book, chapter 6 - DAL
        db.commit()                            # auto commit if you miss commit in myconversion()  
        print ' - done'
    except ImportError:
        pass
    db.close()

def sure_empty_dir(path):
    if os.path.isdir(path):
        if path[:5]=='data\\':  # to be sure to delete previous results only
            for filename in filter(lambda candidate: os.path.isfile(candidate), glob(os.path.join(path, '*'))):
                os.remove(filename)
    else:
        os.makedirs(path)

if __name__=='__main__':
    run_as_script()
