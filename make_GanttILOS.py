# Import packages
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objs as go
import warnings
warnings.filterwarnings("ignore")
# Set display options to show all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)

# Read data from the new CSV file with specified encoding
df = pd.read_csv("formatted_data_ILOS.csv", encoding='utf-8-sig', parse_dates=["Start", "Finish"])
df['Department'] = df['Viðskiptavinur']
df['Location'] = df['Legal']
df['Type'] = df['Tegund verkefnis']
df['PM'] = df['Ábyrgð']
df = df.rename(columns={'Stage': 'Phase'})
print(df.head())
try:
    # Strip leading and trailing spaces from string columns only
    string_columns = df.select_dtypes(include=['object']).columns
    df[string_columns] = df[string_columns].apply(lambda x: x.str.strip())
    
    # Replace 'NaN', 'nan', or any other variant with 'Unknown'
    df.replace({'NaN': 'Unknown PM', 'nan': 'Unknown PM', '': 'Unknown PM'}, inplace=True)
    # Replace NaN values with 'Unknown' in the entire DataFrame
    df.fillna('Unknown PM', inplace=True)
    # Convert 'Start' and 'Finish' to datetime if not already parsed
    df['Start'] = pd.to_datetime(df['Start'])
    df['Finish'] = pd.to_datetime(df['Finish'])
    df['Last Updated Date'] = pd.to_datetime(df['Last Updated Date'])

    # Sort the DataFrame based on 'Start'
    df = df.sort_values(by="Start", ascending=False)

    # Aggregate start and finish times for each task and merge
    project_timeframes = df.groupby('Task').agg({'Start': 'min', 'Finish': 'max'})
    df = df.merge(project_timeframes, on='Task', suffixes=('', '_Project'))

except Exception as e:
    print(f"An error occurred: {e}")
    df = pd.DataFrame()  # Create an empty DataFrame if there's an error

#print(f"after reading in data: {df.head()}")  # Debugging statement

# Update the last updated date in the app layout
last_updated_date_str = df['Last Updated Date'].max().strftime("%Y-%m-%d") if not df.empty else "N/A"

# Initialize the app
app = Dash(__name__)
server = app.server
app.title = 'FUPP'

# Define custom color maps
phase_colors = {
    'Data Preparation': '#5c9977',
    'Submission Deadline': '#faca78',
    'Bid Review': '#a163a2',
    'Finalization/Contract Creation': '#BB8B3F',
    'Improvement Projects': '#DB2A12',
    'Other': '#004DF4',
    'Legal': '#e0dd1b'
}


pm_colors = {
    'Ingvar Baldursson': '#1a2c79',  # Light Salmon
    'Benedikt Magnússon': '#e6a26e',     # Pale Green
    'Daníel Hólmgrímsson': '#7eed94',    # Light Blue
    'Mike McGarvey': '#a163a2',  # Light Green
    'Guttormur Guttormsson': '#64a6ea',     # Light Pink
    'Sigurður Jens': '#f28322',  # Plum
    'Gísli Guðmundsson': '#f2e291',     # Pale Turquoise
    'Brynjar Vatnsdal': '#FFFF99',     # Light Yellow
    'Jóhannes B': '#d94b2b',    # Peach Puff
    'Hartmann Rúnarsson': '#15aebf',     # Powder Blue
    'Siggi Kristó': '#4988bf',   # Pink
    'Bjarni Jakob': '#f5d698',   # 
    'Unknown PM': '#cfcfcf'   # 
}

