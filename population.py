import pandas as pd
import simplejson as json 
import numpy as np
from privacy import PrivateLoadShape
import logging
logger = logging.getLogger(__name__)


import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_uploader as du 
import flask 


import plotly.express as px
import plotly.graph_objs as go
from cache import Cacheable


class Population:
	def __init__(self, db_client, label, rescale, n_meters, scaling, random_seed=1):
		self.label = label
		self.db_client = db_client
		self.rescale = rescale
		self.n_meters = int(n_meters)
		self.scaling = scaling 
		if self.rescale:
			for f in ['lognormal_mean', 'lognormal_sigma', 'gaussian_mean', 'gaussian_sigma']:
				if not f in self.scaling.keys():
					raise ValueError(f"Population param 'scaling' must contain field '{f}'")
		


	def generate(self):		
		i = 0
		logger.info("Generating meter population")
		meter_ids = self.db_client.meter_ids()
		output_meter_ids = meter_ids.sample(self.n_meters, replace=True)
		for m in output_meter_ids.meter_id.values:
			df = self.db_client.time_series_daily(m)
			df = self.transform(df)
			df['meter_id'] = str(i) + "_" + df['meter_id']
			df['population'] = self.label
			i = i+1
			df = df.set_index(['population', 'meter_id', 'hour'])
			self.db_client.load_df(df, 'population', append=True)

	def transform(self, df):
		if self.rescale:
			df['value'] = df['value'] / df['value'].max()
			noise = np.random.normal(loc=self.scaling['gaussian_mean'],
								scale=self.scaling['gaussian_sigma'],
								size=len(df))
			df['value'] = df['value'] + noise
			factor = np.random.lognormal(mean=self.scaling['lognormal_mean'],
								sigma=self.scaling['lognormal_sigma'])
			df['value'] = df['value'] * factor
		return df


# class BuiltPopulation:

# 	def __init__(self, db_client, label, high_outlier=False):
# 		self.db_client = db_client
# 		self.label = label 
# 		self.high_outlier = high_outlier

# 	def get(self):
# 		df = self.db_client.query_df(f"select * from population where population='{self.label}'")
# 		if self.high_outlier:
# 			df = df 
# 		return df

# 	def resample_hours(self, df, n_points):
# 		df['hour'] = df['hour'] // (24/n_points)
# 		df = df.groupby(['population','meter_id','hour']).mean().reset_index()		
# 		return df 

# 	def private_load_shape(self, n_points, quantile_cutoff):
# 		df = self.get()
# 		df = self.resample_hours(df, n_points)
# 		return PrivateLoadShape(df, index_column='meter_id', time_column='hour', value_column='value', 
# 				quantile_cutoff_lower=0, quantile_cutoff_upper=1-quantile_cutoff)
					


