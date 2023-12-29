import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import pandas as pd
import math

# Data
df = pd.read_csv("..\Data\df_dashboard.csv")
y_test = pd.read_csv("..\Data\y_test_dashboard.csv")
y_pred_lstm = pd.read_csv("..\Data\y_pred_dashboard.csv")
y_pred_lr = pd.read_csv("..\Data\predictions_dashboard.csv")
df_reviews = pd.read_csv("..\Data\df_reviews_dashboard.csv")

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")

# Title
st.title('Traffic dashboard in Ireland vs Europe')

# Main content area
main = st.container()

def create_row_1():

    # Filtering options
    categories = list(df['Category'].unique())
    years = list(df['Year'].unique())
    metrics = list(df.columns[2:])

    similar = st.checkbox('Show only countries similar to Ireland')

    col1, col2, col3 = st.columns(3)

    with col1:
        if similar:
            selected_categories = ['France', 'Ireland', 'Latvia', 'Malta', 'Norway', 'Poland',
       'Slovenia', 'Spain', 'United Kingdom']
        else: 
            selected_categories = st.multiselect('Select countries:', categories)

    with col2:
        selected_years = st.multiselect('Select years:', years)

    with col3:
        selected_metrics = st.multiselect('Select traffic metrics:', metrics)

    # Filter data based on user selections
    df_filtered = df.copy()

    if selected_categories and 'All Europe' not in selected_categories:
        df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories + ['Ireland'])]

    if selected_years and 'All years' not in selected_years:
        df_filtered = df_filtered[df_filtered['Year'].isin(selected_years)]

    if selected_metrics and 'All metrics' not in selected_metrics:
        df_filtered = df_filtered[['Category', 'Year'] + selected_metrics]

    # Show dataframe table
    st.markdown("**Table of traffic values for selected countries, years and metrics**")
    st.dataframe(df_filtered.loc[df_filtered["Category"]!="Ireland"], use_container_width=True, height=200)

    return df_filtered  # Return the filtered DataFrame


def create_row_2(df_filtered):

    # Melt the DataFrame to have a 'Country' column and a 'Traffic Metric' column
    melted_df = pd.melt(df_filtered, id_vars=['Category', 'Year'], 
                        value_vars=df_filtered.columns, 
                        var_name='Traffic Metric', value_name='Traffic Value')
    
    # Define a custom color palette based on 'Traffic Metric'
    custom_metric_colors = {
        'Passenger Car Traffic': '#0676B3',
        'Bus and Motor Coach Traffic': '#DE9007',
        'Total Van, Pickup, Lorry and Road Tractor Traffic': '#09A077',
    }
    
    # Map Visualization
    fig = px.scatter_geo(melted_df, 
                        locations="Category", 
                        locationmode="country names",
                        color="Traffic Metric",
                        size="Traffic Value",
                        animation_frame="Year",
                        projection="natural earth",
                        title="Map visualization of traffic values for selected countries, years and metrics",
                        size_max=50,
                        height=800,
                        color_discrete_map=custom_metric_colors)

    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)    

    with col1:
        # Plot the bar chart using seaborn
        plt.figure(figsize=(12, 8))

        # Get unique values in the 'Category' column
        unique_categories = melted_df['Category'].unique()

        # Create a color palette using seaborn's husl palette
        palette_def = sns.color_palette("tab20", n_colors=len(unique_categories))

        # Create a color palette with a different color for each unique category
        #palette = {category: 'red' if category == 'Ireland' else 'lightgray' for category in unique_categories}
        palette = {category: 'red' if category == 'Ireland' else color for category, color in zip(unique_categories, palette_def)}        

        ax = sns.barplot(x='Traffic Metric', y='Traffic Value', hue='Category', data=melted_df, palette=palette)

        plt.title('Traffic Metrics Comparison - Ireland vs Other Countries')
        plt.xlabel('Traffic Metric')
        plt.ylabel('Traffic Value')

        # row x col = unique_categories -> col = unique_categories/5

        # Move the legend outside the plot and display horizontally
        ax.legend(loc='upper right', ncol=int(math.ceil(len(unique_categories)/5)))

        # Display the Matplotlib figure in Streamlit
        st.pyplot(plt)

    with col2:
        # Filter the DataFrame to extract vehicle categories for Ireland
        passenger_df = df[df['Category'] == 'Ireland'][["Passenger Car Traffic", "Year"]]
        bus_df = df[df['Category'] == 'Ireland'][["Bus and Motor Coach Traffic", "Year"]]
        other_df = df[df['Category'] == 'Ireland'][["Total Van, Pickup, Lorry and Road Tractor Traffic", "Year"]]

        # Use a color palette that is colorblind-friendly
        palette = sns.color_palette("colorblind")

        # Create separate figures for better clarity
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot separate lines for passenger car, bus, and other traffic
        sns.lineplot(x='Year', y='Passenger Car Traffic', data=passenger_df, label="Passenger Car Traffic", color=palette[0], ax=ax)
        sns.lineplot(x='Year', y='Bus and Motor Coach Traffic', data=bus_df, label="Bus and Motor Coach Traffic", color=palette[1], ax=ax)
        sns.lineplot(x='Year', y='Total Van, Pickup, Lorry and Road Tractor Traffic', data=other_df, label="Total Van, Pickup, Lorry and Road Tractor Traffic", color=palette[2], ax=ax)

        # Highlight the selected year with a red line
        if filtered_df['Category'].isin(['Ireland']).any() and len(filtered_df["Year"].unique())!=6:
            selected_years = filtered_df["Year"].unique()
            for year in selected_years:
                ax.axvline(x=int(year), color='red', linestyle='--')

        # Increase the font size for labels and title
        ax.set_xlabel('Year')
        ax.set_ylabel('Traffic Value')
        ax.set_title('Traffic Trends Over the Years (Ireland)')

        # Improve legend placement and add a title
        ax.legend(title='Traffic Category', title_fontsize='12', loc='upper left')

        # Display the Matplotlib figure in Streamlit
        st.pyplot(fig)

