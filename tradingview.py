import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions as sel_exc
import pymongo


class API:
    # Initialize class variables and environment variables
    def __init__(self):
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

    # Start market service for symbol

    def start_market_service(self, __tvsymbol):
        