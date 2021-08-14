#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

   Copyright 2021 Recurve Analytics Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""


import pandas as pd
from sqlalchemy import create_engine, inspect
from population import generate_populations
import os 
from time import sleep

class DB:
	def __init__(self):		
		connection_string = os.environ.get('DATABASE_URL', 'postgresql://edo:edo@db/edo')
		connection_string = connection_string.replace('postgres://', 'postgresql://')
		print(connection_string)
		self.engine = create_engine(connection_string)

	def con(self):
		con = self.engine.connect()
		return con 
		


	def table_has_data(self, table):
		if self.table_exists(table):
			if self.query_df(f"select count(*) as n from {table}")['n'].iloc[0] > 0:
				return True
			return False

	def data_loaded(self):
		return self.table_has_data('load_finished')

	def populations_generated(self):
		return self.table_has_data('population')


	def private_load_shape(self, population, quantile_cutoff, n_points, epsilon):
		pass


	def query(self, sql):
		con = self.con()
		con.execute(sql)
		con.close()

	def query_df(self, sql):
		con = self.con()
		df = pd.read_sql_query(sql, con)
		con.close()
		return df

	def table_exists(self, table):
		return inspect(self.engine).has_table(table)
			
	def drop_table(self, table):
		if self.table_exists(table):
			self.query(f'drop table if exists {table}')

	def load_df(self, df, table_name, append=False):
		if append:
			if_exists = 'append'
		else:
			if_exists = 'replace'
		con = self.con()
		df.to_sql(table_name, con, if_exists=if_exists)
		con.close()


	def meter_ids(self):
		return self.query_df(f"select distinct meter_id from meter_time_series")

	def time_series(self, meter_id):
		return self.query_df(f"select * from meter_time_series where meter_id='{meter_id}'")

	def time_series_daily(self, meter_id):
		return self.query_df(f"select * from meter_time_series_daily where meter_id='{meter_id}'")



def load_data(time_series_csv_path, value_col, datetime_col, index_col, population_json_path):
	print(f"loading {time_series_csv_path}")
	db_client = DB()

	db_client.drop_table('meter_time_series')
	db_client.drop_table('meter_time_series_daily')
	db_client.drop_table('population')
	db_client.drop_table('load_finished')

	df = pd.read_csv(time_series_csv_path)
	df['value'] = df[value_col]
	df['datetime'] = df[datetime_col]
	df['meter_id'] = df[index_col]
	df = df[['meter_id', 'datetime', 'value']]
	db_client.load_df(df, 'meter_time_series')

	df = db_client.query_df('select * from meter_time_series')
	df['datetime'] = pd.to_datetime(df['datetime'])
	df['hour'] = df.datetime.dt.hour
	df = df.groupby(['meter_id', 'hour']).mean()['value'].reset_index()
	db_client.load_df(df, 'meter_time_series_daily')


	generate_populations(population_json_path, db_client)

	df = pd.DataFrame({'Finished': True}, index=[0])
	db_client.load_df(df, 'load_finished')
	print("Done")
	return True
