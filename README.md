# Data Engineer - Technical Test

## Documentation

## First Part


### Implementation


Since I was going to containerize this anyways with docker, I decided to use dash, in order to be able to show the data for both functionalities using the same library as the one on https://chart-studio.plotly.com/.

This means that you can access the preview on http://localhost:5000, and you get a quick overview of how they both work (with some simple click navigation). Of course running `python app.py` guarantees that the data pipeline will be run, as this is done before running the dash app.

The ETL code has been developed having the code in `data_handler.py` inside `src`. `call_handler.py` has been implemented to act as the raw code for handling the calls to the dash app. If you wanted purely the pipeline, you could easily:
- replicate into `app.py` (removing everything it currently has) the code from the functions `load_data()` and `create_all_csv()` that are in `call_handler.py`
- remove `call_handler.py`
- remove dash imports from `app.py`
- remove dash dependency from `requirements.txt`

#### A couple noteworthy design choices:
- Made the 2nd functionality (Account Distribution per Country) use the day as parameter to generate the data
- Implemented load function to load data only initially
- Tried to follow PEP standards and prepare all functions to generate a documentation
- Purged control characters before performing any operation on user-written fields of the .jsonl file
- Separated:
  - dash pathname handling `app.py`
  - logic `call_handler.py`
  - data_handing `data_handler.py`

#### TO-DOs:
- Add documentation generator and folders for it
- Use a python library instead of the regex matches used to extract the FQDN
- In hindsight, it may have made sense implementing the two functionalities as separate containers. I'd have to look into this.
- Test docker image builder

### Testing


#### To run the data pipeline you should have the test files provided:

- account_countries.csv
- allowed_origins.jsonl
- server_logs.csv


#### To test this script locally:
1. Move the test files to test_data
2. Run  `python app.py` or `docker-compose up`(and leave it running)
3. New files have been generated in output_data
4. Test functionalities a bit in http://localhost:5000




## Second Part

#### Objective 1
[Account Distribution per Country](https://chart-studio.plotly.com/dashboard/xarxaxdev:0/view)

#### Objective 2
[Hits per domain on the 15th](https://chart-studio.plotly.com/dashboard/xarxaxdev:1/view)
