# arggis_scanner_cdgc
protoytype scanner for ArcGIS REST Services Directory

Features:-
- connect to ArcGIS site via URL e.g. https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services
 and extract metadata about 
  - Services (FeatureServer)
  - Layers - Services can have multiple layers
  - Fields - Layers have fields, position and type are extracted
- URL for the Services/Layers are stored in Description
  - URL for Services Directory link
  - URL for Map Link
  - URL for Query Link  - only for Services, not valid for Layers


## implemention notes

- is server necessary? the cdgc catalog source could act as the server
- some Services have duplicate layer names
    - see https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services/PotentialInundation_Temp/FeatureServer
    - these layters are mostly the same, with some small differences (all else is identical)
      - diff:  extent object has different x/y min/max
      - diff:  domain in first occurrence has values, 2nd is null
      - diff:  index name and content are a little different
    - should we identify only by id & also suffix the id in the object name?

- some fields have aliases- since fields do not have a description, will store it there for now
  - example in Air_Quality_Index_Layers_WFL1


## How to run

the scanner is implemented as a python script, and requires the requests module to be installed

pip install requests

you may want to setup/use a virtual environment to isolate package dependencies

linux/macos
```
python3 arcgis/arcgis_scanner.py --url https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services
```

windows
```
py arcgis/arcgis_scanner.py --url https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services
```

starting the process with -h, will print the command-line help

```
usage: arcgis_scanner.py [-h] [--url URL] [-l LIMIT]

options:
  -h, --help            show this help message and exit
  --url URL             ArcGIS url to scan - e.g. https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services
  -l LIMIT, --limit LIMIT
                        limit the number of services to scan
```


## basic process

- call crawler.py passing the url to scan (hard coded for now)
  https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services
- get that server object - which is really just a collection of services
  - for each service
    - call a read_service process (which creates the service object)
      - iterate over the layer links
        - call read_layer for each one (passing the layer ref info)
          - export the layer object
          - layers have fields (although some have sublayers that have fields)
            - for each field - create an object


## TODO - features to implement

- command-line parameters
  - --out_folder folder to write files (default is ./out)

- remove dependency on requests module (need to pip install requests currently to run)


## Updates

- 2024-09-23 bugfixes
  - if the layer data cannot be extrcted (returns Token Required), the error was not handled and the scanner exited
  - if the layer data was not returned, due to timeout, the cdgc writer failed and the scanner exited.  set timeout to 10sec & handled the error if timeout occurs
