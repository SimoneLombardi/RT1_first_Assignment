from __future__ import print_function
from readline import insert_text
from math import ceil

import time
import token
from sr.robot import *

import numpy
import array
import random
import math

R = Robot()

#-----------------------------------------funzioni native------------------------------------------------#

def drive(speed, seconds):
    """
    Function for setting a linear velocity

    Args: speed (int): the speed of the wheels
          seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def turn(speed, seconds):
    """
    Function for setting an angular velocity

    Args: speed (int): the speed of the wheels
          seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

    
#-----------------------------------------variabili globali ------------------------------------------#
"""Variabili globali utilizzate per le funzioni di movimento"""

MAXSPEED = 100
MSTIME = 0.05

SPEED = 80
TIME = 0.25

basespeed = 1
basetime = 1
#-----------------------------------------funzioni---------------------------------------------------#
def list_comparison(token_list, grabbed_token_list):
    """
    list_comparison: permette di valutare se tutti i token inseriti in token_list sono presenti anche in
                     grabbed_token_list e sapere se tutti i token sono stati mossi

    Args: token_list (list), tutti i codici dei token presenti nell'area di lavoro
          grabbed_token_list (list), codici dei token che sono già stati mossi
    """
    if len(token_list) != len(grabbed_token_list): 
        # se le due liste non hanno la stessa lunghezza c'è stato un errore, stampo messaggio ed esco dal programma
        print("errore liste lunghezza diversa")
        exit()
    
    controllo = 1
    #inizializzo una variabile di controllo per trovare eventuali elementi non uguali 
    for i in range(len(token_list)):
        # posso limitarmi ad un solo ciclo dato che per come ho creato le due liste se due token sono uguali si troveranno
        # al medesimo indice di due liste della stessa lunghezza
        if token_list[i] != grabbed_token_list[i]:
            controllo = 0

    # se la variabile ritornata è zero le due liste sono diverse
    return controllo


def get_token_info(token_code):
    """
    get_token_info: funzione che mi permette di recuperare le informazioni di distanza e rotazione rispetto al robot
                    per un token specifico con codice token_code

    Args: token_code (int), codice identificativo del token di cui mi interessano le informazioni
    """
    dist = ang = -100
    what_i_see = R.see()
    # faccio una scannerizzazione del campo visivo del robot

    for i in what_i_see:
        # guardando tutti gli elementi nel campo visivo se trovo un codice uguale a token_code salvo i suoi campi
        # distanza e rotazione 
        if i.info.code == token_code:
            dist = i.dist
            ang = i.rot_y
            break
    
    # nel caso il token non sia presente nel campo o la lista what_i_see sia vuota i valori ritornati saranno
    # quelli dell'inizializzazione, queste casistiche saranno gestite da altre funzioni
    return dist, ang
    

def get_ancor_tol(token_code):
    """
    get_ancot_tol: funzione che mi permette di valutare quanti token si trovano tra il token ancora e il robot
                   in modo da modificare la tolleranza per l'avvicinamento e evitare che il robot si scontri con
                   i token già posizionati
    
    Args: token_code (int), codice identificativo del token ancora             
    """
    what_i_see = R.see()

    in_between_token = 0

    ang_tol = 5
    dist_tol = 1
    # valori delle tolleranze per considerare un certo token x "davanti" al token ancora

    (dist, ang) = get_token_info(token_code)
    # utilizzo la funzione precedente per recuperare le informazioni del token ancora per 
    # valutare tutte le altre in relazione a queste

    for i in what_i_see:
        # se le differenze in distanza e angolazione sono minori delle tolleranze
        # aumento il conteggio in_between_token
        if  abs(i.rot_y - ang)<ang_tol and abs(i.dist - dist) < dist_tol:
            in_between_token = in_between_token + 1
    
    if in_between_token == 0:
        # dato che voglio utilizzare questo valore per incrementare una certa tolleranza tramite
        # moltiplicazione per per caso il valore dovesse essere nullo faccio in modo che invece sia 
        # sempre 1, non faccio questo passaggio in inizializzazione della variabile perchè voglio che 
        # il ciclo inizi da zero
        in_between_token = 1

    return in_between_token


def turn_parameters(ang):
    """
    turn_parameters: funzione che mi permette di calcolare il valore della velocità di rotazione più adatta
                     a completare l'aggiustamento dell'angolazione
    
    Args: ang (float), valore di rotazione rilevato per un certo token
    """
    sign_moltip = -1 # variabile utilizzata per modificare il verso di rotazione 
    TSPEED = TTIME = 1 # inizializzo le variabili Turn SPEED e Turn TIME

    if ang > 0 : # controllo direzione maggiore di zero -> DX, minore di zero -> SX
        TSPEED = ceil(abs((abs(ang)/3)-0.5))
        print("---> ang speed: ", TSPEED)
    else :
        TSPEED = ceil(abs((abs(ang)/3)-0.5)) * sign_moltip
        print("---> ang speed: ", TSPEED)

    """
    la formula utilizzata per calcolare la velocità di rotazione e trovata da prove sperimentali sulla rotazione del robot
    in genere un incremento di 1 sulla velocità per una rotazione di 1 sec risulta in un aumento di 3 gradi sulla rotazione
    turn(1, 1) --> 3 gradi
    turn(2, 1) --> 6 gradi
    ... ecc

    dividendo l'argomento (rotazione del token a cui mi sto avvicinando) trovo una buona approssimazione della migliore velocità
    per evitare l'overshooting ed il continuo rimbalzo tra due posizioni uguali.
    
    riduco inoltra la velocità trovata di un ulteriore 0.5 (anche questo valore viene da prove sperimentali) per essere ancora più 
    conservativo, concludo arrotondando il risultato all'intero superiore per poter inserire la velocità trovata nella funzione 
    turn(speed, time) e per evitare il soft lock nel caso la formula restituisca un valore nullo (data la presenza dei valori assoluti si 
    vede che il valore minimo possibile della formula abs((abs(ang)/3)-0.5) è un valore compreso tra 0 e 1)
    """

    return TSPEED, TTIME


