import csv # Za obradu CSV datoteka
import cyrtranslit # Za transliteraciju ćirilice u latinicu za potrebe imena
import re # Za obradu imena tj. uklanjanje suvišnih reči


def ucitaj_elo_debatera(ime_datoteke:str,alt_mod:bool=False)->dict[str,(float,int)]:
    '''Funkcija učitava ELO rejtinge debatera iz datoteke.
    Očekivani ulaz je CSV sa jednim razmakom između kolona, strukture:
    ime prezime ELO broj_dosadasnjih_debata
    Vraća rečnik čiji su ključevi imena debatera, a vrednosti su
    uređeni par (ELO rejting,broj dosadašnjih debata).'''
    elo_debateri = {} # Definiše prazan rečnik
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter=' ')
        for red in citac:
            if alt_mod:
                ime_debatera = ocisti_ime(red[0]+' '+red[1])
                elo_debateri[ime_debatera] = (float(red[2]),int(red[3]))
            else:
                ime_debatera = ocisti_ime(red[0])
                elo_debateri[ime_debatera] = (float(red[1]),int(red[2]))
    return elo_debateri

def ocisti_ime(ime:str)->str:
    '''Funckija čisti ime kako bi Nikola Nikolić i Nikola nikolic i Никола Николић  bili ista osoba.'''
    ime = ime.lower()
    ime = ime.strip() # Ukloni razmake na početku i kraju
    ime = cyrtranslit.to_latin(ime, 'sr') # Transliteracija ćirilice u latinicu
    ime = ime.replace('č', 'c')
    ime = ime.replace('š', 's')
    ime = ime.replace('ž', 'z')
    ime = ime.replace('ć', 'c')
    ime = ime.replace('đ', 'd')
    ime = re.sub(r' .+? ', ' ', ime) # Uklanja sve između imena i prezimena
    return ime

def ucitaj_timove_ucesnike(ime_datoteke:str,spiker_csv_mod:bool=False,ignorisi_1:bool=True)->dict[str,str]:
    '''Funkcija učitava imena timova i njegovih učesnika iz datoteke.
   Vraća rečnik čiji su ključevi "očišćena" imena debatera, a vrednosti izvorna imena timova.'''
    govornici_timovi = {}
    prvi_red = True
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t') # delimeter='\t' usled toga što je tab podrazumevani delilac kad se kopira sa Taba
        for red in citac:
            if ignorisi_1==False or prvi_red==False:
                if spiker_csv_mod:
                    ime_ucesnika = ocisti_ime(red[1])
                    govornici_timovi[ime_ucesnika]=red
                else:
                    ime_ucesnika = ocisti_ime(red[1])
                    govornici_timovi[ime_ucesnika]=red[3]
            prvi_red=False
    #print(f'????{govornici_timovi}????')
    return govornici_timovi

def ucitaj_rang_timova(ime_datoteke:str,ignorisi_1:bool=True,alt_instit:bool=False)->dict[str,int]:
    '''Čita rangove time iz datoteke sa imenom tima i njegovim mestom.
    Vraća rečnik čiji su ključevi imena timova, a vrednosti mesta.'''
    timovi_pozicije = {}
    prvi_red = True
    lokacija = 2
    if alt_instit:
        lokacija = 1
    with open(ime_datoteke, newline='\n',encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t')
        for red in citac:
            if ignorisi_1==False or prvi_red==False:
                timovi_pozicije[red[0]]=desifruj_rang(red[lokacija])
            prvi_red=False
    return timovi_pozicije

def desifruj_rang(rang:str)->int:
    ''' Pretvara rang u broj. Primer: '1st' u 1'''
    if rang == '1st':
        return 1
    elif rang == '2nd':
        return 2
    elif rang == '3rd':
        return 3
    elif rang == '4th':
        return 4 
    
def ucitaj_debate(ime_datoteke:str,ignorisi_1:bool=True)->list[set[str]]:
    '''Funkcija učitava debate iz datoteke.
    Vraća listu skupova, gde je svaki skup skup timova učesnika u debati.'''
    debate_timovi = []
    prvi_red=True
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t')
        for red in citac:
            if prvi_red==False or ignorisi_1==False:
                skup = set()
                skup.add(red[1])
                skup.add(red[2])
                skup.add(red[3])
                skup.add(red[4])
                debate_timovi.append(skup)
            prvi_red=False
    return debate_timovi

def izvezi_elo_debatera(elo_debatera:dict[str,(float,int)], ime_datoteke:str):
    '''Funkcija izvozi ELO rejtinge debatera u datoteku.
    Rečnik čiji su ključevi imena debatera, a vrednosti ELO rejting.'''
    with open(ime_datoteke, 'w', newline='\n', encoding='utf-8') as csvdat:
        pisac = csv.writer(csvdat, delimiter=' ')
        for ime, elo in elo_debatera.items():
            pisac.writerow([ime, elo[0], elo[1]])  # Upisujemo ime, ELO rejting i broj debata

def uvezi_spikere(ime_datoteke:str,broj_rundi:int=5,ignorisi_1:bool=True)->dict[str, (str, list[int],float)]:
    '''Funkcija koja iz fajla u učitava spikere debatera za sve preeliminarne runde.
    Vraća rečnik čiji su ključevi imena debatera, a vrednosti niske rezultata.'''
    spikeri = {}
    prvi_red=True
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t')
        for red in citac:
            if prvi_red==False or ignorisi_1==False:    
                try:
                    prosek = float(red[10])
                except ValueError:
                    prosek = 0.0
                lista = []
                for i in range(4, 4+broj_rundi):
                    try:
                        lista.append(int(red[i]))
                    except ValueError:
                        lista.append(0)
                spikeri[ocisti_ime(red[1])] = (red[3],lista, prosek)  # Uzimamo imena i njihove rezultate
            prvi_red=False
        return spikeri
    
def dodaj_debatere(elo_debateri:dict[str,(float,int)], ime_datoteke:str, ignorisi_1:bool=True):
    '''Funkcija dodaje debatere koji nisu na ELO listi u rečnik elo_debateri.
    Učitava podatke iz datoteke sa imenom tima i njegovim mestom.'''
    prvi_red=True
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t')
        for red in citac:
            if prvi_red==False or ignorisi_1 == False:
                if ocisti_ime(red[1]) not in elo_debateri.keys():
                    elo_debateri[ocisti_ime(red[1])]=(1000,0)  # Ako debater nije na listi, dodeljujemo mu početni ELO rejting i broj debata
            prvi_red=False