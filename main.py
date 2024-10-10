import streamlit as st
import base64
import background
import mysql.connector
import pandas as pd
import time

def show_overlay(show=True):
    if show:
        overlay_css_and_html = f"""
        <style>
        .overlay {{
            position: fixed; 
            width: 100vw;
            height: 100vh;
            top: 0;
            left: 0;
            background-color: rgba(0,0,0,0.7);
            z-index: 9999; /* Ensure it overlays everything */
            cursor: not-allowed;
        }}
        .overlay-content {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
        }}
        </style>
        <div class="overlay">
            <div class="overlay-content">
                <img src="data:image/jpeg;base64,{center_img_base64}" alt="Center Image" style="height: 100px;" />
                <p>We are loading the contents for you. Please wait...</p>
            </div>
        </div>
        """
        st.markdown(overlay_css_and_html, unsafe_allow_html=True)
    else:
        hide_overlay_css = '<style>.overlay { display: none; }</style>'
        st.markdown(hide_overlay_css, unsafe_allow_html=True)

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Define the paths to your images
left_image = "logo/left.jpg"
right_image = "logo/right.jpg"
center_image = "logo/center.jpg"

# Convert images to base64
left_img_base64 = image_to_base64(left_image)
right_img_base64 = image_to_base64(right_image)
center_img_base64 = image_to_base64(center_image)
# Create the header layout using HTML
header_html = f"""
<div style="display: flex; align-items: center; justify-content: space-between; background-color: white; padding: 10px; border-radius: 5px;">
    <img src="data:image/jpeg;base64,{left_img_base64}" alt="Left Image" style="height: 100px;">
    <h1 style="font-size: 100px; font-weight: bold; color:#FF0000; margin: 0;">MINI BUS</h1>
    <img src="data:image/jpeg;base64,{right_img_base64}" alt="Right Image" style="height: 100px;">
</div>
"""

# Render the custom header
st.markdown(header_html, unsafe_allow_html=True)

# Initialize session state
if 'fetch_completed' not in st.session_state:
    st.session_state.fetch_completed = False
if 'first_dropdown_data' not in st.session_state:
    st.session_state.first_dropdown_data = None
if 'first_choice' not in st.session_state:
    st.session_state.first_choice = "Please select"
if 'second_choice' not in st.session_state:
    st.session_state.second_choice = "Please select"
if 'second_dropdown_data' not in st.session_state:
    st.session_state.second_dropdown_data = None
if 'third_result' not in st.session_state:
    st.session_state.third_result = None


def sidebar_options():
    options = ["Fetch Data"]
    if st.session_state.fetch_completed:
        options.append("Filter Data")
    return st.sidebar.radio("Select Action", options)
option = sidebar_options()

if option == "Fetch Data":

    if st.session_state.first_dropdown_data is None:
        st.session_state.first_dropdown_data = background.statetransport("https://www.redbus.in")
        st.rerun()

    with st.container():
        # First dropdown for State Transport
        new_first_choice = st.selectbox("Select the State_Transport", 
                                        ["Please select"] + list(st.session_state.first_dropdown_data.keys()),
                                        key="first_dropdown")
        
        if new_first_choice != st.session_state.first_choice:
            st.session_state.first_choice = new_first_choice
            st.session_state.second_choice = "Please select"
            st.session_state.second_dropdown_data = None
            st.session_state.third_result = None
            
            if new_first_choice != "Please select":
                show_overlay(True)
                st.session_state.second_dropdown_data = background.extract_bus_routes(st.session_state.first_dropdown_data[new_first_choice])
                show_overlay(False)
            st.rerun()

        # Second dropdown for Bus Route
        if st.session_state.first_choice != "Please select" and st.session_state.second_dropdown_data is not None:
            new_second_choice = st.selectbox("Select the Bus_Route",
                                             ["Please select"] + list(st.session_state.second_dropdown_data.keys()),
                                             key="second_dropdown")
            
            if new_second_choice != st.session_state.second_choice:
                st.session_state.second_choice = new_second_choice
                st.session_state.third_result = None
                
                if new_second_choice != "Please select":
                    show_overlay(True)
                    st.session_state.third_result = background.scrape_bus_data(new_second_choice, st.session_state.second_dropdown_data[new_second_choice])
                    show_overlay(False)
                st.rerun()
    if st.session_state.third_result is not None:
        st.write(st.session_state.third_result)
 
    if st.button('Complete Fetch Data'):
        if st.session_state.third_result is None :
            st.write('\U0001F622')
            st.error("oops no buses found/Try fetching data again")
        elif st.session_state.third_result is not None and len(st.session_state.third_result) <1 :
            st.write('\U0001F622')
            st.error("oops no buses found/Try fetching data again")
        else:
            background.sql_push(st.session_state.third_result)
            st.write('\U0001F60E')
            st.success('Data pushed successfully')
            st.balloons()
            st.session_state.fetch_completed = True
            st.session_state.third_result = None
            time.sleep(3)
            st.rerun() 