def drive_parameters(dist):
    """
    drive_parameters: funzione che mi permette di calcolare il valore della velocità lineare più adatta
                      a completare l'aggiustamento della distanza
    
    Args: ang (float), valore di distanza rilevato per un certo token
    """
    DSPEED = 1
    DTIME = 0.7558
    lengthunit = 0.01
    # se il valore passato è maggiore di 100, la velocità passata al robot dalla funzione drive(spd, tm) 
    # è semplicemente 100.
    DSPEED = dist / lengthunit 
    print("------> drive speed: ", round(DSPEED, 2))
    if dist < 1: # se mi trovo molto vicino riduco ulteriormente il tempo di movimento
        DTIME = DTIME / 2

    """
    Dato che è necessario controllare tramite R.see() la distanza con i token ho riscontrato maggior successo a
    muovere il robot ad alte velocità per brevi periodi di tempo, in modo da poter controllare la distanza più frequentemente.
    I valori utilizzati di Drive TIME e lengthunit sono derivati da prove sperimentali per trovare una correlazione tra
    la velocità del robot e lo spazio percorso.
    """

    return DSPEED, DTIME
# passa i parametri per la velocità e tempo per i cicli di correzione per arrivare ai token

def create_token_list():
    """
    create_token_list: funzione che permette da qualsiasi posizione di creare una lista di tutti i codici dei token presenti
                       nell'area di lavoro, con una singola istanza per ogni codice

    Args: none
    """
    print("inizio generazione lista token...\n")
    temp_list = list(()) # inizializzo la lista con il costruttore per avere i metodi liste disponibili

    for i in range(7): 
        what_i_see = R.see() # scannerizzo il campo per vedere i token nel campo visivo

        for j in what_i_see:
            # per ogni token visto dalla R.see()
            if j.info.code in temp_list: # se il codice token è già presente in token_list non lo aggiung
                print("") 
            else: # se il codice trovato non è presente in token_list lo aggiungo in coda
                temp_list.append(j.info.code)
 
        if i != 6: # eseguo una rotazione in meno per tornare alla posizione iniziale
            turn(SPEED, TIME)
    
    print("lista token generata...\n")
    return temp_list

    
def set_ancor_token():
    """
    set_ancor_token: funzione che permetta di selezionare un token casuale come token ancora al quale portare gli altri
                     token presenti nell'area di lavoro

    Args: none
    """
    token_list = create_token_list()# richiamo della funzione create token list

    # prendo come ancora un token qualsiasi all'interno della lista token
    temp_index = random.randint(0, len(token_list)-1)
    ancor_token = token_list[temp_index] 

    return token_list, ancor_token
    

def create_grabbed_token_list(token, grabbed_token_list, token_list): 
    """
    create_grabbed_token_list: funzione che permette di creare la lista dei token che sono già stati portati nelle vicinanze
                               del token ancora
                            
    Args: token (int), codice del token da aggiungere alla lista
          grabbed_token_list (list), lista da modificare 
          token_list (list), lista dei token presenti nell'area di lavoro
    """
    if len(grabbed_token_list) == 0:# se la lista passata è vuota la inizializzo 
        grabbed_token_list = list(()) 
        for i in token_list: # insierisco tanti -1 quanti sono i token nell'area di lavoro
            grabbed_token_list.append(-1)
    
    index = token_list.index(token) # recupero l'indice delle elemento token nella lista token_list

    grabbed_token_list.pop(index) # elimino l'elemento temporaneo nella stessa posizione della grabbed_token_list
    grabbed_token_list.insert(index, token) # aggiungo il token che è stato mosso all'indice pari a quello di token_list

    return grabbed_token_list 

def find_movable_token(grabbed_token_list):
    """
    find_movable_token: restituisce il codice di un token che non si trova all'interno della lista dei token già mossi

    Args: grabbed_token_list (list), lista dei token già mossi
    """
    print("finding movable token...\n")
    avail_token = -1 # inizializzo il codice del token a -1 per un ciclo while


    while avail_token == -1:
        what_i_see = R.see()
        if len(what_i_see) == 0:
            # se non vedo è presente nessun token nella porzione visionata fai una rotazione
            turn(SPEED, TIME)
            
        else:
            for i in what_i_see:
                # se trovo dei token valuto se sono presenti all'interno della lista dei token mossi 
                # se almeno uno non lo è restituisco il codice e continuo
                if i.info.code not in grabbed_token_list:
                    avail_token = i.info.code
                    print("token found: ", avail_token)
                    return avail_token
                else:
                    continue
            
            turn(SPEED, TIME)