# Get current date
current_date_str = datetime.now().strftime("%Y-%m-%d")
type_options = [{'label': t, 'value': t} for t in df['Type'].unique()]
#Styles:
filter_container_style = {
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'flex-start',  # Align items to the top
    'paddingRight': '10px',
    #'minWidth': '110px',
    #'maxWidth': '120px'
}
filter_sort_container_style = {
    'display': 'flex',
    'flexWrap': 'wrap',
    'alignItems': 'flex-start',
    'justifyContent': 'space-between',
    'marginBottom': '20px',
    'padding': '0 20px',
    'zIndex': '5'  # Ensure this is lower than the dropdown z-index
}
dropdown_container_style = {
    'position': 'absolute',  # Position it absolutely to place it on top of other elements
    'right': '1%',  # Adjust this value as needed to position from the right
    'top': '170px',  # Adjust top as needed to clear the header
    'zIndex': '10',  # Higher z-index to stack above the graph
    'display': 'flex',  # Using flex to align side by side
    'flexDirection': 'row',  # Align the dropdowns in a row
    'alignItems': 'flex-start',  # Align items at the start of the container
    'gap': '10px',  # Spacing between each dropdown
    'paddingTight': '10px',
}
dropdown_details_style = {
    'display': 'inline-block',  # Using inline-block for side by side layout
    'width': '150px',  # Define a width that accommodates the content
    'verticalAlign': 'top',  # To align at the top if they have different heights
    'border': '1px solid #d3d3d3',
    'borderRadius': '4px',
    'padding': '5px',
    'background-color': '#f8f9fa',
    'overflow': 'visible',  # Allow the dropdown content to overflow
}
left_dropdown_container_style = {
    'position': 'absolute',  # Position it absolutely to place it on top of other elements
    'left': '1%',  # Adjust this value as needed to position from the left
    'top': '150px',  # Adjust top as needed to clear the header
    'zIndex': '5',  # Higher z-index to stack above the graph
    'display': 'flex',  # Using flex to align side by side
    'flexDirection': 'row',  # Align the dropdowns in a row
    'alignItems': 'flex-start',  # Align items at the start of the container
    'gap': '10px',  # Spacing between each dropdown
}
right_dropdown_container_style = {
    'position': 'absolute',  # Position it absolutely to place it on top of other elements
    'right': '1%',  # Adjust this value as needed to position from the right
    'top': '170px',  # Adjust top as needed to clear the header
    'zIndex': '10',  # Higher z-index to stack above the graph
    'display': 'flex',  # Using flex to align side by side
    'flexDirection': 'row',  # Align the dropdowns in a row
    'alignItems': 'flex-start',  # Align items at the start of the container
    'gap': '10px',  # Spacing between each dropdown
}

# Sort the project list alphabetically
project_options = [{'label': project, 'value': project} for project in sorted(df['Task'].unique())]

# Options for stages
stage_options = [
    {'label': 'Undirbuningur gagna', 'value': 'Undirbuningur gagna'},
    {'label': 'Skilafrestur', 'value': 'Skilafrestur'},
    {'label': 'Yfirferð tilboða', 'value': 'Yfirferð tilboða'},
    {'label': 'Frágangur/gerð samnings', 'value': 'Frágangur/gerð samnings'},
    {'label': 'Umbótarverkefni', 'value': 'Umbótarverkefni'},
    {'label': 'Annað', 'value': 'Annað'},
    {'label': 'Legal', 'value': 'Legal'}
]

# Combine all PM related columns into a single Series and remove 'Unknown'
#all_pm_names = pd.Series(pd.concat([df['PM'], df['PML'], df['DM'], df['PM1'], df['PM2']], ignore_index=True))
#all_pm_names = all_pm_names[all_pm_names != 'Unknown'].unique()

# Sort and create dropdown options
pm_options = [{'label': pm, 'value': pm} for pm in sorted(df['PM'].unique()) if pd.notna(pm)]
type_options = [{'label': type_, 'value': type_} for type_ in sorted(df['Type'].unique()) if pd.notna(type_)]
location_options = [{'label': location, 'value': location} for location in sorted(df['Location'].unique()) if pd.notna(location)]
department_options = [{'label': department, 'value': department} for department in sorted(df['Department'].unique()) if pd.notna(department)]
print(f'pm_options: {pm_options}')
print(f'type_options: {type_options}')
print(f'location_options: {location_options}')
print(f'department_options: {department_options}')
# Header layout with title, button, and logos
header_layout = html.Div([
    # Title and Timeline Slider button
    html.Div([
        html.Div([
            html.H1([
                html.Span('ILOS', style={"color": "#101010", "fontWeight": "bold"}),
                html.Span('Projects', style={"color": "#004DF4", "fontWeight": "bold"}),
            ], style={
                'fontSize': "48px",
                'display': 'inline-block',
                'verticalAlign': 'middle',
                'marginRight': '10px',
            }),
            html.Button('Timeline Slider', id='toggle-slider-button', n_clicks=0, style={
                'backgroundColor': '#004DF4',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'padding': '10px 20px',
                'fontSize': '16px',
                'display': 'inline-block',
                'verticalAlign': 'middle',
                'marginLeft': '10px',
            }),
        ], style={
            'display': 'inline-block',
            'verticalAlign': 'middle',
        }),
        
        # Logos
        html.Div([
            html.Img(src="/assets/isavia_logo.png", style={
                'height': '70px',  # Adjust the height to align with the text and button
                'marginRight': '10px',
                'filter': "grayscale(100%)",
                'display': 'inline-block',
                'verticalAlign': 'middle',
            }),
            html.Img(src="/assets/KEF-EN-svart.png", style={
                'height': '70px',  # Adjust the height to align with the text and button
                'filter': "grayscale(100%)",
                'display': 'inline-block',
                'verticalAlign': 'middle',
            }),
        ], style={
            'display': 'inline-block',
            'verticalAlign': 'middle',
            'float': 'right',  # Float right to align with the right edge
        }),
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'padding': '10px 20px',  # Add padding as needed
    }),
], style={
    'overflow': 'hidden',  # Ensure the floating elements are contained within the div
})

