'''
Module definition for colab_gdrive
'''
import os
import sys
import logging
from pprint import pformat, pprint
import inspect
#import traceback
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
class ColabGDrive(GoogleDrive):
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
  This could be more efficient if it kept the file_id information, but it doesn't right now.  The Use Case is generally assumed to be fairly
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
    None
    '''
    #  Set up logger
    self.colab_gdrive_logger = logging.getLogger(__name__)
    logger_ch = logging.StreamHandler(sys.stdout)
    self.colab_gdrive_logger.addHandler(logger_ch)
    #DEBUG, INFO, WARNING, ERROR, CRITICAL
    self.set_log_level(logging_level)
    #Logging
    self._basic_log_("Entering", call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    self.cur_dir = 'root'
    #
    try:
      auth.authenticate_user()
      gauth = GoogleAuth()
      gauth.credentials = GoogleCredentials.get_application_default()
    except Exception as e:
      raise ConnectionError("No GoogleDrive is connected")
    try:
      super().__init__(gauth)
      directory_dictionary = None
      directory_dictionary = self.ls('*')
      if directory_dictionary is None:
        raise FileNotFoundError("Root directory of the GoogleDrive was not found")
    except Exception as e:
      raise FileNotFoundError("Root directory of the GoogleDrive was not found")
    #
    #  Set up the local information
    #
    #self.my_gdrive = self._connect_gdrive_()
    self.initialized = True
    self._basic_log_("Exiting", call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    return None
  #
  #  Basic Logging Function
  #
  def _basic_log_(self, in_str='Please use Entering/Exiting', call_name='',logging_level=logging.INFO):
    if self.colab_gdrive_logger.isEnabledFor(logging_level):
      self.colab_gdrive_logger.info(in_str)
      self.colab_gdrive_logger.info(call_name)
  #
  #  Basic Overrides
  #
  def __str__(self):
    out_str = pformat(self.get_info()) + " : " + pformat(self.cur_dir) + " : " + pformat(self.initialized)
    return out_str
  def __repr__(self):
    out_str = pformat(self.get_info()) + " : " + pformat(self.cur_dir) + " : " + pformat(self.initialized)
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
    return True if(self.GetAbout()['kind'] == 'drive#about') else False

  #  Basic information
  def get_info(self):
    '''
    This just returns the drive information.

    Parameters:
    -----------
    None:

    WARNING:  I am not sure what this entails at this point, so it is just information.WARNING
    '''
    return self.GetAbout()
  #
  #
  #
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
  def get_file_metadata(self, in_str=None):
    '''
    Obtains the file meta data for a string.
    Parameters:
    ===========
    in_str:  The path name for the file of interest
    Results:
    ========
    None if there is an issue with the touching the file
    The entire metadata if the file is found
    '''
    #Logging
    self._basic_log_('Entering', call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    # 
    ret_val = None
    file_info = self._find_file_id_(in_str)
    if file_info:
      drive_file = self.CreateFile({'id': '{:s}'.format(file_info['id'])})
      ret_val = drive_file
    #Logging
    self._basic_log_('Exiting',call_name=pformat(inspect.currentframe().f_code.co_name),logging_level=logging.INFO)
    return ret_val
  #
  #
  #
  def isfile(self, in_str=None):
    '''
    Test if a string is a file name
    Parameters:
    ===========
    in_str:  The path name for the file of interest
    Results:
    ========
    True is a file
    False otherwise
    '''
    ret_val = False
    if in_str:
      f_info = self.get_file_metadata(in_str)
      if f_info and ( 'folder' not in f_info['mimeType']):
        ret_val = True
    return ret_val
  #
  #
  #
  def isdir(self, in_str=None):
    '''
    Test if a string is a file name
    Parameters:
    ===========
    in_str:  The path name for a directory of interest
    Results:
    ========
    True is a file
    False otherwise
    '''
    ret_val = False
    f_info = self.get_file_metadata(in_str)
    if f_info['mimeType']:
      if 'folder' in f_info['mimeType']:
        ret_val = True
    return ret_val
  #
  #
  #
  def getsize(self, in_str=None):
    '''
    Test if a string is a file name
    Parameters:
    ===========
    in_str:  The path name for the file of interest
    Results:
    ========
    file size if >= 0
    -1 otherwise
    False otherwise
    '''
    ret_val = -1
    if in_str:
      f_info = self.get_file_metadata(in_str)
      if int(f_info['fileSize']) >= 0:
        ret_val = int(f_info['fileSize'])
   
    return ret_val
  #
  # State Management
  def set_log_level(self, logging_level=logging.ERROR):
    '''
    Sets the log level
    Parameters:
    ===========
    logging_level:  The logging level to set
    Results:
    ========
    Silent return assumes this is set
    '''
    self.colab_gdrive_logger.setLevel(logging_level)
    return None
  #
  #Main Functions
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
    #Logging
    self._basic_log_("Entering", call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    #
    ret_val = None
    if work_name == '':
      ret_val = None
    else:
      ls_file_dict = self._list_file_dict_(work_name)
      ret_val = ls_file_dict
    #Logging
    self._basic_log_("Exiting", call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    return ret_val
  #
  #Directory Management, uses a quasi linux methodology
  #
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
    #Logging
    self._basic_log_('Entering',call_name=pformat(inspect.currentframe().f_code.co_name),logging_level=logging.INFO)
    #
    if name == '':
      name = 'root'
    if self.isdir(name):
      work_file_info = self.ls(name)
      if(len(work_file_info['file_result']) == 1 and 'folder' in work_file_info['file_result'][0]['mimeType']):
        self.cur_dir = work_file_info['full_name']
      elif work_file_info['full_name'] == 'root':
        self.cur_dir = work_file_info['full_name']
    #Logging
    self._basic_log_('Exiting', call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    return self.getcwd()
  #
  #  Helper functions
  #
  def _build_full_path_(self, in_str=''):
    '''
    This builds a theoretical absolute GoogleDrive path

    Parameters:
    ----------

    in_str:  The proposed directory string

    Result:
    ------
    An absolute path starting at 'root'
    '''
    #Logging
    self._basic_log_('Entering', call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    #
    ret_val = None
    if not in_str.strip():
      ret_val = self.getcwd()
    else:
      work_file_name = os.path.normpath(in_str.strip())
      if work_file_name[0] == '/':
        work_file_name = work_file_name[1:]
      work_file_struct = self._build_path_structure_(work_file_name)
      if work_file_struct['path_array'][0] != 'root':
        work_file_name = os.path.join(self.getcwd(),work_file_name)
      work_file_struct = self._build_path_structure_(work_file_name)
      if work_file_struct['path_array'][0] != 'root':
        raise FileNotFoundError('_build_full_path_ ' + 'path must begin with root ' + work_file_name)
      else:
        ret_val = os.path.normpath(work_file_name)
    #Logging
    self._basic_log_('Exiting', call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    return ret_val
  #
  #  Data movement functions
  #    These function move data to/from a Google drive to a local file system.  The process is a little different because
  #    the file has to be found and then transferred.
  #
  def _copy_from_(self, google_path=None, over_write=True):
    '''
    Copy from a GoogleDrive file to the current working directory.  This is an internal routine that handles one 
    file at a time.
    Parameters:
    ===========
    google_path:  The path of file to download
    over_write:  Logical variable to allow overwrite of file
    
    Results:
    ========
    True if the file was downloaded
    False otherwise
    '''
    if not google_path:
      raise FileNotFoundError('copy_from requires a file name to download')
    download_file_info = self._find_file_id_(google_path)
    if not download_file_info:
      raise FileNotFoundError('copy_from could not find the google file' + pformat(google_path))
    file_id = download_file_info['id']
    file_name = download_file_info['full_name']
    _, file_short_name = os.path.split(file_name)
    #  Now build the tranfer operations
    to_download = self.CreateFile({'id': '{:s}'.format(file_id)})
    ret_val = False
    if over_write:
      if os.path.isfile(file_short_name):
        os.remove(file_short_name)
      to_download.GetContentFile(file_short_name)
      if os.path.isfile(file_short_name):
        ret_val = True
    else:
      if not os.path.isfile(file_short_name):
        to_download.GetContentFile(file_short_name)
        if os.path.isfile(file_short_name):
          ret_val = True
    
    return ret_val
  def copy_from(self, google_paths=None, overwrite=True):
    '''
    Copies a list of files from a GoogleDrive to the current working directory.
    Parameters:
    ===========
    google_paths:  A list of files to copy.  Each is processed independently and not in parallel.google_paths
    overwrite:  True/False to overwrite current files.  The default is True
    Results:
    ========
    List of files that was successfully transferred.  An empty list if none were successfully transferred.
    '''
    if not google_paths:
      raise ValueError('An array of files must be provided, None was provided.')
    good_copies = []
    for gpath in google_paths:
      result = self._copy_from_(google_path=gpath, over_write=overwrite)
      if result:
        good_copies.append(gpath)
    return good_copies
      
  #
  #
  #
  def copy_to(self, local_file=None, google_dir='', over_write=True):
    '''
    Copy to a GoogleDrive file from the current working directory. 
    Parameters:
    ===========
    local_file:  The name of the local file in the current working directory
    google_dir:  The path of folder to upload to
    over_write:  Logical variable to allow overwrite of file
    
    Results:
    ========
    True if the file was uploaded
    False otherwise
    '''
    if not local_file:
      raise FileNotFoundError('copy_to requires a local file name to upload')
    if not os.path.isfile(local_file):
      raise FileNotFoundError('copy_to requires a local file to exist to upload')
    local_dir, short_file_name = os.path.split(local_file)
    if local_dir:
      raise FileNotFoundError('copy_to only supports copying file from the cwd.  Intermediate directory structures are not supported ' + pformat(len(local_dir)))
    if not self.isdir(google_dir):
      raise FileNotFoundError('copy_to requires a valid Google Drive Folder ' + pformat(google_dir))
    download_dir_info = self._find_file_id_(google_dir)
    if not download_dir_info:
      raise FileNotFoundError('copy_to could not find the google directory for ' + pformat(google_dir))
    dir_id = download_dir_info['id']
    dir_name = self._find_file_id_(google_dir)['full_name']
    full_name = os.path.join(dir_name,local_file)
    if over_write:
      if self.isfile(full_name):
        full_id = self.get_file_metadata(full_name)['id']
        to_delete = self.CreateFile({'id':'{:s}'.format(full_id)})
        to_delete.Trash()
        to_delete.Delete()
    #  Now build the tranfer operations
    to_upload = self.CreateFile({'parents':[{'id':"{:s}".format(dir_id)}],'title': local_file})
    to_upload.SetContentFile(local_file)
    to_upload.Upload()
    ret_val = False
    if self.isfile(full_name) and (os.path.getsize(local_file) == self.getsize(full_name)):
      ret_val = True
    return ret_val
  #
  #  Helper Functions
  #
  def _list_file_dict_(self, in_str=''):
    '''
    Returns a dictionary with the file name and file ID (if exists) - None otherwise

    Parameters:
    ----------

    in_str:  Is a path string, must be a GoogleDrive full path starting at root

    Exception
    =========
    Raises a connection error if a GoogleDrive is not connected, from here is probably means something timed out.

    Result:  A dictionary with the file path and file results from the FileList
      The results are called full_name and file_result

    '''
    #Logging
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Entering")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      self.colab_gdrive_logger.info(pformat(self.GetAbout()))
      self.colab_gdrive_logger.info(in_str)
    #
    if self.GetAbout() is None:
      raise ConnectionError("No GoogleDrive is connected, check for a timeout since it was connected at one time")
    file_path = self._build_path_structure_(in_str)
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info(pformat(file_path))
    in_struct = file_path['path_array']
    if in_struct[0] != 'root':
      raise FileNotFoundError('_list_file_dict_ expects a path array starting at root')
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info(pformat(in_struct))
    ret_val = self._traverse_structure_list_(in_struct)
    #Logging
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Exiting")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      self.colab_gdrive_logger.info(pformat(file_path))
    return ret_val
  #
  #  Traverse a file structure list
  #
  def _traverse_structure_list_(self, in_struct=None):
    '''
    Traverses a structure of directories to the last one and returns the information on the last element of the lsit

    Parameters:
    ===========
    in_struct:  The array with the list of directories that ends in a directory or file (as appropriate)

    Result:
    =======
    A dictionary with the full name and the information from the search

    '''
    #Logging
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Entering")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      self.colab_gdrive_logger.info(in_struct)

    if (not in_struct) or (in_struct[0] != 'root'):
      raise FileNotFoundError('_traverse_struct_list_ expects a path array starting at root' + pformat(in_struct))
    file_id = 'root'
    file_path = []
    file_path.append(file_id)
    for cur_name in in_struct[1:-1]:
      file_result = []
      file_list = self.ListFile({'q': "title contains '{:s}' and '{:s}' in parents and trashed=false".format(cur_name, file_id)}).GetList()
      if not file_list:
        break
      else:
        if len(file_list) > 1:
          raise FileExistsError('_list_file_dict_ only supports a single parent of the same name, GoogleDrive allows this but this does not')
        file_name = file_list[0]['title']
        file_id = file_list[0]['id']
        file_path.append(file_name)
    else:
      file_result = []
      c_name = in_struct[-1]
      if len(in_struct) > 1:
        file_list = self.ListFile({'q': "title contains '{:s}' and '{:s}' in parents and trashed=false".format(c_name, file_id)}).GetList()
        if file_list:
          for file_info in file_list:
            file_name = file_info['title']
            file_id = file_info['id']
            file_type = file_info['mimeType']
            t_dict = {"title" : file_name, "id":  file_id, 'mimeType':file_type}
            try:
              t_dict['fileSize'] = file_info['fileSize']
            except KeyError as e:
              pass
            file_result.append(t_dict)
          if len(file_list) == 1:
            file_path.append(file_name)
      else:
        drive_file = self.CreateFile({'id': '{:s}'.format(c_name)})
        t_dict = {'title': drive_file['title'], 'id': drive_file['id'], 'mimeType': drive_file['mimeType']}
        file_result.append(t_dict)
    if self.colab_gdrive_logger.isEnabledFor(logging.INFO):
      self.colab_gdrive_logger.info("Exiting")
      self.colab_gdrive_logger.info(pformat(inspect.currentframe().f_code.co_name))
      self.colab_gdrive_logger.info(pformat(file_path))
    return {'full_name': os.path.join(*file_path), 'file_result':file_result}
  #
  #  Get the full name and path array
  #
  def _build_path_structure_(self, in_str=''):
    '''
    This provides a consistent path build for ColabGDrive

    Parameters:
    ----------

    in_str:  This is assumed to be an absolute path

    Result: a dictionary with the full name and the path array
      These are called full_path and path_array

    WARNING:  The full name does not contain the following ending * if that is the last entry

    '''
    #Logging
    self._basic_log_('Entering', call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    work_str = os.path.normpath(in_str)
    in_struct = []
    while work_str != '':
      work_str, last = os.path.split(work_str)
      in_struct.append(last)
    in_struct.reverse()
    #house cleaning for edge cases
    if not in_struct:
      in_struct.append('*')
#     if len(in_struct) == 1 and in_struct[0] == 'root':
#       in_struct.append('*')
    t_struct = None
    if in_struct[-1] == '*':
      t_struct = in_struct[:-1]
    else:
      t_struct = in_struct
    if not t_struct:
      t_struct = self._build_path_structure_(self.getcwd())
    full_name = os.path.join(*t_struct)
    #Logging
    self._basic_log_('Exiting', call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    return {'full_name':full_name, 'path_array':in_struct}
  #
  #  Find the file id for a file on GoogleDrive
  #
  def _find_file_id_(self, in_str):
    '''
    This finds a file id for a file sent in by in_str
    Parameters
    ==========
    in_str:  The assumed path to a file or directory
    Results
    =======
    A file id for a path or None
    '''
    #Logging
    self._basic_log_('Entering', call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    w_str = self._build_full_path_(in_str)
    file_struct = self._build_path_structure_(w_str)
    r_val = self._traverse_structure_list_(file_struct['path_array'])
    p_val = r_val['file_result']
    ret_val = None
    if p_val:
      if len(p_val) > 1:
        raise FileNotFoundError('_find_file_id found too many files' + pformat(p_val))
      ret_val = {'full_name':r_val['full_name'], 'id': p_val[0]['id']}
    #Logging
    self._basic_log_('Exiting', call_name=pformat(inspect.currentframe().f_code.co_name), logging_level=logging.INFO)
    return ret_val
