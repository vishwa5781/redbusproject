# Bus Route Data Fetching and Filtering Application

This Streamlit application is designed to fetch and filter bus route data from the RedBus website using web scraping (Selenium) and a MySQL database to store the results. The application provides an intuitive interface for users to select State Transport, Bus Routes, and apply various filters to the fetched data, allowing a smooth experience for bus route data analysis.

## Features

- **Data Fetching**: Scrapes bus route data from RedBus based on user selection of State Transport and Bus Routes.
- **Data Filtering**: After fetching, users can filter the data based on:
  - Bus Type
  - Price Range
  - Star Ratings
  - Duration
  - Departure Time
- **Real-time Overlays**: A loading screen overlay is shown while data is being fetched.
- **Session State Management**: The app stores state between sessions for fetched and filtered data.
- **Data Visualization**: Displays filtered results in a clean and interactive table format with links to the RedBus routes.

## Setup and Installation

1. Clone the repository:
    ```bash
    git clone <[(https://github.com/vishwa5781/redbusproject]>
    cd <redbusproject>
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Download and set up the necessary web driver for Selenium (e.g., ChromeDriver). Make sure it's compatible with the browser you're using for scraping.

4. Set up your MySQL database and configure the `redbus_application` database schema to store the bus route data. An example schema for the `bus_data` table:

    ```sql
    CREATE TABLE bus_data (
      id INT PRIMARY KEY AUTO_INCREMENT,
      route_name VARCHAR(255),
      route_link VARCHAR(255),
      busname VARCHAR(255),
      bustype VARCHAR(100),
      departing_time TIMESTAMP,
      duration VARCHAR(20),
      reaching_time TIMESTAMP,
      star_rating DECIMAL(2,1),
      price INT,
      seat_availability INT
    );
    ```

5. Ensure your MySQL server is running and you have the correct credentials to connect. Modify the connection details in the script accordingly:

    ```python
    conn = mysql.connector.connect(
        host='localhost',
        user='your username',
        password='your password',
        database='your database'
    )
    ```

## How to Run

1. Start the application using Streamlit:
    ```bash
    streamlit run main.py
    ```

2. Once the app is running, follow these steps:
   - **Fetch Data**: Select "Fetch Data" from the sidebar to begin scraping bus route data. Choose the State Transport and Bus Route.
   - **Complete Fetch Data**: After the data is fetched, you can choose to store it in the database.
   - **Filter Data**: Once the data is fetched and stored, you can apply filters to the data using various filter options.
   
3. Use the **Quit** button in the sidebar to stop the application.

## Code Structure

- **main.py**: Main Streamlit application file that handles the user interface, data fetching, and filtering logic.
- **background.py**: A utility module that handles the actual web scraping and database push functionalities.
- **logo/**: Directory containing images used in the header of the application.

## Dependencies

- `streamlit`
- `pandas`
- `mysql-connector-python`
- `Selenium`
- `base64`

Install all dependencies using:

```bash
pip install -r requirements.txt
```

## Author

Kaarthikk Vishwa