# Last Updated Date positioned at the bottom right of the header
last_updated_layout = html.Div([
    html.P("Last Updated: " + last_updated_date_str, style={
        'textAlign': 'right',
        'color': '#101010',
        'fontSize': '14px',
        'marginTop': '5px'
    })
], style={'position': 'absolute', 'top': '0px', 'right': '20px'})

# The dropdowns for Stages, PMs, and Projects with spacing between them
select_options_layout = html.Div(style={'paddingRight': '10px', 'display': 'inline-block', 'verticalAlign': 'top', 'position': 'absolute', 'right': '1%', 'top': '0', 'alignItems': 'flex-start'}, children=[
    html.Details([
        html.Summary('Stig:', style={'fontWeight': 'bold'}),
        dcc.Checklist(
            id='stage-checklist-items',
            options=[
                {'label': 'Undirbuningur gagna', 'value': 'Undirbuningur gagna'},
                {'label': 'Skilafrestur', 'value': 'Skilafrestur'},
                {'label': 'Yfirferð tilboða', 'value': 'Yfirferð tilboða'},
                {'label': 'Frágangur/gerð samnings', 'value': 'Frágangur/gerð samnings'},
                {'label': 'Umbótarverkefni', 'value': 'Umbótarverkefni'},
                {'label': 'Annað', 'value': 'Annað'},
                {'label': 'Legal', 'value': 'Legal'}
            ],
            value=['Undirbuningur gagna', 'Skilafrestur', 'Yfirferð tilboða', 'Frágangur/gerð samnings', 'Umbótarverkefni', 'Annað', 'Legal'],  # Default selected values
            style={"color": "black"}
        ),
    ], style=dict(dropdown_details_style, marginRight='10px', minWidth='190px')),  # Adjusted minWidth for consistency

    html.Details([
        html.Summary('Aðstoð frá lögfr.:', style={'fontWeight': 'bold'}),  # Updated to "Viðskiptavinur"
        dcc.Checklist(
            id='location-checklist-items',  # Updated ID
            options=[{'label': customer, 'value': customer} for customer in sorted(df['Location'].unique()) if pd.notna(customer)],
            value=sorted(df['Location'].unique()),
            style={"color": "black"}
        ),
    ], style=dict(dropdown_details_style, marginRight='10px', minWidth='190px')),  # Adjusted minWidth for consistency

    html.Details([
        html.Summary('Ábyrgð:', style={'fontWeight': 'bold'}),  # Updated to "Ábyrgð" for PM
        dcc.Checklist(
            id='pm-checklist-items',
            options=[{'label': pm, 'value': pm} for pm in sorted(df['PM'].unique()) if pd.notna(pm)],
            value=sorted(df['PM'].unique()),
            style={"color": "black"}
        ),
    ], style=dict(dropdown_details_style, minWidth='190px')),  # Consistent minWidth

    html.Details([
        html.Summary('Select Projects:', style={'fontWeight': 'bold'}),
        dcc.Checklist(
            id='filtered-project-list-checklist',
            options=[],  # Initially empty, will be populated dynamically
            value=[],
            style={"color": "black"}
        ),
    ], style=dict(dropdown_details_style, minWidth='190px')),  # Added marginRight for spacing
])


