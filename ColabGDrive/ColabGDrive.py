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
  def __init__(self):
    '''
    The initialization routine sets up the internal information and sets up the GoogleDrive connection.The
    
    Parameters
    ----------
    None:  It sets the current working directory to root
    
    Returns
    -------
    False if no success
    True if successful
    
    TODO:  
    (1)  Determine if I want to pass in an option for the cwd.  Unclear since a single call can set this directory
    '''
    #
    #print("Entering Initialization")
    try:
      self.cur_dir = 'root'
      self.myGDrive = self.__connect_gdrive_()
      self.initialized = True
      return None
    except:
      self.myGDrive = None
      self.cur_dir = None
      self.initialized = False
      return None
  #
  #  Connect the drive
  #
  def __connect_gdrive_(self):
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
    '''
    This just returns the drive information.This
    
    WARNING:  I am not sure what this entails at this point, so it is just information.WARNING
    '''
    return self.myGDrive
  
  def cwd(self):
    '''
    
    '''
    return self.cur_dir
  def ls(self,name = '',print_val=False):
    '''
    ls provides a GoogleDrive listing of the information for a name, with an optional parameter for printing the value of the resulting
    name.  The resulting name goes through a series of steps from the input name:
      (1)  Full path implementation - If the name begins with /, then it is assumed to be a full path.  Otherwise, a relative path.
      (2)  / simplification, means reducing multiple slashes to a single slash akin to Linux operations
      (3)  Path simplification - If the component name is ., then it removes this from the path.  If the component name is .., then it moves back a component
      
    Other simplifications may be applied in the future
    Parameters
    ----------
    name : String for name to list
      If the last component is a ., then the last folder contents are listed
      If the last component is a *, then the last folder contents are listed
    print_val:  A boolean to indicate whether to print the contents information within this methodology
    
    Returns
    -------
    None:  If there is a problem with the name
    Otherwise:
      List with the contents:
        id
        mimeType
        title
        
    Raises
    ------
    None at this point
    
    TODO
    (1)  Raise basic errors
    (2)  Replace the print_val with logging level
    
    '''
    
    work_name = build_full_path(self, name.strip())
    if(len(work_name) == 0):
      if(print_val): pprint(None)
      return None
    else:
      ls_file_dict = list_file_dict(self.myGDrive, work_name)
      if(print_val):
        for lf in ls_file_dict: pprint(lf)
      return ls_file_dict
  
    
  #Directory Management, uses a quasi cd methodology
