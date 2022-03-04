#!/bin/env python3
from cache import Cacheable
import hashlib
import pandas as pd
from database import load_data, DB
db = DB()


def population_hash():
	with open('populations.json', 'r') as f:
		text = f.read()
	return hashlib.sha224(text.encode()).hexdigest()

def populations_have_changed():
	if not db.table_exists('load_hash'):
		return True
	old_hash = db.query_df('select hash from load_hash')['hash'].iloc[0]
	new_hash = population_hash()
	return old_hash != new_hash
	

if not db.data_loaded() or populations_have_changed():
	print("Loading data")
	load_data('data/nrel/meter_time_series.csv', 'electricity_kwh', 'datetime', 'meter_id', 'populations.json')
	df = pd.DataFrame({'hash': population_hash()}, index=[0])
	db.load_df(df, 'load_hash')

	print("Data loaded")

# class PreCache(Cacheable):
# 	def __init__(self, db_client):
# 		self.db_client = db_client
# 		super().__init__()
# 		self.clear_cache()
	
# 	def private_load_shape(self, population, n_points, quantile_cutoff):
# 		pop = BuiltPopulation(db_client=self.db_client, label=population)
# 		def get():
# 			return pop.private_load_shape(n_points, quantile_cutoff)
# 		return self.cache_func(get, self.make_cache_key([population, n_points, quantile_cutoff]))

# # pre-load each population so it's already cached 
# c = PreCache(db)
# print("Pre-loading populations")
# pop_labels = db.query_df('select distinct population from population')['population']
# for pop in pop_labels:
# 	for n_points in [1,2,4,8,12,24]:
# 		for quantile_cutoff in [0,0.01,0.02,0.03,0.04,0.05]:
# 			c.private_load_shape(pop, n_points, quantile_cutoff)

# print("Populations pre-loaded")