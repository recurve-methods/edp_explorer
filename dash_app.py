

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import flask 

#from views.sidebar import build_sidebar
from views.content import content_layout
#from views.file_load_modal import file_load_modal
from views.about import about_layout

from pathlib import Path
from dash.dependencies import Input, Output, State
from cache import Cacheable
from population import PlottingPopulation
from database import load_data

import plotly.express as px
import pandas as pd 
import plotly.graph_objs as go
import os

import numpy as np

#from rq import Queue
#from worker import conn

external_stylesheets = [dbc.themes.BOOTSTRAP, "https://codepen.io/chriddyp/pen/bWLwgP.css"]
container_layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)



class App(Cacheable):


    def serve_layout(self):
        if flask.has_request_context():
            return container_layout
        return html.Div(
            [container_layout, content_layout(self.logos()), about_layout(self.logos())]
        )


    def __init__(self, db_client, port=None):
        
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        self.db_client = db_client
        self.data_loaded = False
    #    self.queue = Queue(connection=conn)                
        self.app.layout = self.serve_layout
        super().__init__()
        self.clear_cache()
        self.react()


    # def to_worker(self, func, *args, **kwargs):
    #     job = self.queue.enqueue(func, job_timeout=10000, *args, **kwargs)
    #     return job

    def logos(self):
        return [self.app.get_asset_url('doe.png'), self.app.get_asset_url('nrel.png'), 
         self.app.get_asset_url('lbnl.png'), self.app.get_asset_url('recurve.png')]

    def n_points_choices(self):    
        return [1,2,4,8,12,24]

    def population_choices(self):
        try:
            return self.db_client.query_df('select distinct population from population')['population'].values            
        except Exception as e:
            return [" (loading) "]


    def quantile_cutoff_choices(self):
        return [0,0.01,0.02,0.03,0.04,0.05]


    def uncertainty_bounds(self):
        return 0, 0.5
   

    def recommended_epsilon(self, societal_value, data_risk):
        if societal_value==2:
            if data_risk==0:
                return "7"
            if data_risk==1:
                return "6"
            if data_risk==2:
                return "5"
        if societal_value==1:
            if data_risk==0:
                return "5"
            if data_risk==1:
                return "4"
            if data_risk==2:
                return "3"
        if societal_value==0:
            if data_risk==0:
                return "3"
            if data_risk==1:
                return "2"
            if data_risk==2:
                return "1"


    def react(self):


        @self.app.callback(
            Output('fifteen_fifteen', 'children'),
            [
                Input('population', "value"),    
                Input('high_outlier', 'value'),    
                Input('quantiles', "value"), 
            ]
            )
        def update_fifteen_fifteen(population, high_outlier, quantile_cutoff):
            pop = PlottingPopulation(self.db_client, population=population, high_outlier=high_outlier, n_points=24, quantile_cutoff=quantile_cutoff)
            return pop.fifteen_fifteen()
           

        # @self.app.callback(
        #     Output('four_eighty', 'children'),
        #     [
        #         Input('population', "value"), 
        #         Input('high_outlier', 'value'),       
        #         Input('quantiles', "value"), 
        #     ]
        #     )
        # def update_four_eighty(population, high_outlier, quantile_cutoff):
        #     pop = PlottingPopulation(self.db_client, population=population, high_outlier=high_outlier, n_points=24, quantile_cutoff=quantile_cutoff)
        #     return pop.four_eighty()
           
        
        @self.app.callback(
            Output('avg_usage', 'children'),
            [
                Input('population', "value"), 
                Input('high_outlier', 'value'),       
                Input('quantiles', "value"), 
            ]
            )
        def avg_usage(population, high_outlier, quantile_cutoff):
            pop = PlottingPopulation(self.db_client, population=population, high_outlier=high_outlier, n_points=24, quantile_cutoff=quantile_cutoff)
            return f"{pop.avg_usage():.1f}"

        @self.app.callback(
            Output('population', 'options'),
            Output('population', 'value'),
            [
            Input('trigger', 'n_intervals')]
            )
        def poll(n_intervals):    
            choices = self.population_choices()
            choices = [{'label': p, 'value': p} for p in choices]
            if len(choices) == 0:
                return choices, dash.no_update       
            return choices, choices[0]['value']
    
        @self.app.callback(
            Output("quantiles_container", component_property="style"),
            Output("quantiles", "value"),
            [
                Input("high_outlier", "value")
            ])
        def toggle_quantiles(high_outlier):
            if high_outlier:
                return {'display': 'none'}, 0
            else:
                return {'display': 'block'}, dash.no_update

  

        @self.app.callback(
            Output("page-content", "children"),
            [Input("url", "pathname")],
        )
        def display_page(pathname):
            if pathname == "/load-shape":
                return content_layout(self.logos())
            elif pathname == "/about":
                return about_layout(self.logos())
            elif pathname == '/':
                return content_layout(self.logos())
            else:
                return "404"

       

        @self.app.callback(
            Output('usage_histogram', "figure"),    
            Output('n_meters', 'children'),
            [
                Input('population', "value"), 
                Input('high_outlier', 'value'),       
                Input('quantiles', "value"), 
            ])
        def update_usage_histogram(population, high_outlier, quantile_cutoff):
            pop = PlottingPopulation(self.db_client, population=population, high_outlier=high_outlier, n_points=24, quantile_cutoff=quantile_cutoff)
            n_meters = pop.n_meters()
            return pop.graph_usage_histogram(), n_meters

        @self.app.callback(
            Output('epsilon_noise', 'figure'),
            [
                Input('population', "value"),
                Input('high_outlier', 'value'),        
                Input('points', "value"), 
                Input('quantiles', "value"), 
        
            ])
        def update_epsilon_noise_graph(population, high_outlier, n_points, quantile_cutoff):
            pop = PlottingPopulation(self.db_client, population=population, high_outlier=high_outlier, n_points=n_points, quantile_cutoff=quantile_cutoff)
            return pop.graph_epsilon_noise()
            

        @self.app.callback(
            Output('epsilon_label', "children"),    
            Output('load_shape', "figure"),    
            Output('uncertainty_label', "children"),

            [
                Input('uncertainty', "value"),        
                Input('population', "value"),   
                Input('high_outlier', 'value'),     
                Input('points', "value"), 
                Input('quantiles', "value"), 
            ])
        def update_uncertainty_value(uncertainty, population, high_outlier, n_points, quantile_cutoff):            
            pop = PlottingPopulation(self.db_client, population=population, high_outlier=high_outlier, n_points=n_points, quantile_cutoff=quantile_cutoff)
            epsilon = pop.find_epsilon(uncertainty)
            load_shape_graph = pop.graph_load_shape(epsilon)
            uncertainty_label = f"Noise: +- {round(100*uncertainty)} %;  privacy factor: {epsilon:.1f}"
            return f"{epsilon:.1f} (min)", load_shape_graph, uncertainty_label
          

        @self.app.callback(
            Output('epsilon_recommended', "children"),    
            [
                Input('data_societal', "value"),        
                Input('data_risk', "value"),        
            ])
        def update_recommended_epsilon(societal_value, data_risk):
            return self.recommended_epsilon(societal_value, data_risk) + " (max)"