#isavia blue : #4396a7 orange:#e65500
# App layout
app.layout = html.Div(style={'backgroundColor': 'white', 'color': '#101010', 'fontFamily': 'Arial'}, children=[

    header_layout,
    last_updated_layout,
    
    # Filters and sorting options
    html.Div(style={'position': 'absolute', 'top': '130px', 'left': '1%', 'right': '1%', 'zIndex': '10'}, children=[
        # Left-aligned options container
        html.Div(style={'display': 'flex', 'flexWrap': 'nowrap', 'justifyContent': 'start', 'alignItems': 'flex-start', 'marginRight': '50%'}, children=[
            # Filter by PM/Phase
            html.Div(style={**filter_container_style, 'width':'80px','minWidth': '80px','maxWidth': '80px'}, children=[
                html.Label('Color by:', style={'paddingRight': '0px'}),
                dcc.RadioItems(
                    options=[
                        {'label': 'Stages', 'value': 'Phase'},
                        {'label': 'PM', 'value': 'PM'}
                    ],
                    value='Phase',
                    id='color-radio-items',
                    inline=True,
                    style={"color": "black"}
                ),
            ]),


            # Filter Data by Viðskiptavinur (previously Department)
            html.Div(style={**filter_container_style, 'minWidth': '150px','maxWidth': '150px'}, children=[
                html.Label('Viðskiptavinur:', style={'paddingRight': '0px'}),
                dcc.Checklist(
                    options=department_options,
                    value=sorted(df['Department'].unique()),  # Assuming you want all selected by default
                    id='department-checklist-items',  # Updated ID
                    style={"color": "black"}
                ),
            ]),

            # Filter Data by Type (Tegund verkefnis)
            html.Div(style={**filter_container_style, 'minWidth': '150px','maxWidth': '150px'}, children=[
                html.Label('Tegund Verkefnis:', style={'paddingRight': '0px'}),
                dcc.Checklist(
                    options=[{'label': type_, 'value': type_} for type_ in sorted(df['Type'].unique())],
                    value=sorted(df['Type'].unique()),  # Adjust default values as needed
                    id='type-checklist-items',
                    style={"color": "black"}
                ),
            ]),


            # Sorting dropdown
            html.Div(style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'flex-start',  # Align items to the top
                    'paddingRight': '10px',
                    'minWidth': '170px',
                    #'maxWidth': '120px'
                }, children=[
                html.Label('Flokka verkefni eftir:', style={'paddingRight': '10px'}),
                dcc.Dropdown(
                    id='sort-dropdown',
                    options=[
                        {'label': 'Project Start', 'value': 'Project_Start'},
                        {'label': 'Project Finish', 'value': 'Project_Finish'},
                        {'label': 'Ábyrgð', 'value': 'PM'},
                        {'label': 'Stafrófsröð', 'value': 'Task'},
                    ],
                    value='Project_Start',
                    clearable=False,
                    style={"width": "100%"}
                ),
            ]),
        ]),

        select_options_layout,

    ]),

    dcc.Store(id='graph-container-height-store'),

    # New Div for spacing
    html.Div(style={'height': '50pt','zIndex': '1'}),

    # Graph container with lower z-index
    dcc.Graph(id='gantt-chart-placeholder', style={
        #"height": "1500px",
        "backgroundColor": "#4396a7",
        'zIndex': '2'
    },
        config={
            'toImageButtonOptions': {
                'format': 'png',  # One of png, svg, jpeg, webp
                'filename': 'FUPP_Timeline_snapshot',
                #'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
            }
        }
    ),
])

# Refactored function for filtering DataFrame
# Refactored function for filtering DataFrame
def filter_dataframe(df, selected_departments, selected_location_categories, selected_types, selected_stages):
    #print("Initial Data Shape:", df.shape)  # Debugging: Print the initial shape of DataFrame


    # Apply Department filter
    if selected_departments:
        df = df[df['Department'].isin(selected_departments)]
        #print("After Department Filter Shape:", df.shape)  # Debugging: Print shape after Department filter

    # Apply Location filter
    if selected_location_categories:
        df = df[df['Location'].isin(selected_location_categories)]
        #print("After Location Filter Shape:", df.shape)  # Debugging: Print shape after Location filter

    # Apply Type filter
    if selected_types:
        df = df[df['Type'].isin(selected_types)]
        #print("After Type Filter Shape:", df.shape)  # Debugging: Print shape after Type filter


    
    # Apply Tier filter
    # Debug: Print unique values in 'Tier' column
    #print("Unique Tiers in DataFrame:", df['Tier'].unique())    
    # Convert selected tiers to integers

    # Apply Stage filter
    if selected_stages:
        df = df[df['Phase'].isin(selected_stages)]
        #print("After Stage Filter Shape:", df.shape)  # Debugging: Print shape after Stage filter

    #print("Final Data Shape:", df.shape)  # Debugging: Print the final shape of DataFrame
    return df





