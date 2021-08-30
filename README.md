# getMODIS
## What is it
This repertory contains the code to download the MODIS data and in particular the MOD09A1 (it can be adapted for other products) from the Earth Data webpage.
It also gives the possibility to get the longitude and latitude of the downloaded tiles and save it in a netCDF file.

Before getting stareted yiou have to make sure to have an account on https://earthdata.nasa.gov/.

The code has been constructed to join two MODIS vertical neighbours tiles. It also works for a single tiles. For now, it is recommended to download / process separatly yhe different tiles.

## Getting started
### Find the data
Before launching the program you have to find the list of links of the data you want to do so : 

1. you can make your search on https://search.earthdata.nasa.gov/search
2. Search, for example, MOD09A1
3. Select a region of study, it is better if it just include one tile
4. Select the right period
5. Then click on download the granules, you will have to connect with youtr account.
6. Select Direct Download, you will access to a list of link that you can save.

This will be the link file used. 

### Prepare the config file
Then, you will have to create and complete a config.def file in the main directory of the project, the following elements must be filled : 

* username
* password

*Take care to keep your file in a secured place so nobody can access your username and password*

* output : directory where you will save your output
* links : file with the links

### Download
The raw file will be download in the **output** directory, in a subdirectory called RAW.
To download you have to launch : 

```bash
python 1_main_download.py
```
### Post process
To post process the file you have to launch :

```bash
python 2_main_save.py
```
This will create a file with the longitude / latitud coordinate of MODIS and a file with the data.


