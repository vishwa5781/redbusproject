Bus Route Data Scraper
Overview
This project is a web scraping application designed to extract bus route data from the RedBus website. It retrieves information about various bus services, including details such as bus names, types, departure times, durations, arrival times, star ratings, prices, and seat availability. The collected data is then stored in a MySQL database.

Features
Scrapes bus route information from RedBus using Selenium.
Handles pagination to gather data from multiple pages.
Extracts detailed bus information including:
Bus name
Bus type
Departure time
Duration
Arrival time
Star rating
Price
Seat availability
Stores the collected data in a MySQL database.
Configurable for different bus routes.
Technologies Used
Python
Selenium
Pandas
MySQL Connector
Chrome WebDriver
Setup Instructions
Prerequisites
Python 3.x
MySQL Server
Chrome WebDriver
Installation
Clone the repository:

bash
Copy code
git clone <repository_url>
cd <repository_directory>
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Set up the MySQL database:

Ensure that your MySQL server is running.
Create a database named redbus_application (the script will automatically create it if it does not exist).
Configuration
MySQL Credentials: Update the database connection details in the sql_push function of your script to match your MySQL configuration:

python
Copy code
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='your_password'  # Update this with your actual password
)
Selenium WebDriver: Ensure that the Chrome WebDriver is compatible with your installed version of Chrome. You can download the driver from ChromeDriver's official site.

Usage
Run the main script:

Call the statetransport function to get the available bus routes:

python
Copy code
bus_routes = statetransport("https://www.redbus.in")
Extract bus data for a specific route:

Use the scrape_bus_data function with the desired route name and link:

python
Copy code
bus_data_df = scrape_bus_data('Hyderabad to Vijayawada', 'https://www.redbus.in/bus-tickets/hyderabad-to-vijayawada')
Push data to MySQL:

Use the sql_push function to store the scraped data into the MySQL database:

python
Copy code
sql_push(bus_data_df)
Logging
The application uses logging to capture events and errors. Logs will be output to the console, providing insight into the scraping process and any issues encountered.

Author
Kaarthikk Vishwa
