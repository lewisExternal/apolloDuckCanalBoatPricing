# Apollo Duck Canal Boat Pricing

This repo mines canal boat data, trains a machine learning model to estimate price and is deployed to a simple flask application within a Docker container.

## Data

Boat pricing data was sourced from Apollo Duck adverts, the link.

[https://narrowboats.apolloduck.co.uk/boats-for-sale](https://narrowboats.apolloduck.co.uk/boats-for-sale)

## How to run

Required scripts can be found within the ./bin subdirectory.

### Data mining script

This script was originally developed on a Raspberry Pi OS, Raspbian GNU/Linux 10 (buster).

Dependencies will be installed inside a virtual environment upon script execution.

The following script can be run with required command line argument:

>1. (Required) Lookup boat adverts [default] y

An example request can be seen below.

```console

./run_scraping_script.sh y

```

Running the script with the "y" argument will look up new boat adverts. This is required if the initial run of the script. Which will then be saved into the SQLite database as table 'adverts'.

If the script does not process all of the boat adverts, the argument "n" can be passed instead and skip looking up further boat adverts.  This will process adverts into the 'boats' data table with attribute information.

```console

./run_scraping_script.sh n

```

Results will be saved within a SQLite database (file: pythonsqlite.db) with the schemas below.

```console

ADVERTS

id integer PRIMARY KEY,

link text NOT NULL,

processed INT NOT NULL

```

```console

BOATS

id integer PRIMARY KEY,

link text,

price text,

status text,

desc text,

specs text,

dealer text,

title text,

location text

```

### Model Training &  Deployment

This script was originally developed for Windows 10.  Please note, dependencies will not be automatically installed.

The following script will reference the SQLite database (file: pythonsqlite.db).

```console

run_create_model.bat

```

The script will extract features and preform data cleansing, the script will also visualise features for which are quantitative.

The script will then create a Docker image from a Dockerfile and run the container, a Flask application with API access to the machine learning  pricing model. Please see the API help page for more details.

```console

http://localhost:5000/help

# Please see quick start instructions below.

Configurable parameters are as follows:

-  length: e.g. 45

-  berths: e.g. 2

-  age: e.g. 30

-  model: e.g. semitrad

-  toilet: e.g. pumpout

The following parameters are assumed:

-  dealer = 'Error': no dealer

-  project = False: not a project boat

-  adLength = 1431: sample median advert length

-  location = 'London': assume within london

Categorical variables entered incorrectly will return accepted values.

```

An example request can be seen below.

```console

http://localhost:5000/v1/api?length=45&berths=2&age=30&model=trad&toilet=cassette

```

The example JSON response would be:

```console

{

"Model": "trad",

"Project": false,

"Toilet": "cassette",

"adLength": 1431,

"age": 30,

"berths": 2,

"dealer": "Error",

"length": 45,

"location": "London",

"price": 35238.87188879248

}

```

** Please note, some features are assumed for convenience.

### Push to Docker

The following script will tag and push the image to docker, the repository must be specified.  Also developed for Windows 10.

```console

tag_push_image.bat

```

## Requirements

Requires python 3.8

Docker (for the .bat files)