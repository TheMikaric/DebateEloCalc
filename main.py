# mydict.get("keyname")
# mydict["keyname"] = "value" adds new key value pair
# if "keyname" in mydict: check if key already exists

import csv # Za obradu CSV datoteka
import cyrtranslit # Za transliteraciju ćirilice u latinicu za potrebe imena
import re # Za obradu imena tj. uklanjanje suvišnih reči
from operator import itemgetter # Za soritiranje liste listi po vrednosti u podlisti
import copy # Za pravljenje kopije rečnika

def ucitaj_elo_debatera(ime_datoteke:str)->dict[str,(float,int)]:
    '''Funkcija učitava ELO rejtinge debatera iz datoteke.
    Očekivani ulaz je CSV sa jednim razmakom između kolona, strukture:
    ime prezime ELO broj_dosadasnjih_debata
    Vraća rečnik čiji su ključevi imena debatera, a vrednosti su
    uređeni par (ELO rejting,broj dosadašnjih debata).'''
    elo_debateri = {} # Definiše prazan rečnik
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter=' ')
        for red in citac:
            ime_debatera = ocisti_ime(red[0]+' '+red[1])
            elo_debateri[ime_debatera] = (float(red[2]),int(red[3]))
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
    #ime = ime.replace(' ', '')
    return ime

def ucitaj_timove_ucesnike(ime_datoteke:str)->dict[str,str]:
    '''Funkcija učitava imena timova i njegovih učesnika iz datoteke.
   Vraća rečnik čiji su ključevi imena debatera, a vrednosti imena timova.'''
    govornici_timovi = {}
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t')
        for red in citac:
            ime_ucesnika = ocisti_ime(red[0])
            govornici_timovi[ime_ucesnika]=red[2]
    return govornici_timovi

