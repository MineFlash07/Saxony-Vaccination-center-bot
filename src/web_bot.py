import os
import sys
import time

from dotenv import load_dotenv
from playsound import playsound
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


class WebBot:

    def __init__(self, driver_path: str, code: str, password: str, town_codes: list):
        self._town_codes = {town_code: 0 for town_code in town_codes}
        # The current index of the town codes
        self._index = 0
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
        key_field = self._driver.find_element_by_xpath(
            "/html/body/div[3]/div/main/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div/div/div/input")
        for char in code:
            key_field.send_keys(char)

        password_field = self._driver.find_element_by_xpath(
            "/html/body/div[3]/div/main/div/div[2]/div[3]/div[2]/div/div[2]/div/div[3]/div/div/div/input")
        for char in password:
            password_field.send_keys(char)

        self._driver.find_element_by_xpath("/html/body/div[3]/div/main/div/div[2]/div[4]/button").click()

        # Check failed login
        time.sleep(5)
        try:
            if "Ihre Zugangsdaten sind nicht korrekt. Bitte überprüfen Sie Ihre Eingabe." in self._driver.\
                    find_element_by_xpath("/html/body/div[3]/div/main/div/div[2]/div[3]/div/div").text:
                self._close("Wrong login information")
        except NoSuchElementException:
            pass

        # Click choosing appointment
        self._driver.find_element_by_xpath(
            "/html/body/div[3]/div/main/div/div[2]/div[3]/div[2]/div/div/div/div/div/div/div/span[2]").click()
        self._driver.find_element_by_xpath("/html/body/div[3]/div/main/div/div[2]/div[4]/button[2]").click()

    def _close(self, close_message: str, exit_code=1):
        print(close_message)
        self._driver.quit()
        sys.exit(exit_code)

    def start_appointment_searching(self):
        try:
            self._search_for_appointment()
        except KeyboardInterrupt:
            pass

        # Print stats
        for town, tries in self._town_codes.items():
            print(f"Tries for {town}: {tries}")
        print(f"Amount of all tries: {sum(self._town_codes.values())}")

        self._close("Finished searching", 0)

    def _search_for_appointment(self):
        # Select town
        town = list(self._town_codes.keys())[self._index]
        self._town_codes[town] = self._town_codes[town] + 1

        # Search for select element
        while True:
            try:
                select_element = self._driver.find_element_by_xpath(
                    "/html/body/div[3]/div/main/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div/div"
                    "/div/span[2]/span[1]/span")
                break
            except NoSuchElementException:
                pass
        # Execute the selection
        select_element.click()
        town_element_to_select = None
        for town_element in self._driver.find_elements_by_tag_name("li"):
            if town not in town_element.get_attribute("data-select2-id"):
                continue
            town_element_to_select = town_element
            break

        if town_element_to_select is None:
            self._close("Found invalid town code")

        ActionChains(self._driver).move_to_element(town_element_to_select).perform()
        town_element_to_select.click()

        try:
            pass
            # select_element.select_by_value(town)
        except NoSuchElementException:
            self._close("Found invalid town code")

        # Click button
        self._driver.find_element_by_xpath("/html/body/div[3]/div/main/div/div[2]/div[4]/button[2]").click()

        # Check if it worked or now waiting few seconds for loading
        time.sleep(5)
        try:
            if "Aufgrund der aktuellen Auslastung der Impfzentren und der verfügbaren Impfstoffmenge können wir Ihnen "\
               "leider keinen Termin anbieten. Bitte versuchen Sie es in ein paar Tagen erneut." not in \
                    self._driver.find_element_by_xpath("/html/body/div[3]/div/main/div/div[2]/div[3]/div/div").text:
                self._announce_available()
                return
        except NoSuchElementException:
            self._announce_available()
            return

        # Go back
        self._driver.find_element_by_xpath("/html/body/div[3]/div/main/div/div[2]/div[4]/button").click()

        # Update town index
        self._index += 1
        if self._index >= len(self._town_codes):
            self._index = 0

        self._search_for_appointment()

    @staticmethod
    def _announce_available():
        playsound("./sounds/success.mp3")
        print("------\nAppointment Found\n------")
        # Infinite loop to let the user interact with the platform can be stopped in key Interrupt
        while True:
            pass


class BotLauncher:

    def __init__(self):
        self._driver_path = os.getenv("WEB_BOT_DRIVER_PATH")
        self._center_code = os.getenv("LOGIN_CODE")
        self._center_password = os.getenv("LOGIN_PASSWORD")
        self._town_codes = os.getenv("TOWN_CODES").split(",")

    def launch(self):
        WebBot(self._driver_path, self._center_code, self._center_password, self._town_codes).start_appointment_searching()


def main():
    load_dotenv()
    BotLauncher().launch()


if __name__ == "__main__":
    main()
