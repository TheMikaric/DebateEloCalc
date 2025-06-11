from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip

def ucitaj_govornike_tekst(driver,url:str):
    '''Funkcija otvara jezicak sa govornicima i kopira podatke.'''
    driver.get(f'{url}/tab/speaker/')
    time.sleep(10)  # Čekamo da se stranica učita, možete koristiti WebDriverWait za bolje upravljanje čekanjem
    csvdugme = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvdugme.click()
    return pyperclip.paste()

def ucitaj_timove_rankove_tekst(driver,url:str,runda:str):
    '''Funkcija otvara jezicak sa timovima i kopira podatke o rankovima, ali ne i o tome
    koji timovi su debatovali jedni protiv drugih.'''
    driver.get(f'{url}/results/round/{runda}/?view=team')
    time.sleep(10)
    csvdugme = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvdugme.click()
    return pyperclip.paste()

def ucitaj_timove_debate_tekst(driver,url:str,runda:str):
    '''Funkcija otvara jezicak sa timovima i kopira podatke o debatama, ali ne i o rankovima.'''
    driver.get(f'{url}/results/round/{runda}/?view=debate')
    time.sleep(10)
    csvdugme = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvdugme.click()
    return pyperclip.paste()

def izvezi_fajl(ime_datoteke:str, sadrzaj:str):
    '''Funkcija za izvoz podataka u csv fajl.'''
    with open(ime_datoteke, 'w', encoding='utf-8') as f:
        f.write(sadrzaj)

def skini_ceo_turnir(url:str,br_rundi:int=5):
    '''Skida podatke sa celog turnira u formati koji Tabbycat daje kada se klikne na CSV dugme.
    Prikupljene podatke zapisuje u CSV fajlove.'''
    driver = webdriver.Chrome()
    timovi_rankovi = []
    timovi_debate = []
    govornici = ucitaj_govornike_tekst(driver,url)
    for i in range(1, br_rundi+1):
        timovi_rankovi = ucitaj_timove_rankove_tekst(driver,url,str(i))
        timovi_debate = ucitaj_timove_debate_tekst(driver,url,str(i))  # Učitajte debate za prvu rundu, možete promeniti runda po potrebi
        izvezi_fajl(f'timovi_rankovi_runda_{i}.csv', timovi_rankovi)
        izvezi_fajl(f'timovi_debate_runda_{i}.csv', timovi_debate)
    izvezi_fajl('govornici.csv', govornici)
    

    driver.quit()