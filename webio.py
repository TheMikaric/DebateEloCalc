from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip

def go_to_tournament_website(driver,url:str):
    """Funkcija otvara veb stranicu turnira koristeći Selenium."""
    driver.get(url)
    time.sleep(3)
    return driver

def ucitaj_govornike_tekst(driver,url:str):
    '''Funkcija otvara jezicak sa govornicima i kopira podatke.'''
    driver.get(f'{url}/tab/speaker/')
    time.sleep(10)  # Čekamo da se stranica učita, možete koristiti WebDriverWait za bolje upravljanje čekanjem
    csvdugme = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvdugme.click()
    return pyperclip.paste()

def ucitaj_timove_rankove_tekst(driver,url:str,runda:str):
    driver.get(f'{url}/results/round/{runda}/?view=team')
    time.sleep(10)
    csvdugme = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvdugme.click()
    return pyperclip.paste()

def ucitaj_timove_debate_tekst(driver,url:str,runda:str):
    driver.get(f'{url}/results/round/{runda}/?view=debate')
    time.sleep(10)
    csvdugme = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvdugme.click()
    return pyperclip.paste()

def scrape_whole_tournament(url:str,br_rundi:int=5):
    driver = webdriver.Chrome()
    timovi_rankovi = []
    timovi_debate = []
    govornici = ucitaj_govornike_tekst(driver,url)
    for i in range(1, br_rundi):
        timovi_rankovi = ucitaj_timove_rankove_tekst(driver,url,str(i+1))
        timovi_debate = ucitaj_timove_debate_tekst(driver,url,str(i+1))  # Učitajte debate za prvu rundu, možete promeniti runda po potrebi
    print(timovi_rankovi)
    print(timovi_debate)
    print(govornici)

    driver.quit()