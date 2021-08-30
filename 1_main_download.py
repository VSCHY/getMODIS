import sys
sys.path.append("library")
from lib_download import download
import configparser
import tqdm
import os

########################
# 1. Download the data #
########################

# Get username and password from the config.def file
config=configparser.ConfigParser()
config.read("config.def")
output=config.get("OverAll", "output") 
links=config.get("OverAll", "links") # links.txt

if not os.path.exists(output):
    print("Error - the directory doesn't exists")
else:
    if not os.path.exists(output+"/RAW"):
        os.makedirs(output+"/RAW")
        
file1 = open(links, 'r')
Lines = file1.readlines()
 
count = 0
for line in tqdm.tqdm(Lines):
    count+=1
    download(line.strip(), output+"/RAW/")
    
