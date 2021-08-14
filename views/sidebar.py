import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "64rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

def build_sidebar(population_choices, uncertainty_bounds, uncertainty_value, epsilon_label, points_choices=[1,24], quantile_choices=[0.0,0.05, 0.1]):
    #import pdb; pdb.set_trace()
   # epsilon_marks = {e: "{:.2f}".format(e) for e in epsilon_choices}
    uncertainty_label = str(uncertainty_value)
    population_options = [{'label': p, 'value': p} for p in population_choices]
    points_options = [{'label': p, 'value': p} for p in points_choices]
    quantile_options = [{'label': f'Top and bottom {p*100}%', 'value': p} for p in quantile_choices]

    return html.Div(
    [

        html.Div([
            html.Div("Population:",style={'width': '4rem', 'display': 'inline-block', 'text-align': 'right'}),
            html.Div([
            dcc.Dropdown(
                id='population',                
                multi=False,
                options=population_options,    
                clearable=False,
                value=population_choices[0])],
                style={'width': '16rem', 'display': 'inline-block'})
        ]),

        html.Div([
            html.Div("Quantile cutoff:",style={'width': '4rem', 'display': 'inline-block', 'text-align': 'right'}),
            #html.Div(id='uncertainty_div', style={"margin-bottom": "20px"}),
            html.Div([
            dcc.Dropdown(
                id='quantiles',                
                multi=False,
                options=quantile_options,    
                clearable=False,
                value=quantile_choices[0])],
                style={'width': '16rem', 'padding': '-25px', 'display': 'inline-block'})      
        ]),

        html.Div([
            html.Div("No. of points to plot:",style={'width': '4rem', 'display': 'inline-block', 'text-align': 'right'}),
            #html.Div(id='uncertainty_div', style={"margin-bottom": "20px"}),
            html.Div([
            dcc.Dropdown(
                id='points',                
                multi=False,
                options=points_options,    
                clearable=False,
                value=24)],
                style={'width': '16rem', 'padding': '-25px', 'display': 'inline-block'})      
        ]),


        html.Div([
            html.Div([dcc.Graph(id="usage_histogram", figure={'layout': {'width':'324', 'height':'256'}})], style={'width': '16rem', "display":"inline-block"}),                
            html.Div([dcc.Graph(id="epsilon_noise", figure={'layout': {'width':'324', 'height':'256'}})], style={'width': '16rem', "display":"inline-block"})
            ]),
        html.Hr(),

        html.Div([
            html.Div("Noise to add:",style={'width': '4rem', 'display': 'inline-block', 'text-align': 'right'}),
            #html.Div(id='uncertainty_div', style={"margin-bottom": "20px"}),
            html.Div([
            dcc.Slider(
                id = 'uncertainty',
                className = "slider_tight",
                min=uncertainty_bounds[0],
                max=uncertainty_bounds[1],
                step=0.01,
                value=uncertainty_value)],
                style={'width': '16rem', 'padding': '-25px', 'display': 'inline-block'}),      
            html.Div(id='uncertainty_label',style={'width': '16rem', 'display': 'inline-block'}),

        ]),
        html.Div([
            html.Div("Required privacy factor: ",style={'width': '16rem', 'display': 'inline-block', 'text-align': 'right'}),
            html.Div(id='epsilon_label',style={'width': '16rem', 'display': 'inline-block'}),
            ]),        

        html.Div([
            html.Div(id='graph_div', style={'width': '48rem', "margin-bottom": "20px"}),    
            dcc.Graph(id="load_shape", figure={'layout': {'width':'48rem', 'height':'16rem'}})
        ])


        # html.Hr(), 
        # html.H3("SEAT/EDP Project", style={'textAlign': 'center'}),
        # html.Img(src=logos[0], width=200),
        # html.Img(src=logos[1], width=200),
        # html.Img(src=logos[2], width=200),
        # html.Img(src=logos[3], width=200)
    
    ],
    style=SIDEBAR_STYLE,
)
