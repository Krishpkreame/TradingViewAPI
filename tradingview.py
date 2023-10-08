# Environment variables and datetime and regex
import os
import re
from datetime import datetime
# For web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidSessionIdException
# For waiting for web elements to load instead of time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# For MySQL database
import json
import pymysql


class API:
    # Initialize class variables and environment variables
    def __init__(self):
        # Get DB info from environment variable
        self.dbconf = json.loads(os.environ.get("MYSQL_DB1_JSON_CONN", ""))
        # Set up flags for services, first connect to database
        self.connection = pymysql.connect(
            host=self.dbconf["host"],
            user=self.dbconf["user"],
            password=self.dbconf["password"],
            db=self.dbconf["database"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)
        # Get symbol names from database
        with self.connection.cursor() as cursor:
            _sql = f"SELECT * FROM `input_info`"
            cursor.execute(_sql)
            # Set up flags for services of each market
            self.tv_market_data = {
                row['tv_symbol']: {
                    'status': False,
                    'link': row['tv_link'],
                    'instance': None
                } for row in cursor}
        # Close the temp connection
        self.connection.close()

        # Get Selenium URL from environment variable
        self.selenium_url = os.environ.get("SELENIUM_URL", "")
        # Set up Selenium options
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_argument("--start-maximized")

    # Start market service for symbol
    def start_market_service(self, __tvsymbol):
        try:
            # Check if symbol is not supported, raise error
            if __tvsymbol not in self.tv_market_data:
                raise Exception(
                    f"TradingView {__tvsymbol} is not supported. (start)")

            # Check if flagged symbol is running and not timed out.
            try:
                # Check timezone button to see if session is timed out
                self.tv_market_data[__tvsymbol]["instance"].find_element(
                    By.XPATH, '//button[@data-name="time-zone-menu"]').text
            # If session doesnt exsit, continue starting the service
            except AttributeError as e:
                pass
            # If session is timed out, restart the flags, continue starting the service
            except InvalidSessionIdException as e:
                self.tv_market_data[__tvsymbol]["status"] = False
                self.tv_market_data[__tvsymbol]["instance"] = None

            # Check if flagged symbol is not running, start the service
            if not self.tv_market_data[__tvsymbol]["status"]:
                # Change status to running
                self.tv_market_data[__tvsymbol]["status"] = True
                # Start selenium browser with needed options
                self.tv_market_data[__tvsymbol]["instance"] = webdriver.Remote(
                    command_executor=self.selenium_url,
                    options=self.browser_options)
                # Go to TradingView link for each symbol
                self.tv_market_data[__tvsymbol]["instance"].get(
                    self.tv_market_data[__tvsymbol]["link"])
                # Wait for Page to load
                WebDriverWait(self.tv_market_data[__tvsymbol]["instance"], 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@data-name="legend-source-item"]')))
                self.tv_market_data[__tvsymbol]["instance"].implicitly_wait(1)

                # Get session id for flagged symbol
                temp_sessionid = str(
                    self.tv_market_data[__tvsymbol]["instance"].session_id)
                # Return success message
                return f"{__tvsymbol} service started. {temp_sessionid}"
            # If flagged symbol is running, raise error
            else:
                # Get session id for flagged symbol
                temp_sessionid = str(
                    self.tv_market_data[__tvsymbol]["instance"].session_id)
                raise Exception(
                    f"TradingView {__tvsymbol} service is already running. {temp_sessionid}")
        # For redundant error handling, if anything happens, reset flags and raise error
        except InvalidSessionIdException as e:
            self.tv_market_data[__tvsymbol]["status"] = False
            self.tv_market_data[__tvsymbol]["instance"] = None
            raise InvalidSessionIdException(e)

    # Get rsi value for symbol
    def get_rsi(self, __tvsymbol):
        try:
            # Check if symbol is not supported, raise error
            if __tvsymbol not in self.tv_market_data:
                raise Exception(
                    f"TradingView {__tvsymbol} is not supported. (get rsi)")

            # Check if flagged symbol is running
            if self.tv_market_data[__tvsymbol]["status"]:
                # Get raw string value of time, rsi, price from TradingView
                self.raw_time = self.tv_market_data[__tvsymbol]["instance"].find_element(
                    By.XPATH, '//button[@data-name="time-zone-menu"]').text.split("\n")[-1]
                self.raw_rsi_value = self.tv_market_data[__tvsymbol]["instance"].find_element(
                    By.XPATH, '//div[@data-name="legend-source-item"]').text.split("\n")[-1]
                self.raw_price_price = self.tv_market_data[__tvsymbol]["instance"].find_element(
                    By.XPATH, '//div[@data-name="legend-series-item"]').text.split("\n")[-1]

                # Format and filter raw time string into datetime
                self.time_step1 = self.raw_time.split(" ")[0]
                self.time_step2 = datetime.strptime(
                    self.time_step1, "%H:%M:%S").time()
                self.datetime_value = str(datetime.combine(
                    datetime.now().date(), self.time_step2))

                # Format and filter raw rsi string into float
                self.rsi_value = float(self.raw_rsi_value)

                # Format and filter raw price string into dict using regex
                self.price_step1 = [
                    float(value) for value in re.findall(
                        '\d+\.\d+', self.raw_price_price)][0:4]
                self.price_values = {
                    "open": self.price_step1[0],
                    "high": self.price_step1[1],
                    "low": self.price_step1[2],
                    "close": self.price_step1[3]}

                # Get session id for flagged symbol
                temp_sessionid = str(
                    self.tv_market_data[__tvsymbol]["instance"].session_id)

                # Return values
                return {
                    "rsi": self.rsi_value,
                    "datetime": self.datetime_value,
                    "tv_symbol": __tvsymbol,
                    "price": self.price_values,
                    "sessionid": temp_sessionid
                }
            # If flagged symbol is not running, raise error
            else:
                raise Exception(
                    f"TradingView {__tvsymbol} service is not running, can not get rsi.")
        # If session is timed out, reset flags, raise error
        except InvalidSessionIdException as e:
            self.tv_market_data[__tvsymbol]["status"] = False
            self.tv_market_data[__tvsymbol]["instance"] = None
            raise InvalidSessionIdException(e)

    # Stop market service for symbol
    def stop_market_service(self, __tvsymbol):
        try:
            # Check if symbol is not supported, raise error
            if __tvsymbol not in self.tv_market_data:
                raise Exception(
                    f"TradingView {__tvsymbol} is not supported. (stop)")

            # Check if flagged symbol is running
            if self.tv_market_data[__tvsymbol]["status"]:
                # Get session id for flagged symbol (before quitting)
                temp_sessionid = str(
                    self.tv_market_data[__tvsymbol]["instance"].session_id)

                # Quit selenium and reset flags
                self.tv_market_data[__tvsymbol]["instance"].quit()
                self.tv_market_data[__tvsymbol]["status"] = False
                self.tv_market_data[__tvsymbol]["instance"] = None

                # Return success message
                return f"{__tvsymbol} service stopped. {temp_sessionid}"
            # If flagged symbol is not running, raise error
            else:
                raise Exception(
                    f"TradingView {__tvsymbol} service is not running.")
        # If session is timed out, reset flags, raise error
        except InvalidSessionIdException as e:
            self.tv_market_data[__tvsymbol]["status"] = False
            self.tv_market_data[__tvsymbol]["instance"] = None
            raise InvalidSessionIdException(e)