# Function to aggregate and merge data
def aggregate_and_merge_data(filtered_df):
    # Calculate the minimum start date and maximum finish date for each task
    project_start_finish = filtered_df.groupby('Task').agg(Project_Start=('Start', 'min'), 
                                                           Project_Finish=('Finish', 'max')).reset_index()

    # Merge the project_start_finish dataframe with the filtered_df
    filtered_df = filtered_df.merge(project_start_finish, on='Task')

    # Additional aggregation and merging for different stages
    # Stage 5 Start
    stage_5_start_df = filtered_df[filtered_df['Phase'] == 'Stage 5'].groupby('Task')['Start'].min().reset_index()
    stage_5_start_df = stage_5_start_df.rename(columns={'Start': 'Stage_5_Start'})
    filtered_df = filtered_df.merge(stage_5_start_df, on='Task', how='left')

    # Procurement Start
    procurement_start_df = filtered_df[filtered_df['Phase'] == 'Procurement'].groupby('Task')['Start'].min().reset_index()
    procurement_start_df = procurement_start_df.rename(columns={'Start': 'Procurement_Start'})
    filtered_df = filtered_df.merge(procurement_start_df, on='Task', how='left')

    # Stage 3 Start
    stage_3_start_df = filtered_df[filtered_df['Phase'] == 'Stage 3'].groupby('Task')['Start'].min().reset_index()
    stage_3_start_df = stage_3_start_df.rename(columns={'Start': 'Stage_3_Start'})
    filtered_df = filtered_df.merge(stage_3_start_df, on='Task', how='left')

    return filtered_df


# Function for sorting DataFrame
def sort_dataframe(filtered_df, sort_column):
    if sort_column == 'Task':
        sorted_df = filtered_df.sort_values(by=sort_column, ascending=False)
    else:
        sorted_df = filtered_df.sort_values(by=sort_column, ascending=False, na_position='first')
    return sorted_df.reset_index(drop=True)

def create_roles_info(df):
    # Define the roles we are interested in
    roles = ['PML', 'DM', 'PM1', 'PM2']
    
    # Initialize the 'RolesInfo' column with empty strings
    df['RolesInfo'] = ''
    
    for index, row in df.iterrows():
        roles_info_list = []
        for role in roles:
            # Check if the role column is not NaN and not 'Unknown'
            if pd.notna(row[role]) and row[role] != 'Unknown PM':
                # Append the role info to the list
                roles_info_list.append(f"{role}: {row[role]}")
        
        # Join all the role info strings with a space
        df.at[index, 'RolesInfo'] = ' '.join(roles_info_list)
    
    return df

# Apply the function to the DataFrame
#df = create_roles_info(df)