def go_to_token(token_code, ancorDistTol):
    """
    go_to_token: si avvicina al token con condice token_code entro una certa tolleranza

    Args: token_code (int), codice del token a cui avvicinarsi
          ancorDistTol (float), valore di tolleranza sulla distanza
    """
    print("getting to token: ", token_code)

    (dist, ang) = get_token_info(token_code) # prendo le varibili del token per la prima votla

    # definisco delle tolleranze per i cicli di correzione della rotazione e distanza
    ang_tol = 1
    if ancorDistTol == 0: 
        # in questo caso il token a cui mi voglio avvicinare non è l'ancora, quindi impongo una condizione
        # più stretta per poter eseguire il R.grab()    
        dist_tol = 0.5
    else:
        # calcolo quanti token ci sono tra l'ancora ed il robot, aggiorno la tolleranza sulla distanza
        token_avoidance = get_ancor_tol(token_code)
        dist_tol = ancorDistTol * token_avoidance

    print("TOLLERANCE:", dist_tol)

    angle_correction = -0.3 # per i primi 3 cicli non voglio aumentare la tolleranza

    while(abs(ang) > ang_tol+angle_correction): # ----------------------------------------------------------------
        print("---> ang corr: ", round(ang, 3))
        TSPEED, TTIME = turn_parameters(ang)# calcolo TSPEED, TTIME tramite la funzione
        turn(TSPEED, TTIME)
        (dist, ang) = get_token_info(token_code) # aggiorno parametri del token
        # volendo evitare un soft lock dove il robot "rimbalza" tra due distanze opposte senza riuscire ad andare sotto
        # la tolleranza, questa tolleranza viene lentamente incrementata con il numero di esecuzioni del ciclo
        angle_correction = angle_correction + 0.1

        
    while(dist > dist_tol): # --------------------------------------------------------------------
        # stessa logica del ciclo precendete, correzione della tolleranza non necessaria verra sempre soddisfatta eventualmente
        print("------> dist corr: ", round(dist, 3))
        DSPEED, DTIME = drive_parameters(dist)
        drive(DSPEED, DTIME)
        (dist, ang) = get_token_info(token_code)

    # release o grab a seconda del caso
    grab_status = 0
    if ancorDistTol != 0: 
        # se l'argomento ancorDistTol significa che stiamo INSEGUENDO il token ancora, quindi abbiamo in mano un token
        R.release()
    else:
        while grab_status == 0:
            # per evitare che il robot sia fermo e non riesca a eseguire R.grab() inserisco un ciclo di controllo e 
            # correzione, se grab() restituisce False eseguo una veloce correzione della posizione del robot
            temp = R.grab()
            if temp == True :
                grab_status = 1
            else:
                drive(MAXSPEED, MSTIME)


#-----------------------------------------definizione main-----------------------------------------------#

def main():
    (token_list, ancor) = set_ancor_token() # creo la lista token e il token ancora
    grabbed_token_list = [] # creo una lista vuota

    ancor = 43
    print("generated token list: ", token_list)
    print("choosen ancor: ", ancor)


    # aggiungo il token ancora alla lista dei token da non muovere e modifico la lista 
    grabbed_token_list = create_grabbed_token_list(ancor, grabbed_token_list, token_list) 
    print(grabbed_token_list)

    # definisco la tolleranza iniziale per la distanza dal token ancora
    ancorTol = 1

    #---------------------------------------------------------------------------------------------#
    # inizializzazione del problema terminata, da adesso finchè token_list != grabbed_token_list continuo a:
    # 1) cerca token, 2) controlla se devi spostarlo, 3) se si spostalo 3.1) aggiorna lista grabbed 4) ripeti 
    #                                                  3) se no vai al (4)

    # variabile di controllo per capire se ho mosso tutti i token
    CONTROL = 0
    while CONTROL == 0:
        # trovo un codice di token che posso spostare
        token_code = find_movable_token(grabbed_token_list) 
        
        # vado a prendere il token con codice token_code
        go_to_token(token_code, 0) # tolleranza a zero --> seguo token non ancor
        go_to_token(ancor, ancorTol) # tolleranza a ancorTol --> seguo ancora

        # correggo posizione per evitare scontri robot token
        drive(-SPEED, TIME*2) 

        # aggiorno la lista dei token grabbati
        grabbed_token_list = create_grabbed_token_list(token_code, grabbed_token_list, token_list)

        # aggiorno la variabile control 
        CONTROL = list_comparison(token_list, grabbed_token_list)
        if CONTROL == 0:
            print("KEEP GONIG...CONTROL = ", CONTROL)
        else:
            print(" NO MORE TOKEN...CONTROL = ", CONTROL)

#-----------------------------------------running--------------------------------------------------------#
main()
