#ColabGDrive Functions
#  tools to provide a mapping between the folder hierarchy and Google Drive storage (not the general cloud storage)
#Support libraries
import os, re, sys
#
#  clean directory path
#
def clean_directory_path(pathString):
  '''Returns a cleaned up path string.
  
  Currently no checks for a string, but probably should be added.
  
  This is an internal function!!!!!!
  
  '''
  wStr = pathString.strip()
  wStr = re.sub('\/\/+', '/', wStr)
  if(wStr[0] == "/"):
    wStr = wStr[1:]
  if(wStr[-1] == "/"):
    wStr = wStr[:-1]
  return(wStr)

def build_full_path(gdrive = None, inStr=''):
  '''
  This decides on an absolute path or relative path
  
  Parameters:
  ----------
  gdrive:  The ColabGDrive being used (so we know the current working directory)
  
  inStr:  The proposed directory string
  
  Result:
  ------
  An absolute path starting at 'root'
  '''
  if(gdrive is None):
    return(None)
  work_file_name = inStr.strip()
  if(len(work_file_name) == 0):  work_file_name = gdrive.getcwd() + '/*'
  else:
    #if(work_file_name[0] != '/'): work_file_name = gdrive.getcwd() + '/' + clean_directory_path(work_file_name)
    if(work_file_name[0] != '/'): work_file_name = os.path.join(gdrive.getcwd(),os.normpath(work_file_name))
  return work_file_name
  
def simplify_path(path_array):
  '''
  This simplifies the path for the standard Linux . and ..
  If ., then that is dropped from the output path array
  If .., then it is backed up one level in the hierarchy
  
  Parameters:
  -----------
  path_array - This is the array for the path
  
  Returns:
  --------
  simple_array - This is the path array after the . and .. were applied.
  '''
  simple_array = []
  #Take care of standard unix '.' and '..'
  for i in range(len(path_array)):
    name = path_array[i]
    if(name == '.' and i < len(path_array) - 1):
      pass
    elif (name == '..'):
      simple_array = simple_array[:-1]
    else:
      simple_array.append(name)
  return simple_array

def build_path_structure(inStr = ''):
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
  wStruct = wStr.split('/')
  inStruct = simplify_path(wStruct)
  #house cleaning for edge cases
  if(len(inStruct) == 0): inStruct.append('*')
  if(len(inStruct) == 1 and inStruct[0] == 'root'): inStruct.append('*')
  if( not (inStruct[0] == 'root')): inStruct = ['root'] + inStruct
  tStruct = None
  if(inStruct[-1] == '*'):
    tStruct = inStruct[:-1]
  else:
    tStruct = inStruct
  full_name = "/".join(tStruct)
  return({'full_name':full_name,'path_array':inStruct})
#
def list_file_dict(drive = None, inStr = ''):
  '''
  Returns a dictionary with the file name and file ID (if exists) - None otherwise
  
  Parameters:
  ----------
  drive:  The object pointing to the Google Drive
  
  inStr:  This is assumed to be an absolute path
  
  Result:  A dictionary with the file path and file results from the FileList
    The results are called full_name and file_result
  
  '''
  if (drive is None):
    return None
  
  file_path = build_path_structure(inStr)
  
  inStruct = file_path['path_array']
  
  fileID = 'root'
  fileResult = []
  for i in range(1,len(inStruct)):
    fileResult = []
    file_list = drive.ListFile({'q': "title contains '{:s}' and '{:s}' in parents and trashed=false".format(inStruct[i],fileID)}).GetList()
    if len(file_list) == 0:
      fileID = None
      break
    else:
      if(i < len(inStruct) - 1):
        fileID = file_list[0]['id']
      else:
        for j in range(len(file_list)):
          fileName = file_list[j]['title']
          fileID = file_list[j]['id']
          fileType = file_list[j]['mimeType']
          fileResult.append({"title" : fileName, "id":  fileID,'mimeType':fileType})
  return({'full_name': file_path['full_name'],'file_result':fileResult})
