A script to fetch and save information on Stream games.

Steam pages utilise Javascript, so Playwright is employed to render pages for extractions.

Three stages are being employed:
* extraction - Render and extract raw data from webpages
* transform - Transform data into more suitable formats
* output - Stores data to local csv files

Configure the data being extracted by updating the _extraction_config settings in extraction.py.

To do:
* Move extraction config into a separate json file