def create_row_3():

    col1, col2, col3 = st.columns(3)

    countries = ['France', 'Ireland', 'Latvia', 'Malta', 'Norway', 'Poland',
       'Slovenia', 'Spain', 'United Kingdom']
    
    with col1:

        metric_name = "Passenger Car Traffic"

        # Create a Matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        color = '#0676B3'

        # Plot the data on the axis
        ax.plot(countries, y_test['PCT'], label=f'Actual {metric_name}', marker='o', color=color)
        ax.plot(countries, y_pred_lstm.iloc[:, 1], label=f'Predicted {metric_name} - LSTM', marker='x', color="#045689")
        ax.plot(countries, y_pred_lr.iloc[:,1], label=f'Predicted {metric_name} - LR', marker='^', color="#023F5F")

        # Set labels and title
        ax.set_xlabel('Country')
        ax.set_ylabel(metric_name)
        ax.set_title(f'Actual vs Predicted {metric_name} in 2021')

        # Show legend
        ax.legend()

        # Display the Matplotlib figure in Streamlit
        st.pyplot(fig)

    with col2:

        metric_name = "Bus and Motor Coach Traffic"

        # Create a Matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        color = '#DE9007'

        # Plot the data on the axis
        ax.plot(countries, y_test['BMCT'], label=f'Actual {metric_name}', marker='o', color=color)
        ax.plot(countries, y_pred_lstm.iloc[:, 2], label=f'Predicted {metric_name} - LSTM', marker='x', color="#B46C05")
        ax.plot(countries, y_pred_lr.iloc[:,2], label=f'Predicted {metric_name} - LR', marker='^', color="#8D5703")

        # Set labels and title
        ax.set_xlabel('Country')
        ax.set_ylabel(metric_name)
        ax.set_title(f'Actual vs Predicted {metric_name} in 2021')

        # Show legend
        ax.legend()

        # Display the Matplotlib figure in Streamlit
        st.pyplot(fig)

        with col3:

            metric_name = "Total Van, Pickup, Lorry and Road Tractor Traffic"

            # Create a Matplotlib figure and axis
            fig, ax = plt.subplots(figsize=(10, 6))
            color = '#09A077'

            # Plot the data on the axis
            ax.plot(countries, y_test['OT'], label=f'Actual {metric_name}', marker='o', color=color)
            ax.plot(countries, y_pred_lstm.iloc[:, 3], label=f'Predicted {metric_name} - LSTM', marker='x', color="#077252")
            ax.plot(countries, y_pred_lr.iloc[:,3], label=f'Predicted {metric_name} - LR', marker='^', color="#055D42")

            # Set labels and title
            ax.set_xlabel('Country')
            ax.set_ylabel(metric_name)
            ax.set_title(f'Actual vs Predicted {metric_name} in 2021')

            # Show legend
            ax.legend()

            # Display the Matplotlib figure in Streamlit
            st.pyplot(fig)

def create_row_4(filtered_df):

    # Show dataframe table
    df_reviews_filtered = df_reviews.loc[df_reviews["Category"].isin(filtered_df["Category"].unique()) & df_reviews["Year"].isin(filtered_df["Year"].unique())].iloc[:,:-2]
    st.dataframe(df_reviews_filtered, use_container_width=True, height=200)

# Display selected graph
filtered_df = create_row_1()
create_row_2(filtered_df)
create_row_3()
create_row_4(filtered_df)