class PlottingPopulation(Cacheable):
	def __init__(self, db_client, population, high_outlier, n_points=24, quantile_cutoff=0):
		self.db_client = db_client
		self.population = population
		self.high_outlier = high_outlier 
		self.n_points = n_points
		self.quantile_cutoff = quantile_cutoff 
		super().__init__()

	def load_shape(self):
		if not self.ready():
			return None

		def get():
			df = self.db_client.query_df(f"select * from population where population='{self.population}'")

			if self.high_outlier:
				total_load_shape = df.groupby(['hour']).sum()
				total_usage = total_load_shape.value.sum()
				new_load_shape = (total_load_shape*0.20).reset_index() 
				new_load_shape['meter_id'] = 'high_outlier'
				new_load_shape['population'] = self.population
				new_load_shape['index'] = None
				df = pd.concat([df, new_load_shape[['population', 'meter_id', 'hour', 'index', 'value']]])			

			df['hour'] = df['hour'] // (24/self.n_points)
			df = df.groupby(['population','meter_id','hour']).mean().reset_index()		
			return PrivateLoadShape(df, index_column='meter_id', time_column='hour', value_column='value', 
					quantile_cutoff_lower=0, quantile_cutoff_upper=1-self.quantile_cutoff)
		return self.cache_func(get, self.make_cache_key([self.population, self.high_outlier, self.n_points, self.quantile_cutoff]))

	def avg_usage_by_meter(self):
		if not self.ready():
			return ""

		df = self.load_shape().df 
		return df.groupby('meter_id').value.mean().reset_index()
		#return self.load_shape().mean_usage()


	def avg_usage(self):
		return self.avg_usage_by_meter().value.mean()

	def ready(self):
		try:
			self.db_client.query_df(f"select count(*) from population where population='{self.population}'")
			return True 
		except Exception as e:
			return False


	def find_epsilon(self, uncertainty):
		if not self.ready():
			return None    
		ls = self.load_shape()
		mean_usage = self.avg_usage_by_meter().value.mean()
		ci = mean_usage * uncertainty 
		epsilon = ls.epsilon_for_confidence_interval(ci)
		return epsilon 
		   
	
	def epsilon_uncertainty_mapping(self):
		if not self.ready():
			return None
		ls = self.load_shape()
		mean_usage = ls.mean_usage()        
		out = []
		for noise in np.linspace(0.01,1,100):
			ci = mean_usage * noise 
			epsilon = ls.epsilon_for_confidence_interval(ci)
			out.append(pd.Series({'noise_pct': noise, 'epsilon': epsilon}))

		return pd.DataFrame(out)

	def fifteen_fifteen(self):
		if not self.ready(): 
			return ""
		df = self.avg_usage_by_meter()
		if len(df) < 15:
			return False 
		total = df['value'].sum()
		max_value = df['value'].max()

		if (max_value / total) < 0.15:
			return "Yes"
		else: 
			return "No"


	def four_eighty(self):
		if not self.ready():
			return ""
		df = self.avg_usage_by_meter()
		if len(df) < 4:
			return False 
		total = df['value'].sum()
		max_value = df['value'].max()

		if (max_value / total) < 0.80:
			return "Yes"
		else:
			return "No"


	def graph_usage_histogram(self):
		
		try:
			if self.ready():
				df = self.avg_usage_by_meter()
				fig = px.histogram(df, x="value")
			else:
				fig = go.Figure()
		except Exception as e:
			print(e)
			fig = go.Figure()
		fig.update_layout(
			yaxis_title='value',
			title='Mean usage histogram',
			hovermode="x",
			showlegend=False,
			height=250,
			#width=320,
			margin=dict(t=50)
		)  
		return fig


	def n_meters(self):
		if not self.ready():
			return ""

		df = self.avg_usage_by_meter()
		return len(df)



	def graph_epsilon_noise(self):

		try:
			if self.ready():
				df = self.epsilon_uncertainty_mapping()
				df = df[df['noise_pct'] <= 0.50]
				df['noise_added (%)'] = df['noise_pct'] * 100
				df['privacy_factor'] = df['epsilon']
				fig = px.line(df, x='noise_added (%)', y='privacy_factor')
			else:
				fig = go.Figure()
		except Exception as e:
			print(e)
			fig = go.Figure()
		fig.update_layout(            
			title='Noise/privacy tradeoff',
			hovermode="x",
			showlegend=False,
			height=250,
			#width=320,
			margin=dict(t=50)
		)  
		return fig 
  
	def graph_load_shape(self, epsilon):
		try:
			if not self.ready():
				fig = go.Figure()
				fig.update_layout(
				title='Privatized average load shape',
				height=350,
			   # width=640,
				margin=dict(t=50)
				)    
				return fig

			if self.n_points == 1:
				mode = "lines+markers"
			else: 
				mode = "lines"

			ls = self.load_shape()
			#epsilon=5
			
			if epsilon is None:
				fig = go.Figure()
				fig.update_layout(
				title='Privatized average load shape',
				height=350,
				#width=640,
				margin=dict(t=50)
				)    
				return fig
				
			df = ls.privatize(epsilon)
			#import pdb; pdb.set_trace()
			fig = go.Figure([
			go.Scatter(
				name='Actual mean',
				x=df['hour'],
				y=df['actual_mean'],
				mode='lines+markers',
				line=dict(color='rgb(31, 119, 180)'),
			),
			go.Scatter(
				name='Upper Bound (95%)',
				x=df['hour'],
				y=df['private_max'],
				mode=mode,
				marker=dict(color="#444"),
				line=dict(width=0),
				showlegend=False
			),
			go.Scatter(
				name='Lower Bound (95%)',
				x=df['hour'],
				y=df['private_min'],
				marker=dict(color="#444"),
				line=dict(width=0),
				mode=mode,
				fillcolor='rgba(68, 68, 68, 0.3)',
				fill='tonexty',
				showlegend=False
			)
			])
			fig.update_layout(
				yaxis_title='value',
				title='Privatized average load shape',
				hovermode="x",
				showlegend=False,
				height=350,
			 #   width=640,
				margin=dict(t=50)
			)  
		except Exception as e:
			raise(e)
			print(e)    
			fig = go.Figure()
			fig.update_layout(
			title='Privatized average load shape',
			height=350,
		   # width=640,
			margin=dict(t=50)
			)    
			return fig

		return fig



# 	def privatize_and_aggregate(self):
# #		quantile_cutoffs = [0,0.1,0.2,0.3,0.4,0.5]
# 		#points = [1,2,4,8,12,18,24]
# 		for n_points in [2,8,12,18,24]:				
# 			df = self.get()
# 			df = self.resample_hours(df, n_points)
# 			for quantile_cutoff in [0,0.01, 0.02, 0.03, 0.04, 0.05]:
# 				for epsilon in np.logspace(start=-0.5, stop=2,num=100):
# 					ls = PrivateLoadShape(df, index_column='meter_id', time_column='hour', value_column='value', 
# 						quantile_cutoff_lower=0, quantile_cutoff_upper=1-quantile_cutoff)
# 					df_aggregated = ls.privatize(epsilon=epsilon)
# 					df_aggregated['population'] = self.label
# 					df_aggregated['epsilon'] = epsilon
# 					df_aggregated['quantile_cutoff'] = quantile_cutoff
# 					df_aggregated['n_points'] = n_points
# 					df_aggregated['span'] = (df_aggregated['private_max'] - df_aggregated['private_mean']) / df_aggregated['private_mean']
					
# 					self.db_client.load_df(df_aggregated, 'private_load_shapes', append=True)




def generate_populations(populations_json_path, db_client):
	db_client.drop_table('population')	
	settings = json.load(open(populations_json_path))
	for p in settings['populations']:	
		logger.info(f"Processing population: {p['label']}")		
		pop = Population(
			db_client = db_client,
			label = p['label'],
			rescale = p['rescale'],
			n_meters = p['n_meters'],
			scaling = p['scaling'],
			random_seed = ['random_seed']
			)
		pop.generate()	
		#pop.privatize_and_aggregate()
		logger.info(f"Finished processing population: {p['label']}")		
		