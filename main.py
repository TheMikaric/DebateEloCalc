from operator import itemgetter # Za soritiranje liste listi po vrednosti u podlisti
import copy # Za pravljenje kopije rečnika
import csvio as csvio # Uvoz svih mojih funkcija iz csvio.py 
import webio as webio # Uvoz svih mojih funkcija iz webio.py
import datetime

verzija = 10

def generisi_parove_timova(timovi_rangovi:dict[str,int], debate_timovi:list[set[str]])->list[tuple[str,str]]:
    '''Generiše uređene parove timova na osnovu rangova.
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
        if len(pobednici_debateri)<2:
            pobednici_debateri.append("NEPOZNAT SINGLE SWING1")
        if len(gubitnici_debateri)<2:
            gubitnici_debateri.append("NEPOZNAT SINGLE SWING1")

        parovi_debatera.append((pobednici_debateri[0], gubitnici_debateri[0])) # Ubaci sve parove debatera na osnovu jednog para timova
        parovi_debatera.append((pobednici_debateri[1], gubitnici_debateri[1]))
        parovi_debatera.append((pobednici_debateri[0], gubitnici_debateri[1]))
        parovi_debatera.append((pobednici_debateri[1], gubitnici_debateri[0]))
        
    return parovi_debatera

def izracunaj_k_faktor(debater:tuple[float,int])->int:
    '''Funkcija vraća K-faktor za ELO rejting.
    K-faktor se menja u zavisnosti od iskustva debatera i njegovog rejtinga.'''
    osnovni_k = 30

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

def primeni_spiker_modifikator(debater:str, spikeri:dict[str, (str, list[int], float)], pobednik:bool, broj_runde:int)->float:
    '''Funkcija primenjuje modifikator spikera na ELO rejting debatera.
    Vraća modifikator koji se množi sa K-faktorom.'''
    
    if debater not in spikeri:
        return 1.0  # Ako debater nije na listi spikera, vraćamo 1.0 (bez modifikacije)

    delta_spikera = spikeri[debater][1][int(int(broj_runde)-1)] - spikeri[nadji_partnera(debater,spikeri)][1][int(int(broj_runde)-1)]  # Razlika između rezultata spikera i proseka
    
    if pobednik:
        if (1+(delta_spikera/10)) < 2 :
            if (1+(delta_spikera/10)) > 0 :
                return 1 + (delta_spikera/10)  # Ako je pobednik, vraćamo modifikator koji povećava ELO rejting
            else: return 0.1
        else: # Ako je pobednik ali je autspikovao za vise od 10, vracamo 2 jer ne zelimo da se precise poveca ELO
            return 2
    else:
        if 1+(delta_spikera/10) < 2:
            if (1+(delta_spikera/10)) > 0 :
                return 1 - (delta_spikera/10)  # Ako je gubitnik a autspikovao je vracamo manji faktor kako bi manje bio kaznjen
            else:
                return 2
        else: # Ako je pobednik ali je autspikovan za vise od 10, vracamo 0.1 jer ne zelimo da smanjujemo ELO za pobedu
            return 0.1        
    
def preracunaj_elo(parovi_debatera:list[tuple[str,str]], elo_debateri:dict[str,(float,int)],spikeri:dict[str, (str, list[int], float)], br_runde:int)->dict[str,(float,int)]:
    '''Funkcija računa novi ELO rejting na osnovu parova debatera.
    Vraća rečnik sa novim ELO rejtingom.'''
    novi_elo_debateri = copy.deepcopy(elo_debateri)  # Napravimo kopiju originalnog rečnika da ne bismo menjali original
    for par in parovi_debatera:
        pobednik = par[0]
        gubitnik = par[1]
        k_pobednika = 1
        k_gubitnika = 1
    
        if pobednik not in elo_debateri.keys():
            elo_pobednika = 1000  # Ako pobednik nije na listi, dodeljujemo mu početni ELO rejting
            k_pobednika = 0
        else:
            elo_pobednika = elo_debateri[pobednik][0]
            k_pobednika = izracunaj_k_faktor(elo_debateri[pobednik]) # K-faktor, menja se u zavisnosti od iskustva debatera i njegovog rejtinga

        if gubitnik not in elo_debateri.keys():
            elo_gubitnika = 1000  # Ako gubitnik nije na listi, dodeljujemo mu početni ELO rejting
            k_gubitnika = 0
        else: 
            elo_gubitnika = elo_debateri[gubitnik][0]
            k_gubitnika = izracunaj_k_faktor(elo_debateri[gubitnik])

        delta_pobednika = 1 - (1 / (1 + 10 ** ((elo_gubitnika - elo_pobednika) / 400))) # Očekivani rezultat pobednika
        delta_gubitnika = 1 - (1 / (1 + 10 ** ((elo_pobednika - elo_gubitnika) / 400)))
        
        delta_pobednika *= k_pobednika*primeni_spiker_modifikator(pobednik,spikeri,True,br_runde)
        delta_gubitnika *= k_gubitnika*primeni_spiker_modifikator(gubitnik,spikeri,False,br_runde)

        novo_elo_pobednika = elo_pobednika + delta_pobednika
        novo_elo_gubitnika = elo_gubitnika - delta_gubitnika
        if delta_gubitnika <= 0 or delta_pobednika <= 0:
            print(delta_pobednika)
            print(delta_gubitnika)
            print(pobednik)
            print(gubitnik)
            print(br_runde)
            print(" ")
        
        if pobednik in elo_debateri.keys():             
            novi_elo_debateri[pobednik]=(novo_elo_pobednika, elo_debateri[pobednik][1]+1) # Ažuriramo ELO rejting pobednika
        if gubitnik in elo_debateri.keys(): 
            novi_elo_debateri[gubitnik]=(novo_elo_gubitnika, elo_debateri[gubitnik][1]+1) # Ažuriramo ELO rejting gubitnika
    
    return novi_elo_debateri

def unesi_turnir(url:str,broj_rundi:int=5,
gov_fajl:str='govornici.csv',nov_elo_fajl:str='elo.csv')->None:
    '''Unosi sve rezultate sa turnira na datom linku, od početka do kraja'''
    verzija+=1
    elo_debateri = csvio.ucitaj_elo_debatera(nov_elo_fajl)
    webio.skini_ceo_turnir(url,broj_rundi)
    csvio.dodaj_debatere(elo_debateri,gov_fajl) # Dodaje debatere koji do sada nisu bili na ELO listi
    govornici_timovi = csvio.ucitaj_timove_ucesnike(gov_fajl,br_rundi=broj_rundi)
    spikeri= csvio.uvezi_spikere(gov_fajl,broj_rundi=broj_rundi)

    for i in range(1,broj_rundi+1):
        timovi_rangovi = csvio.ucitaj_rang_timova(f'timovi_rankovi_runda_{i}.csv',alt_instit=True)
        debate_timovi = csvio.ucitaj_debate(f'timovi_debate_runda_{i}.csv')
        parovi_timova = generisi_parove_timova(timovi_rangovi, debate_timovi)
        parovi_debatera = generisi_parove_debatera(parovi_timova,govornici_timovi)
        print(parovi_debatera)
        print(parovi_timova)
        elo_debateri=preracunaj_elo(parovi_debatera, elo_debateri,spikeri,i)
    csvio.izvezi_elo_debatera(elo_debateri, nov_elo_fajl)
    csvio.izvezi_elo_debatera(elo_debateri, f'nov_elo_fajl {verzija}.csv')

unesi_turnir('https://kampkusici2021.calicotab.com/kusici2021',broj_rundi=4)\
unesi_turnir('https://decembarac2021.calicotab.com/decembarac2021/',broj_rundi=5)