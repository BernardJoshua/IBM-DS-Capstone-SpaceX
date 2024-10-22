import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Data preparation
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df['Launch Site'].unique()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Task 1: Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}] + 
            [{'label': site, 'value': site} for site in launch_sites],
        value='ALL',  # Default value
        placeholder="Select a Launch Site",
        searchable=True
    ),
    
    html.Br(),
    
    # Task 2: Pie chart for launch success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # Task 3: Range slider for selecting payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=100,
        value=[min_payload, max_payload],
        marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 1000)}
    ),
    
    # Task 4: Scatter chart for payload vs. launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Task 2: Callback function for the success-pie-chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        # Aggregate data for all sites
        success_counts = filtered_df['class'].value_counts()
    else:
        # Filter for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts()
        
    # Prepare the data for the pie chart
    labels = ['Success', 'Failure']
    values = [success_counts.get(1, 0), success_counts.get(0, 0)]

    fig = px.pie(values=values, 
                 names=labels, 
                 title='Total Launch Successes' + (f' for {entered_site}' if entered_site != 'ALL' else ' (All Sites)'))

    return fig
# Task 4: Callback function for the success-payload-scatter-chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        title='Payload vs. Launch Success',
        labels={'class': 'Launch Success'},
        color='class',
        category_orders={'class': [0, 1]}  # 0 = Failure, 1 = Success
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
