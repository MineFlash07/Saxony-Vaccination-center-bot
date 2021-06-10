from dotenv import load_dotenv
import os
from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException


class WebBot:

    def __init__(self, driver_path: str, code: str, password: str):
        # Setup driver
        self._driver = webdriver.Chrome(driver_path)
        self._driver.maximize_window()
        # Open web page and login
        self._driver.get("https://sachsen.impfterminvergabe.de/")
        self._driver.get(self._driver.find_element_by_xpath(
            "/html/body/div[3]/div/main/div/div[2]/div[3]/div/div[4]/a[2]").get_attribute("href"))

        # Check if login is available
        while True:
            try:
                data_element = self._driver.find_element_by_xpath(
                    "/html/body/div[3]/div/main/div/div[2]/div[3]/div[2]/div/div[1]/div/div/h3")
                if data_element.text == "Zugangsdaten":
                    break
            except NoSuchElementException:
                pass

        # Login
        self._driver.find_element_by_xpath(
            "/html/body/div[3]/div/main/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div/div/div/input").send_keys(
            code)
        self._driver.find_element_by_xpath(
            "/html/body/div[3]/div/main/div/div[2]/div[3]/div[2]/div/div[2]/div/div[3]/div/div/div/input").send_keys(
            password)
        self._driver.find_element_by_xpath("/html/body/div[3]/div/main/div/div[2]/div[4]/button").click()

        # Check failed login
        time.sleep(3)
        try:
            if "Ihre Zugangsdaten sind nicht korrekt. Bitte überprüfen Sie Ihre Eingabe." in self._driver.find_element_by_xpath("/html/body/div[3]/div/main/div/div[2]/div[3]/div/div").text:
                print("Wrong login information")
                self._driver.close()
                return
        except NoSuchElementException:
            pass

        while True:
            pass


class BotLauncher:

    def __init__(self):
        self._driver_path = os.getenv("WEB_BOT_DRIVER_PATH")
        self._center_code = os.getenv("LOGIN_CODE")
        self._center_password = os.getenv("LOGIN_PASSWORD")

    def launch(self):
        WebBot(self._driver_path, self._center_code, self._center_password)


def main():
    load_dotenv()
    BotLauncher().launch()


if __name__ == "__main__":
    main()
