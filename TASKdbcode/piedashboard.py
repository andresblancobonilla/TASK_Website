#!/usr/bin/env python

#-----------------------------------------------------------------------
# piedashboard.py
# Author: Andres Blanco Bonilla
# Dash app for pie chart display
# route: /pieapp
#-----------------------------------------------------------------------

"""Instantiate a Dash app."""
import dash
import pandas
from TASKdbcode import demographic_db
from TASKdbcode import database_constants
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
from TASKdbcode import graphdashboard_helpers as helpers


def init_piedashboard(server):
    pie_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/pieapp/",
        # using default bootstrap style sheet, could be changed
        external_stylesheets=[dbc.themes.BOOTSTRAP])

    pie_app.layout = html.Div(
        children=[
            html.Div(children=[
                html.H4(
                    "Select Meal Sites (Clear Selections to Select All Sites)"),
                html.H5("Data from selected sites will be aggregated together into a single pie chart"),
                dcc.Dropdown(id='site_options',
                             options=[{'value': o, 'label': o}
                                 for o in database_constants.MEAL_SITE_OPTIONS],
                             clearable=True,
                             multi=True,
                             value=["First Baptist Church"]
                             ),
                html.H4("Select a Demographic Category"),
                dcc.Dropdown(id='demographic',
                             options= [{"label": option.replace("_", " ").title(), "value": option}
                                       for option in database_constants.DEMOGRAPHIC_OPTIONS],
                             clearable=True,
                             value='gender'
                             )         
                , html.H4("Select Filters"),
                # the options for race look weird bc they're long
                dbc.Row(id="filter_options", children=[]),

            ], className='menu-l'
            ),
            dcc.Graph(id='pie_chart',
                      config={'displayModeBar': True,
                          'displaylogo': False},
                      className='card',
                      style={'width': '100vw', 'height': '100vh'}
                      )
        ]
    )

    init_callbacks(pie_app)
    pie_app.enable_dev_tools(
    dev_tools_ui=True,
    dev_tools_serve_dev_bundles=True,)

    return pie_app.server


def init_callbacks(pie_app):

    @pie_app.callback(
            Output('filter_options', 'children'),
            Input('demographic', 'value'),
            State({'type': 'graph_filter', 'name': dash.ALL}, 'value')
    )
    def update_filter_options(selected_demographic, selected_filters):
        selected_fields = helpers.selected_fields_helper(dash.callback_context.states)
        filter_dict = dict(zip(selected_fields, selected_filters))
        filters = helpers.filter_options_helper(selected_demographic, filter_dict)
        return filters

    @pie_app.callback(
            Output('pie_chart', 'figure'),
            [Input('site_options', 'value'),
            Input('demographic', 'value'),
            Input({'type': 'graph_filter', 'name': dash.ALL}, 'value')]
    )
    def update_pie_chart(selected_sites, selected_demographic, selected_filters):
        
        selected_fields = helpers.selected_fields_helper(dash.callback_context.inputs)
        filter_dict = dict(zip(selected_fields, selected_filters))
        selected_fields.append("entry_timestamp")
        
        # The control flow of these if/else statements is logical,
        # but a little complicated
        # Maybe there is a cleaner way of arranging these chunks?

        # overall, would be great if the title of the charts were clearer
        # kinda hard to understand what exactly you're looking at atm lol
        
        # to do for pie charts:
        # include the demographic on the slice (like "Female" on the Female slice)
        # include the percentage of each slice on the key (like Black: 15%)
        # change colors to be readable in black and white and less ugly
        
        # fix scrolling and iframe, there's like 4 overlapping scrollbars
        # and it looks hideous lol, may need to mess with the iframe
        # size and page layout
        # ideally, the chart section doesn't have its own scrollbar
        # and it just scrolls with the rest of the page
        
        # There is also an issue where the chart completely disappears
        # if no diner fits all those filters,
        # there should be something less ugly than just a blank space
        
        if selected_demographic:
            selected_fields.append(selected_demographic)

            if selected_sites:
                filter_dict["meal_site"] = selected_sites
                print(filter_dict)
                selected_sites_df = demographic_db.get_patrons(
                        filter_dict=filter_dict, select_fields=selected_fields)
                pie_chart=go.Figure(data=[go.Pie(labels=selected_sites_df[selected_demographic].value_counts().index.tolist(),
                                                 values=list(selected_sites_df[selected_demographic].value_counts()))])
                pie_chart.update_layout(title=
                f"Distribution of {selected_demographic.title()} of Diners at Selected Sites")
                return pie_chart

            else:
                all_site_df = demographic_db.get_patrons(filter_dict = filter_dict, select_fields=selected_fields)
                all_pie_chart=go.Figure(data=[go.Pie(labels=all_site_df[selected_demographic].value_counts().index.tolist(),
                                                 values=list(all_site_df[selected_demographic].value_counts()))])
                all_pie_chart.update_layout(title=
                f"Distribution of {selected_demographic.title()} of Diners at All Sites")
                return all_pie_chart

        else:

            if selected_sites:
                selected_sites_data = demographic_db.get_patrons(filter_dict=filter_dict, select_fields=selected_fields)["entry_timestamp"].count()
                # I know every site has 50 entries bc I put 50 in there
                # maybe add table with num entries of each site?
                num_entries = len(selected_sites) * 50
                num_entries = num_entries - selected_sites_data
                selected_sites_data = pandas.Series([selected_sites_data],["Diners with Selected Filters"])
                other_count = pandas.Series([num_entries], ["Other"])
                selected_sites_data = pandas.concat([selected_sites_data, other_count])
                # creates an exploded pie chart, with the relevant slice pulled out by the pull factor specified
                # right now the pull looks weird if 0% of the diners meet the filters, somebody should make it look better
                exp_pie_chart = go.Figure(data = [go.Pie(values = selected_sites_data.values, labels = selected_sites_data.index, pull = [0.2,0],
                                                         title = "Percentage of Diners with Selected Filters at Selected Meal Site")])
                return exp_pie_chart

            else:
                all_site_data = demographic_db.get_patrons(
                                filter_dict=filter_dict, select_fields=selected_fields)["entry_timestamp"].count()
                num_entries = len(database_constants.MEAL_SITE_OPTIONS) * 50
                num_entries = num_entries - all_site_data
                all_site_data = pandas.Series([all_site_data],["Diners with Selected Filters"])
                other_count = pandas.Series([num_entries], ["Other"])
                all_site_data = pandas.concat([all_site_data, other_count])
                all_exp_pie_chart = go.Figure(data = [go.Pie(values = all_site_data.values, labels = all_site_data.index, pull = [0.2,0],
                                          title = "Percentage of Diners with Selected Filters Across All Meal Sites")])
                return all_exp_pie_chart
                
                
        