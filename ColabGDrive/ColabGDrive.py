import os, sys, re
import subprocess
import importlib
importlib.reload(pip)

class ColabGDrive:
  
  def __init__(self, current_dir = 'root'):
    try:
      subprocess(['python','-m','pip','install','-U -q','PyDrive'])
      import pydrive
      from pydrive.auth import GoogleAuth
      from pydrive.drive import GoogleDrive
      from google.colab import auth
      from oauth2client.client import GoogleCredentials

    except:
      #print('pydrive is not installed')
      subprocess.call(['python','-m','pip', 'install -U -q','PyDrive'])
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
