import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from .nav import nav


about_layout = html.Div("About this page")


def about_layout(logos):

	return html.Div(
        [
        nav("/about"),

        html.Div([
	        html.Div([
	        	html.A(href="https://edp.recurve.com/", children=[html.Img(src=logos[3], width=200)]),
	        	html.A(href="https://www.nrel.gov", children=[html.Img(src=logos[1], width=200)]),
	        	html.A(href="https://www.lbl.gov", children=[html.Img(src=logos[2], width=200)]),
	        	html.A(href="https://www.energy.gov", children=[html.Img(src=logos[0], width=200)])
	        	], style={'display': 'inline-block', 'width': '200px', 'padding-right': '50px'}),
	    html.Div(style={'display': 'inline-block', 'width': '50px'}),

	        html.Div([
				html.H2("About this application"),
				html.P([
					"The Energy Differential Privacy Explorer was developed in 2021 by Recurve, Inc. in partnership with the National Renewable Energy Laboratory and Berkeley Lab, as part of the ",
					html.A("Energy Data Vault", href="https://www.energy.gov/eere/buildings/energy-data-vault"), 
					" project funded by the US Department of Energy. The purpose of the ",
					"application is to allow an interactive exploration of differential ",
					"privacy applied to energy data in order to help stakeholders ",
					"gain an intuitive sense of how differential privacy could be ",
					"used in practice."]),
				html.H3("About differential privacy"),
				html.P(["Differential privacy is a mathematical transformation technique which allows for ",
						"the public release of aggregated private data with strong, mathematically rigorous ",
						"prviacy guarantees.  More information is available on the ",
						html.A("Recurve product pages.", href="https://edp.recurve.com")]),
				html.P(["This application uses Recurve's open-source ",
					html.A("eeprivacy Python library", href="https://github.com/recurve-inc/eeprivacy"),
					" to compute privatized load shapes using synthetic data provided by ",
					html.A("LBL.", href="https://lbnl-eta.github.io/AlphaBuilding-SyntheticDataset")
					]),						
				html.H3("Usage"),
				html.P(["First, select a population of meters to work with. ",
					"You may use one of the pre-computed populations, or upload a file ",
					"with your own data.  This population will be aggregated to make ",
					"an overall average privatized load shape. ",
					"Pre-computed populations are derived from the LBL synethic load shape ",
					"database and have been randomly shifted and scaled to approximate the ",
					"distribution of a real dataset of buildings."]),
				html.P(["Next, select the number of points you wish to plot, ", 
					"select whether to filter any outliers, and select the amount of ",
					"noise you would like to add to your load shape."
					]),
				html.P(["A privatized load shape will be displayed. ", 
					"The application will compute the privacy factor ",
					"(also known as 'epsilon') that is supportable for your ",
					"chosen population.  Generally, aim for a privacy factor ",
					"less than ten."]),
				html.P(["If the privacy factor is too high, you have the option of ",
					"plotting fewer data points, plotting with more noise, ", 
					"more tightly constraining outliers, or using a larger ",
					"population of meters."]),				
				html.H3("Contact"),
				html.Div([
					"Please contact the Recurve product team using ",
					html.A("this contact form.", href="https://edp.recurve.com/contact.html")
					])
	        	], style={'display': 'inline-block', 'width': '800px', 'verticalAlign': 'top'})
        ])
       ])