if option == "Filter Data" and st.session_state.fetch_completed:

    def get_data(query):
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='redbus_application'
        )
        # Fetch data into a DataFrame
        data = pd.read_sql(query, conn)
        conn.close()
        return data 

    if 'data_fetch' not in st.session_state:
        st.session_state.data_fetch = False
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'original_data' not in st.session_state:
        st.session_state.original_data = None
    if 'expander_open' not in st.session_state:
        st.session_state.expander_open = False
    if 'expander_open' not in st.session_state:
        st.session_state.expander_open = True 

    if not st.session_state.data_fetch:
        # Fetch original data from the database and store it
        query = "SELECT * FROM bus_data"
        st.session_state.original_data = get_data(query)
        st.session_state.data = st.session_state.original_data.copy()
        st.session_state.data_fetch = True

    if st.session_state.original_data is not None:
        # Ensure filter options are fetched from the original data, not the filtered data
        with st.expander("Filter Options", expanded=st.session_state.expander_open):

            # Bus Type Filter (checkboxes)
            st.write("Select Bus Type:")
            bus_types = list(st.session_state.original_data['bustype'].unique())
            selected_bus_types = [bt for bt in bus_types if st.checkbox(bt, key=f"bustype_{bt}")]

            # Star Rating Filter (checkboxes for ranges)
            st.write("Select Star Rating Range:")
            star_rating_1_2 = st.checkbox('1 to 2 stars')
            star_rating_2_3 = st.checkbox('2 to 3 stars')
            star_rating_3_4 = st.checkbox('3 to 4 stars')
            star_rating_4_5 = st.checkbox('4 to 5 stars')

            # Price Range Filter (Handle same min/max value based on original data)
            price_min = int(st.session_state.original_data['price'].min())
            price_max = int(st.session_state.original_data['price'].max())

            if price_min == price_max:
                st.write(f"Only one price available: ₹{price_min}")
            else:
                price_min, price_max = st.slider(
                    'Select Price Range',
                    min_value=price_min,
                    max_value=price_max,
                    value=(price_min, price_max)
                )

            # Duration Filter (checkboxes based on original data)
            st.write("Select Duration Range:")
            durations = list(st.session_state.original_data['duration'].unique())
            selected_durations = [d for d in durations if st.checkbox(d, key=f"duration_{d}")]

            # Departing Time Filter (checkboxes with four predefined options)
            st.write("Select Departing Time:")
            morning_12_6 = st.checkbox('Morning 12 AM to 6 AM')
            morning_6_12 = st.checkbox('Morning 6 AM to 12 PM')
            afternoon_12_6 = st.checkbox('Afternoon 12 PM to 6 PM')
            evening_6_12 = st.checkbox('Evening 6 PM to 12 AM')

            # Filter button
            if st.button('Filter'):
                st.session_state.expander_open = False
                # Construct the query
                query = "SELECT * FROM bus_data WHERE 1=1"

                # Add Bus Type filter
                if selected_bus_types:
                    bus_type_query = " OR ".join([f"bustype = '{bt}'" for bt in selected_bus_types])
                    query += f" AND ({bus_type_query})"

                # Add Price Range filter
                query += f" AND price BETWEEN {price_min} AND {price_max}"

                # Add Star Rating filters based on checkboxes
                star_conditions = []
                if star_rating_1_2:
                    star_conditions.append("star_rating >= 1 AND star_rating < 2")
                if star_rating_2_3:
                    star_conditions.append("star_rating >= 2 AND star_rating < 3")
                if star_rating_3_4:
                    star_conditions.append("star_rating >= 3 AND star_rating < 4")
                if star_rating_4_5:
                    star_conditions.append("star_rating >= 4 AND star_rating <= 5")

                if star_conditions:
                    query += " AND (" + " OR ".join(star_conditions) + ")"

                # Add Duration filters
                if selected_durations:
                    duration_query = " OR ".join([f"duration = '{d}'" for d in selected_durations])
                    query += f" AND ({duration_query})"

                # Add Departing Time filter (formatted)
                time_conditions = []
                if morning_12_6:
                    time_conditions.append("TIME(departing_time) BETWEEN '00:00:00' AND '05:59:59'")
                if morning_6_12:
                    time_conditions.append("TIME(departing_time) BETWEEN '06:00:00' AND '11:59:59'")
                if afternoon_12_6:
                    time_conditions.append("TIME(departing_time) BETWEEN '12:00:00' AND '17:59:59'")
                if evening_6_12:
                    time_conditions.append("TIME(departing_time) BETWEEN '18:00:00' AND '23:59:59'")

                if time_conditions:
                    query += " AND (" + " OR ".join(time_conditions) + ")"

                # Fetch and display the filtered data from the database
                filtered_data = get_data(query)

                if filtered_data.empty:
                    st.warning('No results found for the selected filters.')
                else:
                    st.success('Filtered data is below')
                    st.session_state.data = filtered_data

                

    else:
        st.error('Data could not be fetched. Please check your database connection or query.')

    if st.session_state.data is not None:
        df_display = st.session_state.data.copy()
        df_display['route_link'] = df_display['route_link'].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>')
        st.markdown(df_display.to_html(escape=False), unsafe_allow_html=True)



if st.sidebar.button("Quit"):
    st.stop()
    os.close()
