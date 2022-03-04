import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import dash_uploader as du 
import uuid 
from .nav import nav

societal_value_choices = [{
    'label': 'Low',
    'value': 0
    },
    {'label': 'Medium',
    'value': 1
    },
    {'label': 'High',
    'value': 2
    }]
data_risk_choices = societal_value_choices


def content_layout(logos):
    points_options = [{'label': p, 'value': p} for p in [1,2,4,8,12,24]]
    quantile_options = [{'label': f'Remove highest {p*100}%', 'value': p} for p in [0, 0.01, 0.02, 0.03, 0.04, 0.05]]

    fig_layout = go.Layout(
        width=256,
        height=256,
        margin=go.Margin(t=0, b=0, l=0, r=0)            
        )
    fig_layout_ls = go.Layout(
        width=512,
        height=256,
        margin=go.Margin(t=0, b=0, l=0, r=0)            
        )

    content = html.Div(
        [
        nav("/load-shape"),
        dcc.Store(id='data_store'),
            html.Div([

                html.H2("Population selection"),

                # population
                html.Div([

                        
                        html.Div([
                            html.Div([
                                html.Div("Population", className="padded"),                                             
                                dcc.Dropdown(
                                    id='population',                
                                    multi=False,
                                    options=[],    
                                    clearable=False,
                                    value=" (loading) ", className="padded")], id="prebuilt_population_container"),                            
                                                     
                            html.Div([                       
                                html.Div([
                                    html.Div("Number of meters: ", className="padded"),
                                    html.Div(id='n_meters', className="padded"),
                                ]),
                                html.Div([
                                    html.Div("Average usage: ", className="padded"),
                                    html.Div(id='avg_usage', className="padded"),
                                ])
                            ])                
                            ], style={'display': 'inline-block', 'width': '50%'}),

                        html.Div([                                                                                    
                            html.Div("No. of points to plot:"),
                            dcc.Dropdown(
                                id='points',                
                                multi=False,
                                options=points_options,    
                                clearable=False,
                                value=24, className="padded"),
                            html.Div([                
                                html.Div("Outlier cutoff", className="padded"),                    
                                dcc.Dropdown(
                                    id='quantiles',                
                                    multi=False,
                                    options=quantile_options,    
                                    clearable=False,
                                    value=quantile_options[0]['value'], className="padded")],id='quantiles_container'   ),
                            dcc.Checklist(options=[{'label': ' Add high outlier', 'value': 'Add high outlier'}],
                                    value=[], className='padded', inputClassName='padded', id='high_outlier')
                        ], style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'top'}),                                                                                                    
                        
                    ], style={'display': 'block', 'width': '100%'}), # population source
                

                html.H2("Diagnostics"),
                html.Div([
                    # population diagnostics
                    html.Div([

                        html.Div([                    
                            dcc.Graph(id="usage_histogram")
                        ], style={'width': '100%'}),
                        html.Div([
                            dcc.Graph(id="epsilon_noise")
                        ], style={'width': '100%'})
                    ], style={'display': 'block', 'width': '100%'}) # population diagnostics
                ], style={'display': 'block'}), # population select   
                
            ], className="four columns inputsContainer"),

            # privacy
            html.Div([

                html.Div([
                    html.H2("Differential privacy application"),
                    
                    html.Div([
                        html.Div("Noise to add", className="padded"),
                        #html.Div(id='uncertainty_div', style={"margin-bottom": "20px"}),
                        html.Div([
                        dcc.Slider(
                            id = 'uncertainty',
                            className = "slider_tight padded",
                            min=0,
                            max=0.5,
                            step=0.01,
                            value=0.4)]),      
                        html.Div(id='uncertainty_label', className="padded"),            
                    ], style={'width': '100%'}),

                    html.Div([            
                            dcc.Graph(id="load_shape")
                        ], style={'display': 'inline-block', 'width': '100%'})
                ]), # diff privacy application
            
                html.H2("Differential privacy diagnostics"),

                html.Div([
                    html.Div([
                        html.Div([
                                html.Div("Societal value of data", className="padded"),
                                html.Div([
                                dcc.Dropdown(
                                    id='data_societal',                
                                    multi=False,
                                    options=societal_value_choices,    
                                    clearable=False,
                                    value=0, className="padded")])      
                        ]),
                        html.Div([
                                html.Div("Data reidentification risk", className="padded"),
                                html.Div([
                                dcc.Dropdown(
                                    id='data_risk',                
                                    multi=False,
                                    options=data_risk_choices,    
                                    clearable=False,
                                    value=0, className="padded")])
                        ]),  
                    ], style={'display': 'inline-block', 'width': '30%', 'verticalAlign': 'top'}),
                    html.Div([
                        html.Div([
                                html.Div("Required privacy factor: ", style={"display": "inline-block"}, className="padded"),
                                html.Div(id='epsilon_label', style={"display": "inline-block"}, className="padded"),
                            ]),  

                        html.Div([
                                html.Div("Recommended privacy factor: ", style={"display": "inline-block"}, className="padded"),
                                html.Div(id='epsilon_recommended', style={"display": "inline-block"}, className="padded"),
                            ]),
                        html.Div([
                                html.Div("15/15 privacy eligible: ", style={"display": "inline-block"}, className="padded"),
                                html.Div(id='fifteen_fifteen', style={"display": "inline-block"}, className="padded"),
                            ])
                        #,
                        # html.Div([
                        #         html.Div("4/80 privacy eligible: ", style={"display": "inline-block"}, className="padded"),
                        #         html.Div(id='four_eighty', style={"display": "inline-block"}, className="padded"),
                        #     ])                
                    ], style={'display': 'inline-block', 'width': '70%'})


                ], style={'width': '100%', 'pading': '10px'}),
                dcc.Interval(id='trigger', interval=30000)
            ], className="six columns inputsContainer")
        # html.Div([
        #     html.Img(src=logos[0], width=200),
        #     html.Img(src=logos[1], width=200),
        #     html.Img(src=logos[2], width=200),
        #     html.Img(src=logos[3], width=200)

        # ], style={'display': 'inline-block'}),

        
       
        

        # html.Div([
        #     html.Div(id='graph_div', style={'width': '416rem', "margin-bottom": "20px"}),    
        #     dcc.Graph(id="load_shape", figure={'layout': {'width':'416rem', 'height':'16rem'}})
        # ])


        # html.Hr(), 
        # html.H3("SEAT/EDP Project", style={'textAlign': 'center'}),
        # html.Img(src=logos[0], width=200),
        # html.Img(src=logos[1], width=200),
        # html.Img(src=logos[2], width=200),
        # html.Img(src=logos[3], width=200)
    
    ]) 

    return content
