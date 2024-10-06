import streamlit as st
import base64
import background
import mysql.connector
import pandas as pd

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

# Sidebar with buttons
options = ["Fetch Data"]
if st.session_state.fetch_completed:
    options.append("Filter Data")
option = st.sidebar.radio("Select Action", options)

if option == "Fetch Data":

    if st.session_state.first_dropdown_data is None:
        show_overlay(True) 
        try:
            st.session_state.first_dropdown_data = background.statetransport("https://www.redbus.in")
        finally:
            show_overlay(False) 

    with st.container():
        new_first_choice = st.selectbox("Select the State_Transport", 
                                        ["Please select"] + list(st.session_state.first_dropdown_data.keys()),
                                        key="first_dropdown")

        # Check if first choice has changed
        if new_first_choice != st.session_state.first_choice:
            st.session_state.first_choice = new_first_choice
            if new_first_choice != "Please select":
                st.session_state.third_result = None
                show_overlay(True)
               
                st.session_state.second_dropdown_data = background.extract_bus_routes(st.session_state.first_dropdown_data[new_first_choice])
                
                    
            else:
                st.session_state.second_dropdown_data = None

        # Second dropdown
        if st.session_state.first_choice != "Please select" and st.session_state.second_dropdown_data is not None and st.session_state.third_result is None:
            show_overlay(False)
            second_choice = st.selectbox("Select the Bus_Route", 
                                         ["Please select"] + list(st.session_state.second_dropdown_data.keys()),
                                         key="second_dropdown")
            st.session_state.second_choice = second_choice
            
            if second_choice != "Please select" and st.session_state.third_result is None:
                show_overlay(True)
                st.session_state.third_result = background.scrape_bus_data(second_choice, st.session_state.second_dropdown_data[second_choice])
                show_overlay(True)

    # Simulate the Fetch Data process completion
    if st.button('Complete Fetch Data'):
        if st.session_state.third_result is None:
            st.write('\U0001F622')
            st.error("oops no buses found/Try fetching data again")
        else:
            background.sql_push(st.session_state.third_result)
            st.write('\U0001F60E')
            st.success('Data pushed successfully')
            st.balloons()
            st.session_state.fetch_completed = True
            st.session_state.third_result = None

elif option == "Filter Data" and st.session_state.fetch_completed:

    def get_data(query):
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='redbus_application'
        )
        # Fetch data into a DataFrame
        data = pd.read_sql(query, conn)
        print(data)  # For debugging purposes
        conn.close()
        return data

    # Initialize session state variables
    if 'data_fetch' not in st.session_state:
        st.session_state.data_fetch = False
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'expander_open' not in st.session_state:
        st.session_state.expander_open = False

    # Fetch data if not already fetched
    if not st.session_state.data_fetch:
        query = "SELECT * FROM bus_data"
        st.session_state.data = get_data(query)
        st.session_state.data_fetch = True

    # Check if data has been fetched successfully
    if st.session_state.data is not None:
        with st.expander("Filter Options", expanded=st.session_state.get('expander_open', False)):
            route_name = st.selectbox('Select Route Name', ['All'] + list(st.session_state.data['route_name'].unique()))
            busname = st.selectbox('Select Bus Name', ['All'] + list(st.session_state.data['busname'].unique()))
            bustype = st.selectbox('Select Bus Type', ['All'] + list(st.session_state.data['bustype'].unique()))
            star_rating = st.selectbox('Select Star Rating', ['All'] + list(st.session_state.data['star_rating'].unique()))
            if st.button('Filter'):
                query = "SELECT * FROM bus_data WHERE 1=1"  # Basic query

                # Construct the query based on selected filters
                if route_name != 'All':
                    query += f" AND route_name = '{route_name}'"

                if busname != 'All':
                    query += f" AND busname = '{busname}'"

                if bustype != 'All':
                    query += f" AND bustype = '{bustype}'"

                if star_rating != 'All':
                    query += f" AND star_rating = '{star_rating}'"

                # Fetch and display the filtered data
                filtered_data = get_data(query)

                if filtered_data.empty:
                    st.warning('No results found for the selected filters.')
                else:
                    st.success('filtered data is below')
                    st.session_state.data=filtered_data
                st.session_state.expander_open = False
    else:
        st.error('Data could not be fetched. Please check your database connection or query.')


    if st.session_state.data is not None:
        st.dataframe(st.session_state.data)

# Quit button at the bottom of the sidebar
if st.sidebar.button("Quit"):
    st.stop()
    os.close()
