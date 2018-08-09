import os, sys, re
from pprint import pprint
#PyDrive
import pydrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
#
#  import the helper files
#
from ColabGDrive.helper import clean_directory_path, list_file_dict, build_full_path
#
#  Set logging level
#
#  TODO:  Including logging level information

class ColabGDrive:
  #
  def __init__(self, current_dir = 'root'):
    #
    print("Entering Initialization")
    self.myGDrive = None
    self.cur_dir = clean_directory_path(current_dir)
  #
  #  Connect the drive
  #
  def connect_gdrive(self):
    #return none if failure
    #
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    self.myGDrive = GoogleDrive(gauth)
    #  make sure cur_dir is good
    #
    if(self.myGDrive is not None):
        directory_dictionary = self.ls('')
        if(directory_dictionary is None):
            self.cur_dir = 'root'
        #  check if the directory exists
        c_cur_dir = clean_directory_path(self.cur_dir)
        #  check if the directory exists
        directory_dictionary = self.ls(c_cur_dir)
        if(directory_dictionary is not None):
            self.cur_dir = c_cur_dir
    else:
        return None
  #  Check drive/file/directory information
  def  is_connected(self):
    return True if(self.myGDrive is not None) else False
  
  #  Basic information
  def get_info(self):
    return self.myGDrive
  def cwd(self):
    return self.cur_dir
  def ls(self,file_name = '',print_val=False):
    '''
      TODO:  
    '''
    
    work_file_name = build_full_path(self, file_name.strip())
    if(len(work_file_name) == 0):
      if(print_val): print(None)
      return None
    else:
      print('**' + work_file_name + '**')
      ls_file_dict = list_file_dict(self.myGDrive, work_file_name)
      if(print_val):
        for lf in ls_file_dict: pprint(lf)
      return ls_file_dict
  
    
  #Current Directory Management, uses a quasi cd methodology
