#ColabGDrive Functions
#  tools to provide a mapping between the folder hierarchy and Google Drive storage (not the general cloud storage)
#Support libraries
import re, sys
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
    if(gdrive is None):
      return(inStr)
    work_file_name = inStr
    if(len(work_file_name) == 0):  work_file_name = gdrive.getcwd() + '/*'
    else:
      if(work_file_name[0] != '/'): work_file_name = gdrive.getcwd() + '/' + clean_directory_path(work_file_name)
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
#
def list_file_dict(drive = None, inStr = ''):
  '''Returns a dictionary with the file name and file ID (if exists) - None otherwise'''
  if (drive is None):
    return None
  wStr = clean_directory_path(inStr)
  wStruct = wStr.split('/')
  inStruct = simplify_path(wStruct)
  print(inStruct)
  
#   print(inStruct)
  #house cleaning for edge cases
  if(len(inStruct) == 0): inStruct.append('*')
  if(len(inStruct) == 1 and inStruct[0] == 'root'): inStruct.append('*')
  if( not (inStruct[0] == 'root')): inStruct = ['root'] + inStruct
#   print(inStruct) 
  fileID = 'root'
  fileResult = []
  for i in range(1,len(inStruct)):
    fileResult = []
    file_list = drive.ListFile({'q': "title contains '{:s}' and '{:s}' in parents and trashed=false".format(inStruct[i],fileID)}).GetList()
    if(not file_list):
      fileID = None
      break
    else:
      if(i < len(iStruct) - 1):
        fileID = file_list[0]['id']
      else:
        for j in range(len(file_list)):
          fileName = file_list[j]['title']
          fileID = file_list[j]['id']
          fileType = file_list[j]['mimeType']
          fileResult.append({"title" : fileName, "id":  fileID,'mimeType':fileType})
  return(fileResult)
