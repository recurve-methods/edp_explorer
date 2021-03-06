# Energy Differential Privacy Explorer


## Installation 

The application requires a local installation of Docker and docker-compose.  

- [Docker installation](https://docs.docker.com/get-docker/)
- [docker-compose installation](https://docs.docker.com/compose/install/)

To run the application, you may either launch the script `run.sh`, or use the following command:

- docker-compose up

The application will launch a local webserver and you will be able to access the application at the following URL:

- https://localhost:8050

On first launch, the database and source populations will be created.  This will take some time (30 minutes, an hour) - if you refresh the page, more populations will appear as they become available.

## Source data 

When the application runs, time series meter trace data will be read from the file `data/meter_time_series.csv`.  You may overwrite the file if you wish to use your own data.  The file must be a CSV file in "long" format with the following columns:

- `datetime` - a timestamp
- `meter_id` - a string which identifies each meter
- `electricity_kwh` - a numeric reading

See the existing file for an example.   

When the application is run, the file will be processed and converted to a listing of 24-hour load shapes for each `meter_id`.  In addition, the meter traces may be reorganized into populations, depending on the configuration present in `populations.json`.


## Populations

A group of meters is referred to as a population.  The application provides several populations to explore with differing numbers of meters and distributions of usage values.  These populations are generated by the application upon launch according to the schemes defined in `populations.json`.  


````

		{
			"label": "25000__low_var",
			"rescale": true,
			"n_meters": 25000,
			"metadata_filters": [],
			"random_seed": 1,
			"scaling": {
				"lognormal_mean": 1.5,
				"lognormal_sigma": 0.6,
				"gaussian_mean": 0,
				"gaussian_sigma": 1				
			}
		}
````


To simply use the source data as is, without any scaling or resampling, you may supply a population with the following characteristics:


````

		{
			"label": "data_unchanged",
			"rescale": false,
			"n_meters": null,			
		}
````
