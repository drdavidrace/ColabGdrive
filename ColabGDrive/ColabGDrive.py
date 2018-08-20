import os, sys, re
import logging
from pprint import pprint, pformat
#PyDrive
import pydrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
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
  copy_from - copies from the GDrive to the cwd of the local file system
  copy_to - copies from the path give to the GDrive given
  mkdir - makes a file folder on the GDrive, it does this recursively if necessary
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
    (2)  Do a better logging error message
    (3)  Convert to using os.path.join and other os.path functions for path work
    '''

    #
    try:
      self.Logger = logging.getLogger(__name__)
      ch = logging.StreamHandler(sys.stdout)
      self.Logger.addHandler(ch)
      #DEBUG, INFO, WARNING, ERROR, CRITICAL
      self.Logger.setLevel(logging.INFO)
     
      self.cur_dir = 'root'
      self.myGDrive = self._connect_gdrive_()
      self.initialized = True
      if self.Logger.isEnabledFor(logging.INFO):
        self.Logger.info(pprint("Return After Connect gdrive"))
        self.Logger.info(pprint(self.cur_dir))
      
      return None
    except:
      self.myGDrive = None
      self.cur_dir = None
      self.initialized = False
      return None
  #
  #  Connect the drive
  #
  def _connect_gdrive_(self):
    #return none if failure
    #
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    t_gdrive = GoogleDrive(gauth)
    #  make sure cur_dir is good
    #
    #if self.Logger.isEnabledFor(logger.INFO):
    if(self.Logger.isEnabledFor(logging.INFO)):
      self.Logger.info(t_gdrive)
    if(t_gdrive is not None):
      self.myGDrive = t_gdrive
      directory_dictionary = self.ls('*')
      if self.Logger.isEnabledFor(logging.INFO):
        self.Logger.info("Directory Information")
        self.Logger.info(directory_dictionary['full_name'])
      if(directory_dictionary is None):
          self.cur_dir = 'root'
          return None
      return t_gdrive
    else:
      pprint("SDFG")
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
  def ls(self,name = ''):
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
    if(self.Logger.isEnabledFor(logging.INFO)):
      self.Logger.info(pprint("WORK NAME: {:s}".format(work_name)))
      #self.Logger.info(pprint(work_name.split("/")))
    
    if(len(work_name) == 0):
    #Info Information
      if(self.Logger.isEnabledFor(logging.INFO)):
        self.Logger.info("The length of the work_name is 0")
        self.Logger.info(pprint("******Start******{:s}***********".format(work_name)).split('\n'))
        self.Logger.info(pprint(None))
        self.logger.info(pprint(pformat("******End******{:s}***********".format(work_name))))
      return None
    else:
      pprint('+++++' + work_name)
      pprint(type(work_name))
      try:
        ls_file_dict = self._list_file_dict_(work_name)
      except:
        pprint("Weird")
      pprint('------')
      if(self.Logger.isEnabledFor(logging.INFO)):
        self.Logger.info(pprint("******Start******{:s}***********".format(ls_file_dict['full_name'])))
        for lf in ls_file_dict['file_result']: self.Logger.info(pprint(lf))
        self.Logger.info(pprint("******End******{:s}***********".format(ls_file_dict['full_name'])))
      return ls_file_dict
  
    
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
    if(len(name) == 0): name = 'root'
      
    work_file_info = self.ls(name)
    if self.Logger.isEnabledFor(logging.INFO):
      self.Logger.info(pformat(work_file_info['full_name']))
    if(len(work_file_info['file_result']) == 1 and 'folder' in work_file_info['file_result'][0]['mimeType']):
      self.cur_dir = work_file_info['full_name']
    elif(work_file_info['full_name'] == 'root'):
      self.cur_dir = work_file_info['full_name']
        
    return(self.getcwd())
  #
  #  Helper functions
  #
  def _build_full_path_(self, inStr=''):
    '''
    This decides on an absolute path or relative path

    Parameters:
    ----------

    inStr:  The proposed directory string

    Result:
    ------
    An absolute path starting at 'root'
    '''
    if(self.myGDrive is None):
      return(None)
    work_file_name = inStr.strip()
    if(len(work_file_name) == 0):  work_file_name = self.getcwd() + '/*'
    else:
      if self.Logger.isEnabledFor(logging.INFO):
        try:
          self.Logger.info("_build_full_path_")
          self.Logger.info(work_file_name)
          self.Logger.info(self.getcwd())
          self.Logger.info(os.path.normpath(work_file_name))
        except:
          self.Logger.info("_build_full_path_" + "except")
      if(work_file_name[0] != '/'): work_file_name = os.path.join(self.getcwd(),os.path.normpath(work_file_name))
    return work_file_name
  #
  #
  #
  def _build_path_structure_(self, inStr = ''):
    '''
    This provides a consistent path build for ColabGDrive

    Parameters:
    ----------

    inStr:  This is assumed to be an absolute path

    Result: a dictionary with the full name and the path array
      These are called full_path and path_array

    '''
  #   wStr = clean_directory_path(inStr)
    wStr = os.path.normpath(inStr)
    inStruct = wStr.split('/')
  #   wStruct = wStr.split('/')
  #   inStruct = simplify_path(wStruct)
    #house cleaning for edge cases
    if(len(inStruct) == 0): inStruct.append('*')
    if(len(inStruct) == 1 and inStruct[0] == 'root'): inStruct.append('*')
    if( not (inStruct[0] == 'root')): inStruct = ['root'] + inStruct
    pprint(inStruct)
    tStruct = None
    if(inStruct[-1] == '*'):
      tStruct = inStruct[:-1]
    else:
      tStruct = inStruct
    full_name = "/".join(tStruct)
    return({'full_name':full_name,'path_array':inStruct})
#
def _list_file_dict_(self, inStr = ''):
  '''
  Returns a dictionary with the file name and file ID (if exists) - None otherwise
  
  Parameters:
  ----------
  
  inStr:  This is assumed to be an absolute path
  
  Result:  A dictionary with the file path and file results from the FileList
    The results are called full_name and file_result
  
  '''
  pprint('!!!!!!')
  pprint(self.myGDrive)
  return False
#   try:
#     if (self.myGDrive is None):
#       return None
#     if self.Logger.isEnabledFor(logging.INFO):
#       self.Logger.info("_list_file_dict")
#       self.Logger.info(inStr)
#     file_path = self._build_path_structure_(inStr)

#     inStruct = file_path['path_array']

#     fileID = 'root'
#     fileResult = []
#     for i in range(1,len(inStruct)):
#       fileResult = []
#       file_list = self.myGDrive.ListFile({'q': "title contains '{:s}' and '{:s}' in parents and trashed=false".format(inStruct[i],fileID)}).GetList()
#       if len(file_list) == 0:
#         fileID = None
#         break
#       else:
#         if(i < len(inStruct) - 1):
#           fileID = file_list[0]['id']
#         else:
#           for j in range(len(file_list)):
#             fileName = file_list[j]['title']
#             fileID = file_list[j]['id']
#             fileType = file_list[j]['mimeType']
#             fileResult.append({"title" : fileName, "id":  fileID,'mimeType':fileType})
#     return({'full_name': file_path['full_name'],'file_result':fileResult})
#   except:
#     pprint("FAILURE")
#     return(None)
  