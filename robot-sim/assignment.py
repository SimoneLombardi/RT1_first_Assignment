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


def find_token():
    """
    Function to find the closest token

    Returns:
        dist (float): distance of the closest token (-1 if no token is detected)
        rot_y (float): angle between the robot and the token (-1 if no token is detected)
    """
    dist = 100
    for token in R.see():
        if token.dist < dist:
            dist = token.dist
            rot_y = token.rot_y
    if dist == 100:
        return -1, -1
    else:
        return dist, rot_y
    
#-----------------------------------------variabili globali mie------------------------------------------#
MAXSPEED = 100
MSTIME = 0.05

SPEED = 80
TIME = 0.25

basespeed = 1
basetime = 1
#-----------------------------------------funzioni mie---------------------------------------------------#
def list_comparison(token_list, grabbed_token_list):
    if len(token_list) != len(grabbed_token_list):
        print("errore liste lunghezza diversa")
        exit()
    
    controllo = 1
    for i in range(len(token_list)):
        if token_list[i] != grabbed_token_list[i]:
            controllo = 0

    return controllo


def get_token_info(token_code):
    dist = ang = -100
    what_i_see = R.see()

    for i in what_i_see:
        if i.info.code == token_code:
            dist = i.dist
            ang = i.rot_y
            break
    
    return dist, ang
# passa le info posizione del token con codice token_code alla funzione chiamanta
    

def get_ancor_tol(token_code):
    what_i_see = R.see()

    in_between_token = 0

    ang_tol = 3
    dist_tol = 1

    (dist, ang) = get_token_info(token_code)

    for i in what_i_see:
        if  abs(i.rot_y - ang)<ang_tol and abs(i.dist - dist) < dist_tol:
            in_between_token = in_between_token + 1
    
    if in_between_token == 0:
        in_between_token = 1

    return in_between_token


def turn_parameters(ang):
    sign_moltip = -1
    TSPEED = TTIME = 1

    if ang > 0 :
        if ang < 2:
            TSPEED = 1
            print("---> ang speed: ", TSPEED)
        else:
            TSPEED = ceil(abs((abs(ang)/3)-0.5))
            print("---> ang speed: ", TSPEED)
    else :
        if ang > -2:
            TSPEED = 1 * sign_moltip
            print("---> ang speed: ", TSPEED)
        else:
            TSPEED = ceil(abs((abs(ang)/3)-0.5)) * sign_moltip
            print("---> ang speed: ", TSPEED)

    return TSPEED, TTIME


def drive_parameters(dist):
    DSPEED = 1
    DTIME = 0.7558

    DSPEED = dist / 0.01
    print("------> drive speed: ", round(DSPEED, 2))
    if dist < 1:
        DTIME = DTIME / 2

    return DSPEED, DTIME
# passa i parametri per la velocità e tempo per i cicli di correzione per arrivare ai token

def create_token_list():
    print("inizio generazione lista token...\n")
    temp_list = list(()) # inizializzo la lista con il costruttore

    for i in range(7):
        what_i_see = R.see() # scannerizzo il campo per vedere i token

        for j in what_i_see:
            
            if j.info.code in temp_list:
                print("") # se il codice è già stato trovato non lo aggiungo
            else:
                temp_list.append(j.info.code) # se trovo codice nuovo allora aggiungo in fondo
 
        if i != 6: # non faccio l'ultima rotazione per arrivare nella pos di partenza
            turn(SPEED, TIME)
    
    print("lista token generata...\n")
    return temp_list

    
def set_ancor_token():
    token_list = create_token_list()

    # prendo come ancora un token qualsiasi all'interno della lista token
    temp_index = random.randint(0, len(token_list)-1)
    ancor_token = token_list[temp_index] 

    return token_list, ancor_token
    

def create_grabbed_token_list(token, grabbed_token_list, token_list): # questa funzione crea e restituisce una lista dei token che non vanno più toccati
    if len(grabbed_token_list) == 0:
        grabbed_token_list = list(()) # se la lista è vuota la inizializzo come lista
        for i in token_list:
            grabbed_token_list.append(-1)
    
    index = token_list.index(token)

    grabbed_token_list.pop(index) # elimino l'elemento temporaneo all'indice x
    grabbed_token_list.insert(index, token) # aggiungo il token che è stato mosso all'indice pari a quello di token_list

    return grabbed_token_list # ritorno la lista modificata
