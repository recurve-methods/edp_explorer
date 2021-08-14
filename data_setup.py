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
	

def data_hash():
	with open('data/meter_time_series.csv', 'r') as f:
		text = f.read()
	return hashlib.sha224(text.encode()).hexdigest()


def data_has_changed():
	if not db.table_exists('data_hash'):
		return True
	old_hash = db.query_df('select hash from data_hash')['hash'].iloc[0]
	new_hash = data_hash()
	return old_hash != new_hash



if not db.data_loaded() or populations_have_changed() or data_has_changed():
	print("Loading data")
	load_data('data/meter_time_series.csv', 'electricity_kwh', 'datetime', 'meter_id', 'populations.json')
	df = pd.DataFrame({'hash': population_hash()}, index=[0])
	db.load_df(df, 'load_hash')

	print("Data loaded")

