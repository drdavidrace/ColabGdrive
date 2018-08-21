'''
Module definition for colab_gdrive
'''
import os
import sys
import logging
from pprint import pprint, pformat
import inspect
import traceback
#PyDrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#google
from google.colab import auth
#oauth2client
from oauth2client.client import GoogleCredentials
#
#  Set logging level
#
class ColabGDrive:
  '''
  The class manages the connection to a user's Google Drive.
  #
  Use Case:
  ---------
  The user is running a Colaboratory notebook from their Google Drive (GDrive).  The notebook cannot access the GDrive files information
  since the Colaboratory notebook is running in a VM.  It can only access the local VM files; therefore, the user needs to
  copy-from/copy-to between the local file system and the GDrive.  There is a great tool for setting up the connection to do the copies, but
  it requires many lines of code to make this happen.  The many lines of code detracts from the Colaboratory notebook flow; therefore, it
  is best to have a library for the management.  This is such a library.
  #
  It is modeled after python set of commands (which are used to manage the local VM drives); therefore, it should be easy to use.It
  #
  Special Note:
  -------------
  It is possible to mount the GDrive into the local workspace, but that doesn't seem very "Google Ecosystem".  Since we may be using other
  Google Storage with other applications, this library is trying to be more "Google Ecosystem" like.Google
  #
  WARNING:
  -------
  This could be more efficient if it kept the fileID information, but it doesn't right now.  The Use Case is generally assumed to be fairly
  low performance requirements
  #
  Main Methods:
  -------------
  #
  getcwd  - returns the GDrive current working directory
  chdir  - changes the GDrive current working directory
  ls  - gets the basic listing information for a file/directory
  copy_from - copies from the GDrive to the cwd of the local file system
  copy_to - copies from the path give to the GDrive given
  mkdir - makes a file folder on the GDrive, it does this recursively if necessary
  '''
  #
  def __init__(self, logging_level=logging.ERROR):
    '''
    The initialization routine sets up the internal information and sets up the GoogleDrive connection.The

    Parameters
    ----------
    loggine_level : This sets the logging level for this object.  Default is ERROR

    Returns
    -------
    False if no success
    True if successful

    TODO:
    (1)  Determine if I want to pass in an option for the cwd.  Unclear since a single cwd call can set this directory
    (2)  Do a better logging error message
    (3)  Convert to using os.path.join and other os.path functions for path work
    '''
    #
    try:
      self.colab_gdrive_logger = logging.getLogger(__name__)
      logger_ch = logging.StreamHandler(sys.stdout)
      self.colab_gdrive_logger.addHandler(logger_ch)
      #DEBUG, INFO, WARNING, ERROR, CRITICAL
      self.colab_gdrive_logger.setLevel(logging_level)
      #Logging
      if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
        self.colab_gdrive_logger.info("Entering")
        self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      self.cur_dir = 'root'
      self.my_gdrive = self._connect_gdrive_()
      self.initialized = True
      #Logging
      if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
        self.colab_gdrive_logger.info("Leaving __init__")
        self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      return None
    except Exception:
      self.my_gdrive = None
      self.cur_dir = None
      self.initialized = False
      return None
  #
  #  Connect the drive
  #
  def _connect_gdrive_(self):
    #
    #return none if failure
    #
    #Logging
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Entering")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    t_gdrive = GoogleDrive(gauth)
    #if self.colab_gdrive_logger.isEnabledFor(logger.INFO):
    ret_val = None
    if t_gdrive is not None:
      if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
        self.colab_gdrive_logger.info("Good GoogleDrive")
        self.colab_gdrive_logger.info(pformat(t_gdrive))
      self.my_gdrive = t_gdrive
      directory_dictionary = None
      try:
        directory_dictionary = self.ls('*')
      except Exception:
        traceback.print_exc()
      if directory_dictionary is None:
        self.cur_dir = None
        self.initialized = False
        ret_val = None
      else:
        self.cur_dir = 'root'
        ret_val = t_gdrive
    else:
      ret_val = None
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Leaving")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
    return ret_val
  #
  #  Basic Overrides
  #
  def __str__(self):
    out_str = pformat(self.my_gdrive) + " : " + pformat(self.cur_dir) + " : " + pformat(self.initialized)
    return out_str
  def __repr__(self):
    out_str = pformat(self.my_gdrive) + " : " + pformat(self.cur_dir) + " : " + pformat(self.initialized)
    return out_str
  #  Check drive/file/directory information
  def  is_connected(self):
    '''
    This returns True if it is connected and False otherwise.
    #
    Parameters:
    -----------
    None
    #
    Returns:
    --------
    True if connected and False otherwise

    TODO:
    -----
    (1)  Just checks the local variable.  Probably should check the drive just incase it was timed out.
    '''
    return True if(self.my_gdrive is not None) else False

  #  Basic information
  def get_info(self):
    '''
    This just returns the drive information.

    Parameters:
    -----------
    None:

    WARNING:  I am not sure what this entails at this point, so it is just information.WARNING
    '''
    return self.my_gdrive

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
  #
  #
  #
  def ls(self, name=''):
    '''
    ls provides a GoogleDrive listing of the information for a name.  Informational logging is provided to stdout if the logging level is set to INFO
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

    Returns
    -------
    None:  If there is a problem with the name
    Otherwise:  A dictionary containing the full_name and a list of the full_name contents
      Contents of file_result are:
        id
        mimeType
        title

    Raises
    ------
    None at this point

    TODO
    (1)  Raise basic errors

    '''
    work_name = self._build_full_path_(name.strip())
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Entering")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      self.colab_gdrive_logger.info(pformat(name))
      self.colab_gdrive_logger.info(pformat(work_name))
    
    ret_val = None
    if work_name == '':
      ret_val = None
    else:
      ls_file_dict = self._list_file_dict_(work_name)
      ret_val = ls_file_dict
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Leaving")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      self.colab_gdrive_logger.info(pformat(ls_file_dict))
      self.colab_gdrive_logger.info(pformat(ret_val))
    return ret_val

  #Directory Management, uses a quasi cd methodology
  def chdir(self, name=''):
    '''
    This sets the current working directory (if valid directory) and returns the current working directory at the end of the method.
    If name is passed in as '', then it resets to 'root'

    Parameters:
    -----------
    name:  The proposed name of the directory.  If begins with /, then an absolute path.  Otherwise a relative path.

    Returns:
    --------
    The current working directory
    '''
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Entering")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
    if name == '':
      name = 'root'
    work_file_info = self.ls(name)
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info(pformat(work_file_info['full_name']))
    if(len(work_file_info['file_result']) == 1 and 'folder' in work_file_info['file_result'][0]['mimeType']):
      self.cur_dir = work_file_info['full_name']
    elif work_file_info['full_name'] == 'root':
      self.cur_dir = work_file_info['full_name']
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Leaving")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
    return self.getcwd()
  #
  #  Helper functions
  #
  def _build_full_path_(self, in_str=''):
    '''
    This decides on an absolute path or relative path

    Parameters:
    ----------

    in_str:  The proposed directory string

    Result:
    ------
    An absolute path starting at 'root'
    '''
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Entering")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
    ret_val = None
    if self.my_gdrive is None:
      ret_val = None
    work_file_name = in_str.strip()
    if work_file_name == '':
      ret_val = self.getcwd() + '/*'
    else:
      if work_file_name[0] != '/':
        ret_val = os.path.join(self.getcwd(), os.path.normpath(work_file_name))
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Leaving")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
    return ret_val