# crea e aggiorna la lista dei token che sono stati mossi 

def find_movable_token(grabbed_token_list):
    print("finding movable token...\n")
    avail_token = -1 # inizializzo il codice del token a -1 per un ciclo while


    while avail_token == -1:
        what_i_see = R.see()
        if len(what_i_see) == 0:
            turn(SPEED, TIME)
            
        else:
            for i in what_i_see:
                if i.info.code not in grabbed_token_list:
                    avail_token = i.info.code
                    print("token found: ", avail_token)
                    return avail_token
                else:
                    continue
            
            turn(SPEED, TIME)
    # incremento cicli dopo ogni rotazione, vengono eseguite solo 1 volta per ciclo

# scannerizza l'arena per un token che non sia presente dentro la lista dei token che 
# sono già stati mossi e lo restituisce alla chiamante

def go_to_token(token_code, ancorDistTol):
    print("getting to token: ", token_code)

    (dist, ang) = get_token_info(token_code) # prendo le varibili del token per la prima votla

    # definisco delle tolleranze per i cicli della rotazione e distanza
    ang_tol = 1
    if ancorDistTol == 0:       
        dist_tol = 0.5
    else:
        token_avoidance = get_ancor_tol(token_code)
        dist_tol = ancorDistTol * token_avoidance

    print("TOLLERANCE:", dist_tol)

    angle_correction = -0.3 # per i primi 3 cicli non voglio aumentare la tolleranza

    while(abs(ang) > ang_tol+angle_correction): # ----------------------------------------------------------------
        print("ang corr: ", round(ang, 3))
        TSPEED, TTIME = turn_parameters(ang)
        turn(TSPEED, TTIME)
        (dist, ang) = get_token_info(token_code)
        angle_correction = angle_correction + 0.1

        
    while(dist > dist_tol): # --------------------------------------------------------------------
        print("dist corr: ", round(dist, 3))
        DSPEED, DTIME = drive_parameters(dist)
        drive(DSPEED, DTIME)
        (dist, ang) = get_token_info(token_code)

    grab_status = 0
    while grab_status == 0:
        temp = R.grab()
        if temp == True:
            grab_status = 1
        elif temp == False:
            drive(100, 0.01)
        else:
            R.release()
            grab_status = 1


# questa funzione mi permette di arrivare a qualsiasi token entro una tolleranza, se devo raggiungere 
# l'ancora la tolleranza della distanza devo passarla come parametro ed è maggiore 



#-----------------------------------------definizione main-----------------------------------------------#

def main():
    (token_list, ancor) = set_ancor_token() # creo la lista token e il token ancora
    grabbed_token_list = []

    print("generated token list: ", token_list)
    print("choosen ancor: ", ancor)

    # aggiungo il token ancora alla lista dei token da non muovere e modifico la lista 
    grabbed_token_list = create_grabbed_token_list(ancor, grabbed_token_list, token_list) 
    print(grabbed_token_list)

    ancorTol = 1

    #---------------------------------------------------------------------------------------------#
    # inizializzazione del problema terminata, da adesso finchè token_list != grabbed_token_list continuo a:
    # 1) cerca token, 2) controlla se devi spostarlo, 3) se si spostalo 3.1) aggiorna lista grabbed 4) ripeti 
    #                                                  3) se no vai al (4)


    CONTROL = 0
    while CONTROL == 0:
        # trovo un codice di token che posso spostare
        token_code = find_movable_token(grabbed_token_list) 
        
        # vado a prendere il token con codice token_code
        go_to_token(token_code, 0) # tolleranza a zero --> seguo token non ancor
        go_to_token(ancor, ancorTol) # tolleranza a ancorTol --> seguo ancora

        drive(-5, 1)

        # aggiorno la lista dei token grabbati
        grabbed_token_list = create_grabbed_token_list(token_code, grabbed_token_list, token_list)

        # aggiorno la variabile control 
        CONTROL = list_comparison(token_list, grabbed_token_list)
        if CONTROL == 0:
            print("KEEP GONIG...CONTROL = ", CONTROL)
        else:
            print(" NO MORE TOKEN...CONTROL = ", CONTROL)
'''
modifica 1) 
    aggiungo controllo su get token info per evitare che ritorni -100 -100 troppe volte

'''

#-----------------------------------------running--------------------------------------------------------#
main()
