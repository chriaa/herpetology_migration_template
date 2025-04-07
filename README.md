# Herpetology Migration Template

This is a template workflow for migrating the contents of the herpetology database into the CALAS wider specify collections database.


Notes/Works in progress:

* Currently the application outputs transformed data into an excel spreadsheet. This will be expanded to include direct import into a test instance of the specify database.
* This only supports 1 to 1 table transformations (i.e. you can only write changes that impact a single table)
* There is no error handling, godspeed

## Set Up

### Datasets

Obtain a copy of the *herpetology database* and use it to populate a docker instance (*instructions coming soon*) as well as access to the *FIELD_MAPPING_DICTIONARY.*

### requirements.txt

* Create a virtual environment with `virtualenv venv` (for macos)
* install the necessary requirements using the command `pip install -r requirements.txt`

### .env file

Define a .env file with the following format and substitute your own database credentials:

#Source Database Configuration

HERP_DB_HOST="127.0.0.1"

HERP_DB_DATABASE="herpetology"

HERP_DB_USER="root"

HERP_DB_PASSWORD="password"

HERP_DB_PORT=3308

#SPECIFY Database Configuration

SPECIFY_DB_HOST="127.0.0.1"

SPECIFY_DB_DATABASE="casbotany"

SPECIFY_DB_USER="root"

SPECIFY_DB_PASSWORD="password"

SPECIFY_DB_PORT=3301

## Defining your Transformations

You can define your own transformations for different fields by writing your own logic into the `apply_transformations` function within app.py. The function is given a list of dictionaries where the user may define their own transformations in accordance with the HERPETOLOGY_FIELD_MAPPING document. 

The current ` apply_transformations` function contains code for a simple transformation as an example. All entries under the field 'Local Annotation' are changed to 'this is a test'.

*Example of a single entry:*

```
{'catno': 10, 'origno': 532, 'prefix': None, 'museum': 'CAS', 'class': 'Reptilia', 'ordersub': 'Sauria', 'family': 'Phrynosomatidae', 'groupno': '25', 'genus': 'Sceloporus', 'sp': 'occidentalis', 'ssp': None, 'status': None, 'sex': None, 'continen': 'North America', 'country': 'USA', 'state': 'California', 'ids': None, 'id': None, 'county': 'Alameda Co.', 'local': 'Oakland', 'collect': 'W.E. Bryant', 'recd': None, 'datecoll': '1891', 'preserv': 'Alc', 'accno': None, 'idby': None, 'iddate': None, 'stage': None, 'storage2': None, 'skel': None, 'nospec': '0', 'elev': None, 'remarks': 'Lost in earthquake and fire of 1906.', 'ecodata': None, 'checkby': 'FHK, 26 May 1993', 'origloc': 'Oakland, California', 'catby': None, 'musacr': None, 'musno': None, 'fieldno': None, 'dateyear': 1891, 'elevfrom': None, 'elevto': None, 'elevunit': None, 'storage': None, 'latdeg': 37.0, 'latmin': 48.0, 'latsec': 16.0, 'latdir': 'N', 'longdeg': 122.0, 'longmin': 16.0, 'longsec': 11.0, 'longdir': 'W', 'curate': None, 'coorig': 'N', 'idgroup': None, 'dateday': None, 'datemonth': None, 'LatText': None, 'LongText': None, 'TRS': None, 'Township': None, 'Townshipdir': None, 'Range': None, 'Rangedir': None, 'TRSsection': None, 'TRSpart': None, 'DetByPerson': 'M.S. Koo', 'DetDate': '12 Mar 1997', 'DetRef': 'Place-Name-Index, Buckmaster Publishing, 1988', 'OrigCoordSystem': None, 'Datum': None, 'DecLat': None, 'DecLong': None, 'UTMZone': None, 'UTMEW': None, 'UTMNS': None, 'MaxErrorDist': None, 'MaxErrorUnits': None, 'LatLongRemarks': None, 'NoGeoRef': None, 'LocalAnnotation': 'this is a test', 'Extent': None, 'NamedPlace': None, 'CurrentGenus': None, 'CurrentSp': None, 'CurrentSsp': None}
```


## Running the Application

Run the application by running: `python app.py` from the main directory.

Any outputs generated will be stored in the output folder.
