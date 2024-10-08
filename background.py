import time
import pandas as pd
import mysql.connector
from selenium import webdriver
import logging
import re
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from mysql.connector import Error
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException


def statetransport(url):
    # # chrome_options = Options()
    # # chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome()
    # driver.minimize_window()
    # driver.get(url)
    # time.sleep(3)

    # bus_routes = {}
    # index = 0

    # while True:
    #     try:
    #         clickable_elements = driver.find_elements(By.CLASS_NAME, 'rtcBack')  # clickable route elements
            
    #         # Fetch bus name for each element in the loop
    #         bus_name_elements = driver.find_elements(By.CLASS_NAME, 'rtcName')
    #         if index >= len(clickable_elements):
    #             break
            
    #         # Extract the bus name and make sure it corresponds to the clickable element
    #         bus_name = bus_name_elements[index].text
    #         element = clickable_elements[index]
            
    #         try:
    #             ActionChains(driver).move_to_element(element).click().perform()
    #             time.sleep(1)
                
    #             # Fetch the current URL (route link)
    #             current_url = driver.current_url

    #             # Add the bus name and link to the dictionary
    #             bus_routes[bus_name] = current_url

    #             driver.back()
    #             time.sleep(1)

    #             index += 1

    #         except Exception as e:
    #             print(f"Error with element {index + 1}: {e}")
    #             driver.back()
    #             time.sleep(1)
    #             index += 1

    #     except Exception as e:
    #         print(f"Error finding elements: {e}")
    #         break

    # driver.quit()
    bus_routes={'APSRTC': 'https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile', 'KERALA RTC': 'https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile', 'TGSRTC': 'https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile', 'KTCL': 'https://www.redbus.in/online-booking/ktcl/?utm_source=rtchometile', 'RSRTC': 'https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile', 'SBSTC': 'https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc/?utm_source=rtchometile', 'HRTC': 'https://www.redbus.in/online-booking/hrtc/?utm_source=rtchometile', 'ASTC': 'https://www.redbus.in/online-booking/astc/?utm_source=rtchometile', 'UPSRTC': 'https://www.redbus.in/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc/?utm_source=rtchometile', 'WBTC': 'https://www.redbus.in/online-booking/wbtc-ctc/?utm_source=rtchometile', 'CTU RTC': 'https://www.redbus.in/online-booking/chandigarh-transport-undertaking-ctu', 'PEPSU': 'https://www.redbus.in/online-booking/pepsu/?utm_source=rtchometile', 'NBSTC': 'https://www.redbus.in/online-booking/north-bengal-state-transport-corporation', 'BSRTC': 'https://www.redbus.in/online-booking/bihar-state-road-transport-corporation-bsrtc/?utm_source=rtchometile', 'KAAC Transport': 'https://www.redbus.in/online-booking/kaac-transport', 'WBSTC': 'https://www.redbus.in/online-booking/west-bengal-transport-corporation?utm_source=rtchometile', 'JKSRTC': 'https://www.redbus.in/online-booking/jksrtc'}

    return bus_routes
# statetransport("https://www.redbus.in")



def extract_bus_routes(url):
    driver = webdriver.Chrome()
    driver.minimize_window()
    driver.get(url)
    time.sleep(3)
    bus_routes_dict = {}
    page_num = 1 

    while True:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1) 
        driver.execute_script("window.scrollBy(0, 1500);")
        time.sleep(1)
        routes = driver.find_elements(By.CLASS_NAME, 'route_link')

        for route in routes:
            route_name = route.find_element(By.CLASS_NAME, 'route').text.strip()
            
            route_link_element = route.find_element(By.TAG_NAME, 'a') 
            route_link = route_link_element.get_attribute('href') if route_link_element else None

            # Store the route_name as key and route_link as value
            bus_routes_dict[route_name] = route_link

        try:
            next_page_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, f"//div[@class='DC_117_pageTabs ' and text()='{page_num + 1}']"))
            )

            driver.execute_script("arguments[0].click();", next_page_button)
            page_num += 1

        except Exception as e:
            break
    
    driver.quit()
    return bus_routes_dict
# extract_bus_routes('https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile')

import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import pandas as pd

