from __future__ import print_function
from readline import insert_text

import time
import token
from sr.robot import *

import numpy
import array

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

#-----------------------------------------funzioni mie---------------------------------------------------#
def create_token_list(token_list):

    for i in range(7):
        what_i_see = R.see() 

        for j in what_i_see:
            token_list.append(j.info.code)

        turn(80, 0.213)    

    print("not unique", token_list)  
    token_list.append(38)
    temp_array = numpy.unique(token_list)

    token_list = temp_array.tolist()
    print("unique ", token_list)
    
    return token_list
            
def set_ancor_token(): # -------------------------------------------

    choosen_ancor = -1

    while choosen_ancor == -1:
        what_i_see = R.see()
        if len(what_i_see) == 0:
            choosen_ancor = -1
            turn(80, 0.213)
        else:
            choosen_ancor = what_i_see[0].info.code
        

    return choosen_ancor

def go_to_token(token_to_grab): # -------------------------------------------
    dist = 0
    ang = 0

    for i in what_i_see:
        what_i_see = R.see()
        print("cosa vedo: ", i.info.code)
        if i.info.code == token_to_grab:
            dist = i.dist
            ang = i.rot_y

        turn(80, 0.213)

    print("start dist: ", dist)
    print("start ang", ang)

    ang_tol = 1
    dist_tol = 0.5

    tspeed = 1
    speed = 100

    time = 0.5
    ttime = 1

    while(abs(ang) > ang_tol):
        what_i_see = R.see()
        for i in what_i_see:
            if i.info.code == token_to_grab:
                ang = i.rot_y
        

        turn(numpy.sign(ang)*tspeed, ttime)
        print("angolo: ", ang)
        
    while(dist > dist_tol):
        what_i_see = R.see()
        for i in what_i_see:
            if i.info.code == token_to_grab:
                dist = i.dist
        
        drive(dist*speed, time)
        print("distanza: ", dist)
    
    R.grab()


def grab_token_and_back(ancor_token, token_list): # -------------------------------------------
    token_to_grab = token_list[0]
    print("token to grab: ", token_to_grab)

    found_token = -1

    while found_token != 1:
        print("start search for: ", token_to_grab)
        what_i_see = R.see()
        if len(what_i_see) == 0:
            found_token = -1
            turn(80, 0.213)
        else:
            print("lista non vuota...\n")
            for i in what_i_see:
                if i.info.code == token_to_grab:
                    found_token = 1
                    print("token trovato\n")
                    break
                else:
                    found_token = -1
        

    go_to_token(token_to_grab)
    go_to_token(ancor_token)
    R.release()

    
def update_token_list(token, token_list):
    token_list.remove(token)

    return token_list

#-----------------------------------------definizione main-----------------------------------------------#

def main():
    token_list = []

    token_list = create_token_list(token_list)
    print(token_list)

    ancor = set_ancor_token()
    print(ancor)

    update_token_list(ancor, token_list)

    grab_token_and_back(ancor, token_list)

    


#-----------------------------------------running--------------------------------------------------------#
main()
