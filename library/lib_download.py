import sys

import requests 
from datetime import date, timedelta
import numpy as np 
import os 
import subprocess
import time
import multiprocessing
import random
import glob

import configparser
import tqdm

#https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
# overriding requests.Session.rebuild_auth to mantain headers when redirected

config=configparser.ConfigParser()
config.read("config.def")
username=config.get("OverAll", "username")
password=config.get("OverAll", "password")

class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'
    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)
 
   # Overrides from the library to keep headers when redirected to or from
   # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return

def download(url, doutput):
    t0 = time.time()
    filename = url[url.rfind('/')+1:] 
    
    if not os.path.isfile(doutput + filename):
        #print(filename)
        session = SessionWithHeaderRedirection(username, password)
        #try:
        time.sleep(1)
        
        response = session.get(url)
        response.raise_for_status()
        try:
          f = open(doutput + filename,'wb')
          f.write(response.content)
          f.close()    
          response.close()
        except requests.exceptions.ConnectionError:
          print("Connection error")
          try:
             response.close()
             session.close()
          except:
             session.close()
             time.sleep(2)
        except:
           print('requests.get() returned an error code '+str(response.status_code))
           try:
               response.close()
               session.close()
           except:
               session.close()
               time.sleep(2)  
        session.close()

