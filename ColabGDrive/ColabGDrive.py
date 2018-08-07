import os, sys, re
import importlib
importlib.reload(pip)

class ColabGDrive:
  
  def __init__(self, current_dir = 'root'):
    try:
      import pydrive
      from pydrive.auth import GoogleAuth
      from pydrive.drive import GoogleDrive
      from google.colab import auth
      from oauth2client.client import GoogleCredentials
      print("PyDrive Already Exists")
    except:
      pip.main(['install','-U -q','PyDrive'])
      #print('pydrive is not installed')
      #subprocess.call(['pip', 'install -U -q','PyDrive'])
      import pydrive
      from pydrive.auth import GoogleAuth
      from pydrive.drive import GoogleDrive
      from google.colab import auth
      from oauth2client.client import GoogleCredentials
      print("PyDrive installed and imported")
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    self.myGdrive = GoogleDrive(gauth)
