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

### Model Interpretation - SHAP Values 

More information on SHAP values can be seen here:

[https://christophm.github.io/interpretable-ml-book/shap.html](https://christophm.github.io/interpretable-ml-book/shap.html)

For a brief summary:

"The first one is global interpretability — the collective SHAP values can show how much each predictor contributes, either positively or negatively, to the target variable. This is like the variable importance plot but it is able to show the positive or negative relationship for each variable with the target (see the SHAP value plot below)"

REF:

[https://towardsdatascience.com/explain-your-model-with-the-shap-values-bc36aac4de3d](https://towardsdatascience.com/explain-your-model-with-the-shap-values-bc36aac4de3d)

The script will save the summary plot to src/modeling/summary_plot.png 

The ranking of the most significant features of the model can be seen within the below (from the dataset provided). 

![alt text](https://github.com/lewisExternal/apolloDuckCanalBoatPricing/blob/main/src/modeling/summary_plot.png?raw=true)

The script will save the beeswarm plot to src/modeling/beeswarm.png 

![alt text](https://github.com/lewisExternal/apolloDuckCanalBoatPricing/blob/main/src/modeling/beeswarm.png?raw=true)

Shap values can also be used to interpret the relationship between individual features and the target variable.

The relationship between the boat price and boat length split by age can be seen here:

![alt text](https://github.com/lewisExternal/apolloDuckCanalBoatPricing/blob/main/src/modeling/length_shap.png?raw=true)

The relationship between the boat price and boat age split by length can be seen below.

![alt text](https://github.com/lewisExternal/apolloDuckCanalBoatPricing/blob/main/src/modeling/age_shap.png?raw=true)

### Log output 

Example log output from the model creation is included for reference. 

The data is within the database provided and from the time of running the mining script. 

```console

21-08-2021 19:46:40 - INFO - model has been trained
#################################################
Testing model performance
21-08-2021 19:46:40 RMSE: 30120.49
21-08-2021 19:46:40 R2: 0.47
Feature importance
year_diff: 32.52778381846008
length: 16.421931782753646
Model: 13.767382273520658
adLength: 8.796854243890277
location: 8.515559656287708
Toilet: 7.880168318411312
dealer: 6.624350436844077
berths: 5.0657144985342235
Project: 0.400254971298003
21-08-2021 19:46:41 - INFO - file has been moved: 21082021185144cat_boost_model
21-08-2021 19:46:41 - df # of records - 787
21-08-2021 19:46:41 - df_pre_cleansed # of records - 787
21-08-2021 19:46:41 - df_cleansed # of records - 787
21-08-2021 19:46:41 - df_final # of records - 518
Processing categorical variables.
#################################################
21-08-2021 19:46:41 - INFO - processing dealer
dealer
Error                                             107
Lakeland Leisure Boat Sales                        52
Rugby Boat Sales                                   52
Boatfinder Brokerage Services                      42
New and Used Boat Co Derby                         27
David Mawby Ltd                                    22
ABNB Ltd                                           20
Virginia Currer Marine Ltd                         16
ABC Leisure Group Ltd                              14
BC Boat Management Ltd                             14
Castle Boat Sales                                  14
Braunston Marina Ltd                               12
Narrowboats LTD                                    11
Blue Water Marina Ltd                              10
Venetian Marina                                     9
Swanley Bridge Marina                               7
Musk Marine Sales                                   5
Tollhouse Boat Sales                                5
Norbury Wharf Limited                               5
Aqueduct Brokerage                                  5
ABC Boats                                           5
Ashwood Marina                                      4
Houseboats at London                                4
West London Boat Brokerage                          4
NarrowCraft Brokerage                               4
Stewart Marine                                      3
RIVERHOMES Central London                           3
Premier Houseboats                                  3
Marine Services (Chirk) Ltd                         3
Midway Boats Limited                                3
Boat Showrooms of London                            3
Frouds Bridge Marina                                3
Ely Marine Ltd                                      2
Alan G Pease                                        2
Victoria Quay Marina Ltd                            2
TBS Boats Bray Ltd                                  2
Fish & Duck Leisure Ltd                             1
Tingdene Boat Sales - Upton Marina                  1
Liverpool Boat Sales                                1
Weltonfield Narrowboats Ltd                         1
Aquavista Ltd                                       1
Homesafloat                                         1
Great Haywood Boat Sales Ltd                        1
Boatinland                                          1
Tingdene Narrowboats                                1
Tingdene Boat Sales - Thames and Kennet Marina      1
Roydon Boat Sales                                   1
Tingdene Boat Sales - Stourport Marina              1
TBS Boats Penton Hook                               1
Longport Brokerage                                  1
Classic Yacht Brokerage                             1
Premier Marine Ltd.                                 1
Sirius Marine Services ltd                          1
First Peninsula Marine                              1
York Marina                                         1
Name: id, dtype: int64
#################################################
#################################################
21-08-2021 19:46:41 - INFO - processing berths
berths
4    184
2    145
1     86
6     52
3     29
5     15
8      6
7      1
Name: id, dtype: int64
#################################################
#################################################
21-08-2021 19:46:41 - INFO - processing Model
Model
cruiser       183
trad          177
semitrad       86
widebeam       53
none           10
tug             5
dutchbarge      4
Name: id, dtype: int64
#################################################
#################################################
21-08-2021 19:46:41 - INFO - processing Project
Project
False    508
True      10
Name: id, dtype: int64
#################################################
#################################################
21-08-2021 19:46:41 - INFO - processing Toilet
Toilet
none         224
cassette     140
pumpout       93
macerator     37
compost       22
sealand        2
Name: id, dtype: int64
#################################################
#################################################
21-08-2021 19:46:41 - INFO - processing location
location
Northamptonshire    85
Cheshire            74
London              56
Staffordshire       38
Midlands            28
Essex               28
Gloucestershire     28
Leicestershire      26
Yorkshire           22
Derbyshire          16
Surrey              14
Worcestershire      13
Warwickshire        11
Berkshire           11
Buckinghamshire      9
Oxfordshire          9
Lancashire           8
Lincolnshire         7
Wiltshire            6
Kent                 4
Hertfordshire        4
Cambridgeshire       4
Wrexham              3
Bristol              3
Merseyside           2
Somerset             2
Shropshire           2
Nottinghamshire      1
Monmouthshire        1
Manchester           1
Cumbria              1
location.            1
Name: id, dtype: int64
#################################################
Processing numerical variables.
#################################################
21-08-2021 19:46:41 - INFO - processing length
21-08-2021 19:46:41 - INFO - max value is: 75
21-08-2021 19:46:41 - INFO - min value is: 10
21-08-2021 19:46:41 - INFO - mean value is: inf
21-08-2021 19:46:41 - INFO - median value is: 58.0
#################################################
#################################################
21-08-2021 19:46:42 - INFO - processing year_diff
21-08-2021 19:46:42 - INFO - max value is: 116
21-08-2021 19:46:42 - INFO - min value is: 0
21-08-2021 19:46:42 - INFO - mean value is: 19.231660231660232
21-08-2021 19:46:42 - INFO - median value is: 17.0
#################################################
#################################################
21-08-2021 19:46:42 - INFO - processing adLength
21-08-2021 19:46:42 - INFO - max value is: 9351
21-08-2021 19:46:42 - INFO - min value is: 245
21-08-2021 19:46:42 - INFO - mean value is: 1685.915057915058
21-08-2021 19:46:42 - INFO - median value is: 1431.0
#################################################

```


## Requirements

Requires python 3.8

Docker (for the .bat files)
