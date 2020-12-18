# Connect and launch
# written by https://github.com/Mekolaos
# not quite a fork because im using it inside my bot
# edited 12/15/2020

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
import asyncio
import time
import json

# load the credentials and links from a json file
creds_path = 'server_credentials.json'
try:
    with open(creds_path, 'r') as fp:
        creds = json.load(fp)
except:
    print('Credentials file not found')
    quit()

URL = "https://aternos.org/go/"
USER = creds["username"]
PASSWORD = creds["password"]

connected = False

options = webdriver.ChromeOptions()

# uncomment these to test on windows
#from chromedriver_py import binary_path
#driver = webdriver.Chrome(options=options, executable_path=binary_path)

# uncomment this to run on rpi
options.add_argument('headless')
driver = webdriver.Chrome(options=options)


async def start_server():
    """ Starts the server by clicking on the start button.
        The try except part tries to find the confirmation button, and if it
        doesn't, it continues to loop until the confirm button is clicked."""
    element = driver.find_element_by_xpath("//*[@id=\"start\"]")
    element.click()
    await asyncio.sleep(3)
    # hides the notification question
    driver.execute_script('hideAlert();')
    # server state span
    state = driver.find_element_by_xpath('//*[@id="nope"]/main/section/div[3]'
                                         '/div[3]/div[1]/div/span[2]/span')
    while state.text == "Waiting in queue":
        # while in queue, check for the confirm button and try click it
        await asyncio.sleep(3)
        state = driver.find_element_by_xpath('//*[@id="nope"]/main/section/'
                                             'div[3]/div[3]/div[1]/div/span[2]'
                                             '/span')
        try:
            element = driver.find_element_by_xpath('//*[@id="confirm"]')
            element.click()
        except ElementNotInteractableException:
            pass
    print("Server Started")


def get_status():
    """ Returns the status of the server as a string."""
    element = driver.find_element_by_xpath('//*[@id="nope"]/main/section/'
                                           'div[3]/div[3]/div[1]/div/span[2]'
                                           '/span')
    return element.text


def get_number_of_players():
    """ Returns the number of players as a string."""
    element = driver.find_element_by_xpath('//*[@id="players"]')
    return element.text


def get_server_info():
    """ Returns a string of information about the server
        Returns: server_ip, server_status, number of players, software,
        version"""
    server_ip = driver.find_element_by_xpath('//*[@id="nope"]/main/section/'
                                             'div[3]/div[1]').text[:-8]
    software = driver.find_element_by_xpath('//*[@id="software"]').text
    version = driver.find_element_by_xpath('//*[@id="version"]').text

    return server_ip, get_status(), get_number_of_players(), software, version


def connect_account():
    """ Connects to the accounts through a headless chrome tab so we don't
        have to do it every time we want to start or stop the server."""

    driver.get(URL)
    # login to aternos
    element = driver.find_element_by_xpath('//*[@id="user"]')
    element.send_keys(USER)
    element = driver.find_element_by_xpath('//*[@id="password"]')
    element.send_keys(PASSWORD)
    element = driver.find_element_by_xpath('//*[@id="login"]')
    element.click()
    time.sleep(2)

    # selects server from server list
    element = driver.find_element_by_css_selector('body > div > main > section'
                                                  '> div > div.servers.single '
                                                  '> div > div.server-body')
    element.click()


async def stop_server():
    """ Stops server from aternos panel."""
    element = driver.find_element_by_xpath("//*[@id=\"stop\"]")
    iterations = 0
    
    while iterations < 5:
        try:
            element.click()
            break
        except ElementNotInteractableException:
            print("interactable exception")
            time.sleep(2)
            driver.execute_script('hideAlert()')
            iterations += 1
            continue
        except ElementClickInterceptedException:
            print("intercepted exception")
            driver.execute_script('hideAlert()')
            time.sleep(2)
            iterations += 1
            continue
            
    print("Server Stopped")


def quitBrowser():
    """ Quits the browser driver cleanly."""
    driver.quit()