# Function to create Gantt Chart
def create_gantt_chart(sorted_df, color_column, task_order, pm_colors, phase_colors, graph_container_height):
    # Set the figure size or layout properties to adjust the width
    fig = go.Figure()
    fig.update_layout(
        # ... (your existing layout updates)
        width=900,  # Adjust width as necessary to fit the sidebar
        # ... (other layout properties)
    )
    relative_legend_item_height = 15 / graph_container_height

    # Check if the DataFrame is empty
    if sorted_df.empty:
        return None
    print(sorted_df)
    # Create the Plotly timeline
    if color_column == 'PM':
        fig = px.timeline(sorted_df, x_start="Start", x_end="Finish", y="Task",
                          color="PM", hover_name="Phase", opacity=0.7,
                          hover_data={ 'Task': False, 'Phase': True,'Department': True, 'PM': False, 'Location': True, 'Type': True,},
                          labels={"Task": "Projects", "Phase": "Project Phase", "PM": "Project Manager","Department":"Department"},
                          color_discrete_map=pm_colors,  # Use the PM color map
                          category_orders={"Task": task_order})  # Specify the order of tasks
        fig.update_layout(legend=dict(itemclick=False, itemdoubleclick=False))
    else:
        fig = px.timeline(sorted_df, x_start="Start", x_end="Finish", y="Task",
                          color="Phase", hover_name="PM", opacity=0.7,
                          hover_data={ 'Task': False, 'Phase': True,'Department': True, 'PM': False, 'Location': True, 'Type': True},
                          labels={"Task": "Projects", "Phase": "Project Phase", "PM": "Project Manager","Department":"Department"},
                          color_discrete_map=phase_colors,  # Use the Phase color map
                          category_orders={"Task": task_order})  # Specify the order of tasks
        fig.update_layout(showlegend=False)

        # Define starting positions for the custom legend
        legend_x_start = 1.02  # X position of legend start (right of the graph)
        legend_y_start = 1  # Y position of legend start (top of the graph)

        # Define aesthetics for the custom legend
        color_block_width = 0.03  # Width of the color block
        vertical_space_between_items = 15 / graph_container_height  # Space between legend items

        # Create the custom legend using the relative height
        for i, (label, color) in enumerate(reversed(list(phase_colors.items()))):
            current_y_position = legend_y_start - i * (relative_legend_item_height + vertical_space_between_items)
            fig.add_shape(
                type="rect",
                xref="paper", yref="paper",
                x0=legend_x_start, y0=current_y_position,
                x1=legend_x_start + color_block_width,
                y1=current_y_position - relative_legend_item_height,
                fillcolor=color,
                line=dict(color=color),
            )
            fig.add_annotation(
                xref="paper", yref="paper",
                x=legend_x_start + color_block_width + 0.01,
                y=current_y_position - (relative_legend_item_height / 2),
                text=label,
                showarrow=False,
                align="left",
                font=dict(size=12, color="black"),
                xanchor="left",
                yanchor="middle",
            )

        # Update the layout to accommodate the custom legend
        fig.update_layout(
            margin=dict(r=170),  # Adjust the right margin to fit the custom legend
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

    return fig


# Function to add a current date line to the figure
def add_current_date_line(fig):
    current_date = datetime.now().date()
    fig.add_shape(
        type="line",
        x0=current_date,
        x1=current_date,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="Black", width=2),
    )
    fig.add_annotation(
        x=current_date,
        y=1.025,
        yref="paper",
        showarrow=False,
        xanchor="right",
        text="Today",
        bgcolor="black",
        opacity=0.7,
        font=dict(color="white")
    )

# Function to toggle range slider visibility
def toggle_range_slider(fig, n_clicks):
    fig.update_layout(xaxis_rangeslider_visible=(n_clicks % 2 == 1))
    
@app.callback(
    Output('filtered-project-list-checklist', 'options'),
    [
        Input('department-checklist-items', 'value'),
        Input('location-checklist-items', 'value'),
        Input('type-checklist-items', 'value'),
        Input('stage-checklist-items', 'value'),
        Input('pm-checklist-items', 'value'),
    ]
)
def update_filtered_project_checklist(selected_departments, selected_locations, selected_types, selected_stages, selected_pms):
    print("Callback Triggered: update_filtered_project_checklist")  
    # Perform filtering
    filtered_df = filter_dataframe(df, selected_departments, selected_locations, selected_types, selected_stages)    
    # Further filter based on selected PMs
    if selected_pms:
        filtered_df = filtered_df[filtered_df['PM'].isin(selected_pms)]

    # If no data to display after filters, prevent the update
    if filtered_df.empty:
        raise PreventUpdate

    # Create project checklist options based on the filtered dataframe
    project_checklist_options = [{'label': project, 'value': project} for project in sorted(filtered_df['Task'].unique())]

    return project_checklist_options


@app.callback(
    Output('gantt-chart-placeholder', 'style'),
    [Input('filtered-project-list-checklist', 'options')]
)
def update_graph_container_height(selected_projects):
    # Set a minimum height
    min_height = 850

    # Calculate the height based on the number of projects (18px per project)
    height_per_project = 25
    dynamic_height = max(min_height, len(selected_projects) * height_per_project)

    # Return the updated style dictionary with the new height
    return {
        "height": f"{dynamic_height}px",
        "backgroundColor": "#4396a7",
        'zIndex': '2'
    }

@app.callback(
    Output('graph-container-height-store', 'data'),
    [Input('filtered-project-list-checklist', 'options')]
)
def get_graph_container_height(selected_projects):
    # Set a minimum height
    min_height = 850

    # Calculate the height based on the number of projects (18px per project)
    height_per_project = 25
    dynamic_height = max(min_height, len(selected_projects) * height_per_project)
    return {"height": dynamic_height}