#
  def _list_file_dict_(self, in_str=''):
    '''
    Returns a dictionary with the file name and file ID (if exists) - None otherwise

    Parameters:
    ----------

    in_str:  This is assumed to be an absolute path

    Result:  A dictionary with the file path and file results from the FileList
      The results are called full_name and file_result

    '''
    try:
      if self.my_gdrive is None:
        return None
      #Logging
      if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
        self.colab_gdrive_logger("Entering")
        self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
        self.colab_gdrive_logger.info(in_str)
      file_path = _build_path_structure_(in_str)
      in_struct = file_path['path_array']
      file_id = 'root'
      file_result = []
      for i in range(1, len(in_struct)):
        file_result = []
        file_list = self.colab_gdrive_logger.ListFile({'q': "title contains '{:s}' and '{:s}' in parents and trashed=false".format(in_struct[i], file_id)}).GetList()
        if not file_list:
          file_id = None
          break
        else:
          if i < len(in_struct) - 1:
            file_id = file_list[0]['id']
          else:
            for j in range(len(file_list)):
              file_name = file_list[j]['title']
              file_id = file_list[j]['id']
              file_type = file_list[j]['mimeType']
              file_result.append({"title" : file_name, "id":  file_id, 'mimeType':file_type})
      #Logging
      if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
        self.colab_gdrive_logger("Leaving")
        self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      file_path = _build_path_structure_(in_str)
      return {'full_name': file_path['full_name'], 'file_result':file_result}
    except Exception:
      return None
#
#
#
def _build_path_structure_(in_str=''):
  '''
  This provides a consistent path build for ColabGDrive

  Parameters:
  ----------

  in_str:  This is assumed to be an absolute path

  Result: a dictionary with the full name and the path array
    These are called full_path and path_array

  TODO:
  _____
  (1)  Change to use of os.path splitting functions.  This will require an iterative process, but not bad

  '''
#   work_str = clean_directory_path(in_str)
  work_str = os.path.normpath(in_str)
  in_struct = []
  while work_str != '':
    work_str, last = os.path.split(work_str)
    in_struct.append(last)
  in_struct.reverse()

  #house cleaning for edge cases
  if not in_struct:
    in_struct.append('*')
  if len(in_struct) == 1 and in_struct[0] == 'root':
    in_struct.append('*')
  if not (in_struct[0] == 'root'):
    in_struct = ['root'] + in_struct
  t_struct = None
  if in_struct[-1] == '*':
    t_struct = in_struct[:-1]
  else:
    t_struct = in_struct
  full_name = os.path.join(t_struct[0], t_struct[1:])
  return {'full_name':full_name, 'path_array':in_struct}
