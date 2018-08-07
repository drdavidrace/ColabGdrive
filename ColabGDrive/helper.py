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

def list_file_dict(drive = None, inStr = ''):
  '''Returns a dictionary with the file name and file ID (if exists) - None otherwise'''
  if (drive is None):
    return None

  wStr = cleanDirectoryPath(inStr)
  inStruct = wStr.split('/')
  if (not (inStruct[0] == "root")):
    inStruct = ["root"] + inStruct
  fileID = None
  fileResult = None
  for i in range(1,len(inStruct)):
    if(i == 1):
      file_list = drive.ListFile({'q': "'root' in parents and title = '{:s}' and trashed=false".format(inStruct[1])}).GetList()
      if(not file_list):
        fileID = None
        break
      else:
        fileID = file_list[0]['id']
        if(i == len(inStruct) - 1):
          fileName = inStruct[i]
          fileResult = {"title" : fileName, "id":  fileID}
          break
    else:
      file_list = drive.ListFile({'q': "title = '{:s}' and '{:s}' in parents and trashed=false".format(inStruct[i],fileID)}).GetList()
      if(not file_list):
        fileID = None
        break
      else:
        fileID = file_list[0]['id']
        if(i == len(inStruct) - 1):
          fileName = inStruct[i]
          fileResult = {"title" : fileName, "id":  fileID}
          break
  return(fileResult)
