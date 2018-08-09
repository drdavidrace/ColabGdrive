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
  wStr = clean_directory_path(inStr)
  wStruct = wStr.split('/')
  inStruct = []
  #Take care of standard unix '.' and '..'
  for name in wStruct:
    if(name == '.'):
      pass
    elif (name == '..'):
      inStruct = inStruct[:-1]
    else:
      inStruct.append(name)
  print(inStruct)
  #house cleaning for edge cases
  if(len(inStruct) == 0): inStruct.append(['*'])
  if( not (inStruct[0] == 'root')): inStruct = ['root'] + inStruct
  print(inStruct) 
  fileID = None
  fileResult = []
  for i in range(1,len(inStruct)):
    fileResult = []
    if(i == 1):
      file_list = drive.ListFile({'q': "'root' in parents and title contains '{:s}' and trashed=false".format(inStruct[1])}).GetList()
      if(not file_list):
        fileID = None
        break
      else:
        for j in range(len(file_list)):
          fileID = file_list[j]['id']
          fileType = file_list[j]['mimeType']
          if(i == len(inStruct) - 1):
            fileName = file_list[j]['title']
            fileResult.append({"title" : fileName, "id":  fileID, "mimeType": fileType})
    else:
      file_list = drive.ListFile({'q': "title contains '{:s}' and '{:s}' in parents and trashed=false".format(inStruct[i],fileID)}).GetList()
      if(not file_list):
        fileID = None
        break
      else:
        for j in range(len(file_list)):
          fileName = file_list[0]['title']
          fileID = file_list[0]['id']
          fileType = file_list[0]['mimeType']
          if(i == len(inStruct) - 1):
            fileName = file_list[j]['title']
            fileResult.append({"title" : fileName, "id":  fileID,'mimeType':fileType})
  return(fileResult)
