import re
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# For MySQL database
import json
import pymysql

dbconf = json.loads(os.environ.get("MYSQL_DB1_JSON_CONN", ""))


def get_url(_cmckeyword):  # Get keywords from database
    # MySQL database setup
    connection = pymysql.connect(
        host=dbconf["host"], user=dbconf["user"],
        password=dbconf["password"], db=dbconf["database"],
        charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    # Get keywords from database
    with connection.cursor() as cursor:
        sql = f"SELECT * FROM `input_info` WHERE `cmc_keyword` = '{_cmckeyword}'"
        cursor.execute(sql)
        return [row for row in cursor][0]


time.sleep(1)

selenium_url = os.environ.get("SELENIUM_URL", "")

try:
    appinfo = get_url("S&P-ASX 200 ST")

    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--start-maximized")
    cmc = webdriver.Remote(
        command_executor=selenium_url,
        options=browser_options)

    cmc.get(appinfo["tv_link"])

    WebDriverWait(cmc, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@data-name="legend-source-item"]')))

    cmc.implicitly_wait(1)

    raw_time = cmc.find_element(
        By.XPATH, '//button[@data-name="time-zone-menu"]').text.split("\n")[-1]

    raw_rsi_value = cmc.find_element(
        By.XPATH, '//div[@data-name="legend-source-item"]').text.split("\n")[-1]

    raw_price_price = cmc.find_element(
        By.XPATH, '//div[@data-name="legend-series-item"]').text.split("\n")[-1]

    time_step1 = raw_time.split(" ")[0]
    time_step2 = datetime.strptime(time_step1, "%H:%M:%S").time()
    datetime_value = str(datetime.combine(datetime.now().date(), time_step2))

    rsi_value = float(raw_rsi_value)

    price_step1 = [float(value)
                   for value in re.findall('\d+\.\d+', raw_price_price)][0:4]

    price_values = {
        "open": price_step1[0],
        "high": price_step1[1],
        "low": price_step1[2],
        "close": price_step1[3]
    }

    time.sleep(1)

    final_data = {
        "cmc_name": appinfo["cmc_name"],
        "tv_symbol": appinfo["tv_symbol"],
        "datetime": datetime_value,
        "rsi": rsi_value,
        "price": price_values
    }

    print(final_data)

    time.sleep(1)
    cmc.quit()

except KeyboardInterrupt:
    cmc.quit()
