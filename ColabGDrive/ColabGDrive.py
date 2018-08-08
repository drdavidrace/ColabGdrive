import os, sys, re
import pydrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
#
#  import the helper files
#
from ColabGDrive.helper import clean_directory_path, list_file_dict

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
  def connect_drive(self, cur_dir = None):
    #return none if failure
    #
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    self.myGDrive = GoogleDrive(gauth)
    #  make sure cur_dir is good
    #
    if(self.myGDrive is not None):
        directory_dictionary = list_file_dict(self.myGDrive, self.cur_dir)
        if(directory_dictionary is None):
            self.cur_dir = 'root'
        if(cur_dir is not None):
          #  check if the directory exists
          c_cur_dir = clean_directory_path(cur_dir)
          #  check if the directory exists
          directory_dictionary = list_file_dict(c_cur_dir)
          if(directory_dictionary is not None):
              self.cur_dir = c_cur_dir
    else:
        return None
  #  Check drive/file/directory information
  def  is_connected(self):
    return True if(self.myGDrive is not None) else False
  
  #  Basic information
  def get_drive_info(self):
    return self.myGDrive
  def get_current_directory(self):
    return self.cur_dir
  def get_file_information(self,file_name = ''):
    if(len(file_name) == 0):
      return None
    return list_file_dict(self,file_name)
    
    
  #change directory