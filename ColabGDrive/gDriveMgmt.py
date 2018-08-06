#ColabGDrive Functions
#  tools to provide a mapping between the folder hierarchy and Google Drive storage (not the general cloud storage)
#Support libraries
import re, sys
#  First install PyDrive
#Update to use the colab pip standard
##!pip install -U -q PyDrive
import pydrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
# Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)
#
#  clean directory path
#
def cleanDirectoryPath(pathString):
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
#
#  create the queing command for directories
#
def createListFileQ(title, parentDir='root'):
  '''Return the command to use for the ListFile query.  Current targeted query
  
  This is an internal function!!!!!!
  
  title - this is the file name
  parentID - this is the parent id of the parent.  The default is root, but if you want a specific directory
    the fileID must be passed into the function.  If it is not 'root', then it is expected to be a GoogleDrive fileID
  '''
  parentStr = cleanDirectoryPath(parentDir)
  titleStr = "{:s}".format(title)
  titleStr = cleanDirectoryPath(title)
  resultStr = None
  if(titleStr == 'root'):
    resultStr = "'root' in parents and trashed = false"
  elif (parentStr == 'root'):
    resultStr = "'root' in parents and 'title = '{:s}' and trashed = flase".format(titleStr)
  else:
    resultStr = "'{:s}' in parents and title = '{:s}' and trashed = false".format(parentStr,titleStr)
  return(resultStr)
#
#  find the id for the file
#
def findFileID(inStr):
  '''Returns the Google Drive ID for the file defined by the inStr.  The inStr is assumed to be a typical Linux Path (simple form)'''
  wStr = cleanDirectoryPath(inStr)
  inStruct = wStr.split('/')
  if (not (inStruct[0] == "root")):
    inStruct = ["root"] + inStruct
  fileID = None
  for i in range(1,len(inStruct)):
    if(i == 1):
      file_list = drive.ListFile({'q': "'root' in parents and title = '{:s}' and trashed=false".format(inStruct[1])}).GetList()
      if(not file_list):
        fileID = None
        break
      else:
        fileID = file_list[0]['id']
        if(i == len(inStruct) - 1):break
    else:
      file_list = drive.ListFile({'q': "title = '{:s}' and '{:s}' in parents and trashed=false".format(inStruct[i],fileID)}).GetList()
      if(not file_list):
        fileID = None
        break
      else:
        fileID = file_list[0]['id']
        if(i == len(inStruct) - 1):break
  return(fileID)

def listFileDict(inStr):
  '''Returns a string with the file name and file ID (if exists) - None otherwise'''
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