def scrape_bus_data(route_name, route_link):
    def retry_on_stale(func, max_attempts=5):
        for attempt in range(max_attempts):
            try:
                return func()
            except StaleElementReferenceException:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(1)

    def click_buttons_within_gmeta_data(gbus, retries=10):
        attempt = 0
        while attempt < retries:
            try:
                logger.info("Locating buttons...")
                buttons = WebDriverWait(gbus, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, ".//i[contains(@class, 'p-left-10') and contains(@class, 'icon-down')]"))
                )
                logger.info(f"Found {len(buttons)} buttons.")
                time.sleep(2)
                for button in buttons:
                    try:
                        logger.info("Scrolling to button...")
                        driver.execute_script("arguments[0].scrollIntoView();", button)
                        time.sleep(1)
                        logger.info("Clicking button...")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)
                    except Exception as e:
                        logger.warning(f"Error clicking button: {e}")
                        continue
                break
            except Exception as e:
                attempt += 1
                logger.warning(f"Error clicking buttons, attempt {attempt}/{retries}: {e}")
                if attempt == retries:
                    logger.error("Max retries reached. Moving to the next bus.")
                    break
                time.sleep(2)

    def scroll_to_load_buses():
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 100);")
            time.sleep(1)

    def extract_bus_details(route_name, route_link):
        nonlocal bus_id
        driver.get(route_link)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'gmeta-data')))
        gov_buses = driver.find_elements(By.CLASS_NAME, 'gmeta-data')
        for count, gbus in enumerate(gov_buses, 1):
            click_buttons_within_gmeta_data(gbus)
            if count == len(gov_buses):
                break
            scroll_to_load_buses()
        scroll_to_load_buses()   

        gov_buses = driver.find_elements(By.CLASS_NAME, 'bus-item')
        for gbus in gov_buses:
            try:
                busname = retry_on_stale(lambda: gbus.find_element(By.CLASS_NAME, 'travels').text.strip())
                bustype = retry_on_stale(lambda: gbus.find_element(By.CLASS_NAME, 'bus-type').text.strip())
                departing_time = retry_on_stale(lambda: gbus.find_element(By.CLASS_NAME, 'dp-time').text.strip())
                duration = retry_on_stale(lambda: gbus.find_element(By.CLASS_NAME, 'dur').text.strip())

                today = datetime.now().date()
                departure_datetime = datetime.combine(today, datetime.strptime(departing_time, "%H:%M").time())
                
                duration_parts = duration.split()
                duration_hours = int(duration_parts[0].replace('h', ''))
                duration_minutes = int(duration_parts[1].replace('m', '')) if len(duration_parts) > 1 else 0
                duration_obj = timedelta(hours=duration_hours, minutes=duration_minutes)

                arrival_datetime = departure_datetime + duration_obj

                formatted_departure = departure_datetime.strftime("%Y-%m-%d %H:%M")
                formatted_arrival = arrival_datetime.strftime("%Y-%m-%d %H:%M")

                try:
                    star_rating = retry_on_stale(lambda: gbus.find_element(By.CLASS_NAME, 'rating').find_element(By.TAG_NAME, 'span').text.strip())
                    star_rating = float(star_rating) if star_rating else 0.0
                except (NoSuchElementException, ValueError):
                    star_rating = 0.0

                try:
                    price = retry_on_stale(lambda: gbus.find_element(By.CLASS_NAME, 'fare').find_element(By.TAG_NAME, 'span').text.strip())
                    price = price.replace('INR', '').strip()
                except NoSuchElementException:
                    price = '0'

                try:
                    seat_availability = retry_on_stale(lambda: gbus.find_element(By.CLASS_NAME, 'seat-left').text.strip())
                    seat_availability = seat_availability.split()[0] if seat_availability else '0'
                except (NoSuchElementException, IndexError):
                    seat_availability = '0'

                bus_df.loc[len(bus_df)] = [bus_id, route_name, route_link, busname, bustype, 
                                           formatted_departure, duration, formatted_arrival, 
                                           star_rating, price, seat_availability]
                bus_id += 1
            except StaleElementReferenceException:
                logger.warning("Encountered a stale element reference, retrying...")
                continue

    bus_id = 1
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    columns = ['id', 'route_name', 'route_link', 'busname', 'bustype', 'departing_time', 'duration', 'reaching_time', 'star_rating', 'price', 'seat_availability']
    bus_df = pd.DataFrame(columns=columns)

    try:
        extract_bus_details(route_name, route_link)
    except Exception as e:
        logger.error(f"Error in extract_bus_details: {e}")
    finally:
        driver.quit()

    return bus_df

# scrape_bus_data('Hyderabad to Vijayawada', 'https://www.redbus.in/bus-tickets/hyderabad-to-vijayawada')


def sql_push(final_df):

    final_df.dropna(subset=['departing_time', 'duration', 'reaching_time','price'], how='any', inplace=True)
    final_df.dropna(subset=['route_name', 'route_link', 'busname'], how='any', inplace=True)
    final_df['bustype'].replace('', 'Seater', inplace=True)
    final_df['star_rating'].fillna(0.0, inplace=True)
    final_df = final_df[final_df['seat_availability'] != '0']
    final_df = final_df.loc[final_df[['route_name', 'route_link', 'busname', 'bustype', 'departing_time', 'duration', 'reaching_time', 'star_rating','price','seat_availability']].drop_duplicates().index]
    final_df['id'] = range(1, len(final_df) + 1)
    final_df.reset_index(drop=True, inplace=True)

    # Convert departing_time and reaching_time to datetime
    final_df['departing_time'] = pd.to_datetime(final_df['departing_time'])
    final_df['reaching_time'] = pd.to_datetime(final_df['reaching_time'])

    connection = None

    try:
        connection = mysql.connector.connect(
            host='localhost',        
            user='your_user',               
            password='your_password'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            cursor.execute("CREATE DATABASE IF NOT EXISTS redbus_application")
            cursor.execute("USE redbus_application")
            cursor.execute("DROP TABLE IF EXISTS bus_data")

            create_table_query = """
            CREATE TABLE bus_data (
                id INT PRIMARY KEY,
                route_name VARCHAR(255),
                route_link VARCHAR(255),
                busname VARCHAR(255),
                bustype VARCHAR(255),
                departing_time DATETIME,
                duration VARCHAR(20),
                reaching_time DATETIME,
                star_rating FLOAT,
                price DECIMAL(10, 2),
                seat_availability INT
            );
            """
            cursor.execute(create_table_query)

            for i, row in final_df.iterrows():
                sql = """
                INSERT INTO bus_data (id, route_name, route_link, busname, bustype, departing_time, duration, reaching_time, star_rating, price, seat_availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                # Convert datetime to string in the format MySQL expects
                row_data = list(row)
                row_data[5] = row_data[5].strftime('%Y-%m-%d %H:%M:%S')
                row_data[7] = row_data[7].strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(sql, tuple(row_data))

            connection.commit()
            print(f"{cursor.rowcount} rows were inserted successfully.")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return final_df