def ucitaj_rang_timova(ime_datoteke:str)->dict[str,int]:
    '''Čita rangove time iz datoteke sa imenom tima i njegovim mestom.
    Vraća rečnik čiji su ključevi imena timova, a vrednosti mesta.'''
    timovi_pozicije = {}
    with open(ime_datoteke, newline='\n',encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t')
        for red in citac:
            timovi_pozicije[red[0]]=desifruj_rang(red[1])
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

def ucitaj_debate(ime_datoteke:str)->list[set[str]]:
    '''Funkcija učitava debate iz datoteke.
    Vraća listu skupova, gde je svaki skup skup timova učesnika u debati.'''
    debate_timovi = []
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t')
        for red in citac:
            skup = set()
            skup.add(red[1])
            skup.add(red[2])
            skup.add(red[3])
            skup.add(red[4])
            debate_timovi.append(skup)
    return debate_timovi

def generisi_parove_timova(timovi_rangovi:dict[str,int], debate_timovi:list[set[str]])->list[tuple[str,str]]:
    '''Generiše parove timova na osnovu rangova.
    Primer od toga da je tim A prvi, B drugi, C treći i D četvrti:
    [A,B],[A,C],[A,D],[B,C],[B,D],[C,D]
    Prvi tim je pobedio drugi u svakom paru.'''

    parovi = []
    for debata in debate_timovi:
        rangovi = []
        for tim in debata:
            if tim not in timovi_rangovi:
                raise ValueError(f'Tim {tim} nije pronađen u rangovima.')
            else:
                rangovi.append([tim,timovi_rangovi[tim]])
        rangovi = sorted(rangovi, key=itemgetter(1))   

        for i in range(len(rangovi)):
            for j in range(i+1, len(rangovi)):
                parovi.append((rangovi[i][0], rangovi[j][0]))
    
    return parovi

def generisi_parove_debatera(parovi_timova:list[tuple[str,str]],govornici_timovi:dict[str,str])->list[tuple[str,str]]:
    '''
    Ulaz: 
        lista parova timova, uređena tako da je prvi tim pobednik, a drugi gubitnik.
        Rečnik čiji su ključevi imena debatera, a vrednosti imena timova.
    Izlaz:
        lista parova debatera, gde je prvi debater pobednik, a drugi gubitnik.
    '''
    parovi_debatera = []
    pobednici_debateri=[]
    gubitnici_debateri=[]

    for par in parovi_timova:
        pobednici_debateri = []
        gubitnici_debateri = []
        for govornik,tim in govornici_timovi.items():
            if tim == par[0]:
                pobednici_debateri.append(govornik)
            elif tim == par[1]:
                gubitnici_debateri.append(govornik)

        if not gubitnici_debateri: # Swingovi obično nisu na listi učesnika, za svaki slućaj
            gubitnici_debateri.append("NEPOZNAT SWING 1")
            gubitnici_debateri.append("NEPOZNAT SWING 2")
        if not pobednici_debateri:
            pobednici_debateri.append("NEPOZNAT SWING 1")
            pobednici_debateri.append("NEPOZNAT SWING 2")

        parovi_debatera.append((pobednici_debateri[0], gubitnici_debateri[0])) # Ubaci sve parove debatera na osnovu jednog para timova
        parovi_debatera.append((pobednici_debateri[1], gubitnici_debateri[1]))
        parovi_debatera.append((pobednici_debateri[0], gubitnici_debateri[1]))
        parovi_debatera.append((pobednici_debateri[1], gubitnici_debateri[0]))        

    return parovi_debatera

def izracunaj_k_faktor(debater:tuple[float,int])->int:
    '''Funkcija vraća K-faktor za ELO rejting.
    K-faktor se menja u zavisnosti od iskustva debatera i njegovog rejtinga.'''
    osnovni_k = 6

    if debater[0] > 1500:
        osnovni_k -= 2
    elif debater[0] > 1250:
        osnovni_k -= 1

    if debater[1] < 10:
        osnovni_k *= 2
    elif debater[1] < 20:
        osnovni_k *= 1.5

    return int(osnovni_k)

def nadji_partnera(debater:str, spikeri:dict[str, (str, list[int], float)])->str:
    '''Funkcija pronalazi partnera debatera u spikerima.
    Vraća ime partnera.'''
    for ime, podaci in spikeri.items():
        if debater == ime:  # Ako je debater spiker]
            tim_partnera = podaci[0]
    for ime, podaci in spikeri.items():
        if tim_partnera == podaci[0] and debater!=ime: # Ako je debater spiker]
            return ime
    return debater # Ako nema partnera, kao da debatuje sam

def primeni_spiker_modifikator(debater:str, spikeri:dict[str, (str, list[int], float)], pobednik:bool, broj_runde)->float:
    '''Funkcija primenjuje modifikator spikera na ELO rejting debatera.
    Vraća modifikator koji se množi sa K-faktorom.'''
    if debater not in spikeri:
        print(f"Upozorenje: Debater {debater} nije na listi spikera.")
        return 1.0  # Ako debater nije na listi spikera, vraćamo 1.0 (bez modifikacije)
    delta_spikera = spikeri[debater][1][broj_runde-1] - spikeri[nadji_partnera(debater,spikeri)][1][broj_runde-1]  # Razlika između rezultata spikera i proseka
    if pobednik:
        return 1 + (delta_spikera/10)
    else:
        return 1 - (delta_spikera/10)
    
def preracunaj_elo(parovi_debatera:list[tuple[str,str]], elo_debateri:dict[str,(float,int)],spikeri:dict[str, (str, list[int], float)])->dict[str,(float,int)]:
    '''Funkcija računa novi ELO rejting na osnovu parova debatera.
    Vraća rečnik sa novim ELO rejtingom.'''
    novi_elo_debateri = copy.deepcopy(elo_debateri)  # Napravimo kopiju originalnog rečnika da ne bismo menjali original
    for par in parovi_debatera:
        pobednik = par[0]
        gubitnik = par[1]
        if pobednik not in novi_elo_debateri.keys():
            elo_pobednika = 1000  # Ako pobednik nije na listi, dodeljujemo mu početni ELO rejting
            k_pobednika = 0
        else: 
            elo_pobednika = novi_elo_debateri[pobednik][0]
            k_pobednika = izracunaj_k_faktor(elo_debateri[pobednik]) # K-faktor, menja se u zavisnosti od iskustva debatera i njegovog rejtinga

        if gubitnik not in novi_elo_debateri.keys():
            elo_gubitnika = 1000  # Ako gubitnik nije na listi, dodeljujemo mu početni ELO rejting
            k_gubitnika = 0
        else: 
            elo_gubitnika = novi_elo_debateri[gubitnik][0]
            k_gubitnika = izracunaj_k_faktor(elo_debateri[gubitnik])

        delta_pobednika = 1 - (1 / (1 + 10 ** ((elo_gubitnika - elo_pobednika) / 400))) # Očekivani rezultat pobednika
        delta_gubitnika = 0 - (1 / (1 + 10 ** ((elo_pobednika - elo_gubitnika) / 400)))
        
        delta_pobednika *= k_pobednika*primeni_spiker_modifikator(pobednik,spikeri,True,1)
        delta_gubitnika *= k_gubitnika*primeni_spiker_modifikator(gubitnik,spikeri,False,1)

        novo_elo_pobednika = elo_pobednika + delta_pobednika
        novo_elo_gubitnika = elo_gubitnika + delta_gubitnika
 
        if pobednik in elo_debateri.keys():             
            novi_elo_debateri[pobednik]=(novo_elo_pobednika, elo_debateri[pobednik][1]+1) # Ažuriramo ELO rejting pobednika

        if gubitnik in elo_debateri.keys(): 
            novi_elo_debateri[gubitnik]=(novo_elo_gubitnika, elo_debateri[gubitnik][1]+1) # Ažuriramo ELO rejting gubitnika
    return novi_elo_debateri

def izvezi_elo_debatera(elo_debatera:dict[str,(float,int)], ime_datoteke:str):
    '''Funkcija izvozi ELO rejtinge debatera u datoteku.
    Rečnik čiji su ključevi imena debatera, a vrednosti ELO rejting.'''
    with open(ime_datoteke, 'w', newline='\n', encoding='utf-8') as csvdat:
        pisac = csv.writer(csvdat, delimiter=' ')
        for ime, elo in elo_debatera.items():
            pisac.writerow([ime, elo[0], elo[1]])  # Upisujemo ime, ELO rejting i broj debata

def uvezi_spikere(ime_datoteke:str)->dict[str, (str, list[int],float)]:
    '''Funkcija koja iz fajla u učitava spikere debatera za sve preeliminarne runde.
    Vraća rečnik čiji su ključevi imena debatera, a vrednosti niske rezultata.'''
    spikeri = {}
    with open(ime_datoteke, newline='\n', encoding='utf-8') as csvdat:
        citac = csv.reader(csvdat, delimiter='\t')
        for red in citac:
            try:
                prosek = float(red[10])
            except ValueError:
                prosek = 0.0
            lista = []
            for i in range(4, 9):
                try:
                    lista.append(int(red[i]))
                except ValueError:
                    lista.append(0)
            spikeri[ocisti_ime(red[1])] = (red[3],lista, prosek)  # Uzimamo imena i njihove rezultate
        return spikeri

elo_debateri = ucitaj_elo_debatera("proba4.csv")
govornici_timovi = ucitaj_timove_ucesnike("proba.csv")
timovi_rangovi = ucitaj_rang_timova("proba2.csv")
debate_timovi = ucitaj_debate("proba3.csv")
parovi_timova = generisi_parove_timova(timovi_rangovi, debate_timovi)
parovi_debatera = generisi_parove_debatera(parovi_timova,govornici_timovi)
spikeri=uvezi_spikere("proba5.csv")
print(spikeri)
elo_debateri=preracunaj_elo(parovi_debatera, elo_debateri,spikeri)
izvezi_elo_debatera(elo_debateri, "novi_elo.csv")