# Callback to update the checklist value
@app.callback(
    Output('stage-checklist-items', 'value'),
    [Input('stage-checklist-items', 'value')],
    [State('stage-checklist-items', 'value')]
)
def ensure_strategies_and_plans(selected_stages, current_value):
    # Ensure 'Strategies and Plans' is always included in the value
    if 'Strategies and Plans' not in selected_stages:
        selected_stages.append('Strategies and Plans')
    return selected_stages

@app.callback(
    Output('pm-checklist-items', 'options'),
    [
        Input('department-checklist-items', 'value'), 
        Input('location-checklist-items', 'value'),
        Input('type-checklist-items', 'value'),
        Input('stage-checklist-items', 'value'),
        # No need to include the PM checklist itself as an input, to avoid circular updates
    ]
)
def update_filtered_project_checklist(selected_departments, selected_locations, selected_types, selected_stages):
    # Perform filtering based on the checklist values
    filtered_df = filter_dataframe(df, selected_departments, selected_locations, selected_types, selected_stages)

    pm_options = [{'label': pm, 'value': pm} for pm in sorted(df['PM'].unique()) if pd.notna(pm)]

    return pm_options

@app.callback(
    Output('gantt-chart-placeholder', 'figure'),
    [
        Input('color-radio-items', 'value'),
        Input('graph-container-height-store', 'data'),
        Input('department-checklist-items', 'value'), 
        Input('location-checklist-items', 'value'),
        Input('type-checklist-items', 'value'),
        Input('stage-checklist-items', 'value'),
        Input('pm-checklist-items', 'value'),
        Input('toggle-slider-button', 'n_clicks'),
        Input('sort-dropdown', 'value'),
        Input('filtered-project-list-checklist', 'value'),  # New input for the filtered project list
    ]
)
def update_graph(color_column, graph_container_height_data, selected_departments, selected_location_categories, selected_types, selected_stages, selected_pms, n_clicks, sort_column, filtered_projects):
    # Proceed with filtering if location categories are selected
    if not selected_location_categories:
        return go.Figure()

    # Filter the DataFrame based on the selected filters
    filtered_df = filter_dataframe(df, selected_departments, selected_location_categories, selected_types, selected_stages)
    #print(f"Filtered Data: {filtered_df.head()}")  # Debugging statement

    # Filter based on selected PMs
    if selected_pms:
        # Check if 'Unknown PM' is a selected option
        if 'Unknown PM' in selected_pms:
            # Create a filter that includes 'Unknown PM' as well as the selected PMs
            pm_filter = (filtered_df['PM'].isin(selected_pms))
        else:
            # If 'Unknown PM' is not selected, filter normally
            pm_filter = (filtered_df['PM'].isin(selected_pms))

        # Apply the filter to the DataFrame
        filtered_df = filtered_df[pm_filter]

    # Further filter the dataframe based on selected projects from the filtered checklist
    if filtered_projects:
        filtered_df = filtered_df[filtered_df['Task'].isin(filtered_projects)]

    # Aggregate and merge data
    filtered_df = aggregate_and_merge_data(filtered_df)
    #print(f"Aggregated and Merged Data: {filtered_df.head()}")  # Debugging statement

    # Sort the DataFrame
    sorted_df = sort_dataframe(filtered_df, sort_column)
    #print(f"Sorted Data for Chart: {sorted_df.head()}")  # Debugging statement

    # Determine the order of tasks
    task_order = sorted_df['Task'].unique().tolist()
    task_order.reverse()
    
    # Create the Gantt chart
    graph_container_height = graph_container_height_data['height'] if graph_container_height_data else 800  # default if data is None
    fig = create_gantt_chart(sorted_df, color_column, task_order, pm_colors, phase_colors, graph_container_height)

    # Add current date line and toggle range slider if the figure is not None
    if fig is not None:
        add_current_date_line(fig)
        toggle_range_slider(fig, n_clicks)
        #print("Gantt Chart Created")  # Debugging statement

    # If there's no data to display after filtering
    else:
        fig = go.Figure()
        fig.update_layout(title="No Data to Display")
        #print("Gantt Chart is None, no data to display")  # Debugging statement

    return fig


# This is just for demonstration, you can integrate it with your main app script.
if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=True, host='0.0.0.0')

