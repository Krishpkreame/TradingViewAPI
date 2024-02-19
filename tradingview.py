import os
import re
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions as sel_exc
import pymongo


class API:
    # Initialize class variables and environment variables
    def __init__(self):
        """
        Initializes an instance of the TradingViewAPI class.

        The __init__ method sets up the necessary configurations and connections for the TradingViewAPI class.

        Parameters:
            None

        Returns:
            None
        """
        # Get mongodb connection string if set, otherwise assume local
        self.conn_str = os.environ.get(
            "DB_CONN_STR",
            "mongodb://user:password@localhost:27017/")
        # Get selenium url if set, otherwise assume local
        self.selenium_url = os.environ.get(
            "SELENIUM_URL", "http://localhost:4444/wd/hub")

        # Initialize browser options
        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_argument("--start-maximized")

        # Initialize MongoDB client
        self.mydb = pymongo.MongoClient(self.conn_str)["cmc_db"]
        # Initialize Mongo collections
        self.info_data = self.mydb["info"]

        # Set up flags for services of each market
        self.session_flags = {
            row['tv_symbol']: {
                'status': False,
                'keyword': row['cmc_keyword'],
                'link': row['tv_link'],
                'instance': None
            } for row in self.info_data.find()}

    def find(self, __tvsymbol, xpath, multiple=False):
        """
        Find element(s) using XPath in the TradingView session.

        Parameters:
        __tvsymbol (str): The symbol of the TradingView session.
        xpath (str): The XPath expression to locate the element(s).
        multiple (bool, optional): If True, returns a list of elements. If False, returns a single element. Default is False.

        Returns:
        WebElement or list: The found element(s) or an empty list if no element is found.
        """
        if multiple:
            return self.session_flags[__tvsymbol]["instance"].find_elements(By.XPATH, xpath)
        else:
            return self.session_flags[__tvsymbol]["instance"].find_element(By.XPATH, xpath)

    def start_market_service(self, __tvsymbol):
        """
        Starts the market service for the given symbol.

        Args:
            __tvsymbol (str): The symbol for which to start the market service.

        Returns:
            dict: A dictionary containing the success status, message, symbol, and session ID.
        """
        # Check if the given TV symbol is in the database
        if __tvsymbol not in self.session_flags:
            return {
                "success": False,
                "message": f"{__tvsymbol} not found in database",
                "symbol": __tvsymbol}

        # Check if the market service for the given TV symbol is already started
        if self.session_flags[__tvsymbol]['status']:
            return {
                "success": False,
                "message": f"{__tvsymbol} already started",
                "symbol": __tvsymbol}

        try:
            # Check if the Selenium session is still active by trying to find the time zone menu button
            self.find(
                __tvsymbol,
                '//button[@data-name="time-zone-menu"]'
            )
        except sel_exc.InvalidSessionIdException:
            print("Selenium session timed out.\n Creating new session...")
            # If the session is not active, restart the session
            self.session_flags[__tvsymbol]["status"] = False
            self.session_flags[__tvsymbol]["instance"] = None
        except AttributeError:
            print("Selenium session not created.\n Creating new session...")

        # Create a new Selenium session
        self.session_flags[__tvsymbol]["instance"] = webdriver.Remote(
            command_executor=self.selenium_url,
            options=self.browser_options)

        # Open the TradingView link for the given TV symbol
        self.session_flags[__tvsymbol]["instance"].get(
            self.session_flags[__tvsymbol]["link"])
        # Wait for the page to load
        time.sleep(5)

        # Set the flag for the market service to True
        self.session_flags[__tvsymbol]["status"] = True

        # Return the success status, message, symbol, and session ID
        return {
            "success": True,
            "message": f"{__tvsymbol} service started",
            "symbol": __tvsymbol,
            "session_id": self.session_flags[__tvsymbol]["instance"].session_id,
        }

    def stop_market_service(self, __tvsymbol):
        """
        Stop the market service for the given TV symbol.

        Args:
            __tvsymbol (str): The TV symbol for which to stop the market service.

        Returns:
            dict: A dictionary containing the success status, message, and symbol.
        """
        # Check if the given TV symbol is in the database
        if __tvsymbol not in self.session_flags:
            return {
                "success": False,
                "message": f"{__tvsymbol} not found in database",
                "symbol": __tvsymbol}

        # Check if the market service for the given TV symbol is already stopped
        if not self.session_flags[__tvsymbol]['status']:
            return {
                "success": False,
                "message": f"{__tvsymbol} already stopped",
                "symbol": __tvsymbol}

        try:
            # Check if the Selenium session is active
            self.find(
                __tvsymbol,
                '//button[@data-name="time-zone-menu"]'
            )
        except sel_exc.InvalidSessionIdException:
            print("Selenium session timed out.")
            self.session_flags[__tvsymbol]["status"] = False
            self.session_flags[__tvsymbol]["instance"] = None
            return {
                "success": True,
                "message": f"{__tvsymbol} service timed out",
                "symbol": __tvsymbol}

        # Close the Selenium session
        self.session_flags[__tvsymbol]["instance"].quit()

        # Set the flag for the market service to False
        self.session_flags[__tvsymbol]["status"] = False

        # Return the success status, message, and symbol
        return {
            "success": True,
            "message": f"{__tvsymbol} service stopped",
            "symbol": __tvsymbol,
        }

    def get_rsi(self, __tvsymbol):
        """
        Get the RSI (Relative Strength Index) values for a given TradingView symbol.

        Args:
            __tvsymbol (str): The TradingView symbol for which to fetch the RSI values.

        Returns:
            dict: A dictionary containing the success status, message, symbol, RSI values, and prices.
                - success (bool): True if the RSI values were fetched successfully, False otherwise.
                - message (str): A message indicating the status of the RSI fetch operation.
                - datetime (str): The current date and time in the format "%Y-%m-%d %H:%M:%S".
                - symbol (str): The TradingView symbol for which the RSI values were fetched.
                - rsi (float): The RSI value.
                - rsi_ma (float): The Moving Average of the RSI value.
                - prices (dict): A dictionary containing the open, high, low, and close prices.
                    - open (float): The open price.
                    - high (float): The high price.
                    - low (float): The low price.
                    - close (float): The close price.
        """
        # Check if the given TV symbol is in the database
        if __tvsymbol not in self.session_flags:
            return {
                "success": False,
                "message": f"{__tvsymbol} not found in database",
                "symbol": __tvsymbol}

        # Check if the market service for the given TV symbol is already started
        if not self.session_flags[__tvsymbol]['status']:
            return {
                "success": False,
                "message": f"{__tvsymbol} not running",
                "symbol": __tvsymbol}

        try:
            # Check if the Selenium session is still active by trying to find the time zone menu button
            self.find(
                __tvsymbol,
                '//button[@data-name="time-zone-menu"]'
            )
        except sel_exc.InvalidSessionIdException:
            print("Selenium session timed out.\n Creating new session...")
            # If the session is not active, restart the session
            self.session_flags[__tvsymbol]["status"] = False
            self.session_flags[__tvsymbol]["instance"] = None
            self.start_market_service(__tvsymbol)

        print("Getting RSI...")

        # Get the raw prices values from the TradingView session
        self.raw_prices = self.find(
            __tvsymbol,
            '//div[@data-name="legend-series-item"]').text

        # Format the raw prices values in open, high, low, close float values
        self.prices = [float(value) for value in re.findall(
            '\d+\.\d+', self.raw_prices) if float(value) > 10]

        # Get the RSI value from the TradingView session
        self.raw_rsi = self.find(
            __tvsymbol,
            '//div[@data-name="legend-source-item"]',
            multiple=True)

        # Filter the list for elements that contain the 'RSI' words
        self.raw_rsis = [e for e in self.raw_rsi if 'RSI' in e.text][0].text

        # Extract the RSI values (RSI and Moving Avg) from text
        self.rsi_values = [float(value) for value in re.findall(
            '\d+\.\d+', self.raw_rsis)]

        # Return the success status, message, symbol, RSI values, and prices
        return {
            "success": True,
            "message": f"RSI for {__tvsymbol} fetched",
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": __tvsymbol,
            "rsi": self.rsi_values[0],
            "rsi_ma": self.rsi_values[1],
            "prices":
                {
                "open": self.prices[0],
                "high": self.prices[1],
                "low": self.prices[2],
                "close": self.prices[3]
            }
        }
