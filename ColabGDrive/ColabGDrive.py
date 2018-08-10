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
  '''
  The class manages the connection to a user's Google Drive.
  
  Use Case:
  ---------
  The user is running a Colaboratory notebook from their Google Drive (GDrive).  The notebook cannot access the GDrive files information
  since the Colaboratory notebook is running in a VM.  It can only access the local VM files; therefore, the user needs to
  copy-from/copy-to between the local file system and the GDrive.  There is a great tool for setting up the connection to do the copies, but
  it requires many lines of code to make this happen.  The many lines of code detracts from the Colaboratory notebook flow; therefore, it
  is best to have a library for the management.  This is such a library.  
  
  It is modeled after python set of commands (which are used to manage the local VM drives); therefore, it should be easy to use.It
  
  Special Note:
  -------------
  It is possible to mount the GDrive into the local workspace, but that doesn't seem very "Google Ecosystem".  Since we may be using other 
  Google Storage with other applications, this library is trying to be more "Google Ecosystem" like.Google
  
  WARNING:
  -------
  This could be more efficient if it kept the fileID information, but it doesn't right now.  The Use Case is generally assumed to be fairly 
  low performance requirements
  
  Main Methods:
  -------------
  
  getcwd  - returns the GDrive current working directory
  chdir  - changes the GDrive current working directory
  ls  - gets the basic listing information for a file/directory
  '''
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
    (1)  Determine if I want to pass in an option for the cwd.  Unclear since a single cwd call can set this directory
    '''
    #
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
    t_gdrive = GoogleDrive(gauth)
    #  make sure cur_dir is good
    #
    if(t_gdrive is not None):
      self.myGDrive = t_gdrive
      directory_dictionary = self.ls('*',print_val=True)
      print(directory_dictionary)
      if(directory_dictionary is None):
          self.cur_dir = 'root'
          return None
      return t_gdrive
    else:
      return None
  #  Check drive/file/directory information
  def  is_connected(self):
    '''
    This returns True if it is connected and False otherwise.
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    True if connected and False otherwise
    
    TODO:
    -----
    (1)  Just checks the local variable.  Probably should check the drive just incase it was timed out.
    '''
    return True if(self.myGDrive is not None) else False
  
  #  Basic information
  def get_info(self):
    '''
    This just returns the drive information.
    
    Parameters:
    -----------
    None:
    
    WARNING:  I am not sure what this entails at this point, so it is just information.WARNING
    '''
    return self.myGDrive
  
  def getcwd(self):
    '''
    Just returns the current working directory
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    The current working directory
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
    Otherwise:  A dictionary containing the full_name and a list of the full_name contents
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
      if(print_val): 
        pprint("******Start******{:s}***********".format(work_name))
        pprint(None)
        pprint("******End******{:s}***********".format(work_name))
      return None
    else:
      ls_file_dict = list_file_dict(self.myGDrive, work_name)
      if(print_val):
        pprint("******Start******{:s}***********".format(ls_file_dict['full_name']))
        for lf in ls_file_dict['file_result']: pprint(lf)
        pprint("******End******{:s}***********".format(ls_file_dict['full_name']))
        
      return ls_file_dict
  
    
  #Directory Management, uses a quasi cd methodology
  def chdir(self, name=''):
    '''
    This sets the current working directory (if valid directory) and returns the current working directory at the end of the method.
    
    Parameters:
    -----------
    name:  The proposed name of the directory.  If begins with /, then an absolute path.  Otherwise a relative path.
    
    Returns:
    --------
    The current working directory
    '''
    work_file_info = self.ls(name)
    if(len(work_file_info['file_result']) == 1 and 'folder' in work_file_info['file_result'][0]['mimeType']):
      self.cur_dir = work_file_info['full_name']
    elif(work_file_info['full_name'] == 'root'):
      self.cur_dir = work_file_info['full_name']
        
    return(self.getcwd())