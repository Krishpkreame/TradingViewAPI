# Environment variables and datetime
import os
import time
# For web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
# For waiting for web elements to load instead of time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class API:
    # Initialize class variables and environment variables
    def __init__(self, __keywords=None):
        self.__account_name = "Quality Kiwi Shop Ltd"
        self.tv_started = False  # Flag to check if Trading View is running
        # Get Selenium URL from environment variable
        self.selenium_url = os.environ.get("SELENIUM_URL", "")

        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_argument("--start-maximized")
        self.cmc_url = "file:///docker/selenium/asx200.html"

    def wait_for_element(self, xpath_str, seconds=60):
        try:
            # Wait for the element to load (default timeout is 60 seconds)
            WebDriverWait(self.cmc, seconds).until(
                EC.presence_of_element_located((By.XPATH, xpath_str)))
            self.cmc.implicitly_wait(3)
            return True
        except Exception as e:  # If the element does not load, catch exception
            print(e)
            return False

    def start_service(self):  # Start CMC Markets
        if not self.cmc_started:  # If CMC is not running, start it
            print(" service started.")
            self.cmc_started = True

            # Start the browser
            self.cmc = webdriver.Remote(
                command_executor=self.selenium_url,
                options=self.browser_options)
            # Go to the CMC Markets login page
            self.cmc.get(self.cmc_url)
            # Wait for the page to load and zooming out
            self.cmc.execute_script("document.body.style.zoom='50%'")
            # Wait for the login page to load
            if self.wait_for_element('//*[@id="username"]'):
                print("Login page loaded.\n--- waiting for selection...")
            else:
                raise Exception("CMC login page failed to load.")

            # Login to CMC Markets
            self.type_element('//*[@id="username"]', self.username)
            self.type_element('//*[@id="password"]', self.password)

            # Click login button
            self.click_element("""
                /html/body/div[1]/div/cmc-login/div/section/div[1]/div[1]/form/div[4]/input
                """)

            try:
                # Wait for the account select page to load
                if self.wait_for_element("""
                    /html/body/div[1]/div/div/div/div/section/cmc-account-options/div/div[3]/div[1]/button[2]
                    """, seconds=25):
                    print("CMC account tab switch needed.")
                else:
                    raise TimeoutError
                # Select the account
                self.click_element("""
                    /html/body/div[1]/div/div/div/div/section/cmc-account-options/div/div[3]/div[1]/button[2]
                    """)
            except TimeoutError:
                print("CMC account tab switch not needed.")
                pass

            self.cmc.implicitly_wait(15)

            # Sometimes CMC asks for account selection, if needed select the account otherwise, wait for 20 second timeout
            try:
                # Wait for the account select page to load
                span_list = self.cmc.find_elements(By.TAG_NAME, "span")
                for span in span_list:
                    if self.__account_name in span.text:
                        span.click()
                        print("CMC account selection and account selected")
                        raise ValueError
                raise TimeoutError("Account not found")
            except ValueError:
                pass

            # if not wait and try again
            for time_ran in range(10):
                if self.cmc_loggedin == True:  # If the flag is already True, break the loop
                    break
                # Wait for the main page to load (cant use wait_for_element because the elements are unique)
                time.sleep(30)
                if len(self.cmc.find_elements(By.CLASS_NAME, 'news-list-item')) > 399:
                    print("The main page news loaded.")
                    self.cmc_loggedin = True  # Set the flag to True
                else:
                    print(
                        "The main page news failed to load, trying again. attempt: " + str(time_ran))
            if not self.cmc_loggedin:
                raise Exception("CMC News failed to load in.")
        else:
            # Raise exception if CMC is already running
            raise Exception("CMC News service is already running.")

    def stop_service(self):
        if self.cmc_started:  # If CMC is running, stop it
            try:
                self.cmc.quit()  # Close the browser
                self.cmc_started = False  # Set the flag to False
            except Exception as e:
                print(e)
        else:  # If CMC is not running, raise exception
            raise Exception("CMC News service is not running.")
