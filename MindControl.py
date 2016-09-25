import sys
import os
import platform
import time
import ctypes
import numpy as np

from array import *
from ctypes import *
from __builtin__ import exit

try:
    if sys.platform.startswith('win32'):
        libEDK = cdll.LoadLibrary("../../bin/win32/edk.dll")
    elif sys.platform.startswith('linux'):
        srcDir = os.getcwd()
	if platform.machine().startswith('arm'):
            libPath = srcDir + "/../../bin/armhf/libedk.so"
	else:
            libPath = srcDir + "/../../bin/linux64/libedk.so"
        libEDK = CDLL(libPath)
    else:
        raise Exception('System not supported.')
except Exception as e:
    print 'Error: cannot load EDK lib:', e
    exit()

IEE_EmoEngineEventCreate = libEDK.IEE_EmoEngineEventCreate
IEE_EmoEngineEventCreate.restype = c_void_p
eEvent = IEE_EmoEngineEventCreate()

IEE_EmoEngineEventGetEmoState = libEDK.IEE_EmoEngineEventGetEmoState
IEE_EmoEngineEventGetEmoState.argtypes = [c_void_p, c_void_p]
IEE_EmoEngineEventGetEmoState.restype = c_int

IEE_EmoStateCreate = libEDK.IEE_EmoStateCreate
IEE_EmoStateCreate.restype = c_void_p
eState = IEE_EmoStateCreate()

userID = c_uint(0)
user   = pointer(userID)
ready  = 0
state  = c_int(0)

alphaValue     = c_double(0)
low_betaValue  = c_double(0)
high_betaValue = c_double(0)
gammaValue     = c_double(0)
thetaValue     = c_double(0)

alpha     = pointer(alphaValue)
low_beta  = pointer(low_betaValue)
high_beta = pointer(high_betaValue)
gamma     = pointer(gammaValue)
theta     = pointer(thetaValue)

channelList = array('I',[3, 7, 9, 12, 16])   # IED_AF3, IED_AF4, IED_T7, IED_T8, IED_Pz 

depth = 10
w, h = depth , 5

mtrx = [[0 for x in range(w)] for y in range(h)]

count = 0

avgtheta = 32
avgalpha = 11
avglbeta = 8
avghbeta = 4
avggamma = 2

avgtheta2 = 32
avgalpha2 = 11
avglbeta2 = 8
avghbeta2 = 4
avggamma2 = 2

def readtrain(direct):

    global avgtheta
    global avgalpha
    global avglbeta
    global avghbeta
    global avggamma

    global avgtheta2
    global avgalpha2
    global avglbeta2
    global avghbeta2
    global avggamma2

    if direct == 1:

        target = open("trainfileu.txt", "r")
        lines = target.readlines()

        avgtheta = lines[0].rstrip
        avgalpha = lines[1].rstrip
        avglbeta = lines[2].rstrip
        avghbeta = lines[3].rstrip
        avggamma = lines[4].rstrip

    elif direct == 0:

        target = open("trainfiled.txt", "r")
        lines = target.readlines()

        avgtheta2 = lines[0].rstrip
        avgalpha2 = lines[1].rstrip
        avglbeta2 = lines[2].rstrip
        avghbeta2 = lines[3].rstrip
        avggamma2 = lines[4].rstrip

    


    return

def logtrain(direct, the, alp, lbet, hbet, gam):

    if direct == 1:
        target = open("trainfileu.txt", "w")
    elif direct == 0:
        target = open("trainfiled.txt", "w")

    target.truncate

    target.write(the)
    target.write("\n")
    target.write(alp)
    target.write("\n")
    target.write(lbet)
    target.write("\n")
    target.write(hbet)
    target.write("\n")
    target.write(gam)

    target.close()
    return

def training(direct, the, alp, lbet, hbet, gam):

    while (1):
        state = libEDK.IEE_EngineGetNextEvent(eEvent)
        
        if state == 0:
            eventType = libEDK.IEE_EmoEngineEventGetType(eEvent)
            libEDK.IEE_EmoEngineEventGetUserId(eEvent, user)
            if eventType == 16:  # libEDK.IEE_Event_enum.IEE_UserAdded
                ready = 1
                libEDK.IEE_FFTSetWindowingType(userID, 1);  # 1: libEDK.IEE_WindowingTypes_enum.IEE_HAMMING
                print "User added"
                            
            if ready == 1:
                for i in channelList: 
                    result = c_int(0)
                    result = libEDK.IEE_GetAverageBandPowers(userID, i, theta, alpha, low_beta, high_beta, gamma)
                    
                    if result == 0:    #EDK_OK

                        mtrx[count][0] = thetaValue.value
                        mtrx[count][1] = alphaValue.value
                        mtrx[count][2] = low_betaValue.value
                        mtrx[count][3] = high_betaValue.value
                        mtrx[count][4] = gammaValue.value

                        count += 1

                        if count == depth+1:

                            sums = np.sum(mtrx, axis=0)

                            the = (the+sums[0])/(depth+1)
                            alp = (alp+sums[1])/(depth+1)
                            lbet = (lbet+sums[2])/(depth+1)
                            hbet = (hbet+sums[3])/(depth+1)
                            gam = (gam+sums[4])/(depth+1)

                            print "Training complete"
                            count = 0
                            logtrain(direct, the, alp, lbet, hbet, gam)
                            break


                        #print "Theta: %.6f, Alpha: %.6f, Low beta: %.6f, High beta %.6f, Gamma: %.6f \n" % (thetaValue.value, alphaValue.value, 
                        #                                           low_betaValue.value, high_betaValue.value, gammaValue.value)
                     
        elif state == 0x0600:
            print "Internal error in Emotiv Engine ! "
        time.sleep(0.1)
    return

def running():

    while (1):
        state = libEDK.IEE_EngineGetNextEvent(eEvent)
        
        if state == 0:
            eventType = libEDK.IEE_EmoEngineEventGetType(eEvent)
            libEDK.IEE_EmoEngineEventGetUserId(eEvent, user)
            if eventType == 16:  # libEDK.IEE_Event_enum.IEE_UserAdded
                ready = 1
                libEDK.IEE_FFTSetWindowingType(userID, 1);  # 1: libEDK.IEE_WindowingTypes_enum.IEE_HAMMING
                print "User added"
                            
            if ready == 1:
                for i in channelList: 
                    result = c_int(0)
                    result = libEDK.IEE_GetAverageBandPowers(userID, i, theta, alpha, low_beta, high_beta, gamma)
                    
                    if result == 0:    #EDK_OK

                        up = []

                        up[0] = abs(thetaValue.value - avgtheta)
                        up[1] = abs(alphaValue.value - avgalpha)
                        up[2] = abs(low_betaValue.value - avglbeta)
                        up[3] = abs(high_betaValue.value - avghbeta)
                        up[4] = abs(gammaValue.value - avggamma)

                        down = []

                        down[0] = abs(thetaValue.value - avgtheta2)
                        down[1] = abs(alphaValue.value - avgalpha2)
                        down[2] = abs(low_betaValue.value - avglbeta2)
                        down[3] = abs(high_betaValue.value - avghbeta2)
                        down[4] = abs(gammaValue.value - avggamma2)

                        if np.sum(up) > np.sum(down):
                            print "up"

                        else:
                            print "down"


                        #print "Theta: %.6f, Alpha: %.6f, Low beta: %.6f, High beta %.6f, Gamma: %.6f \n" % (thetaValue.value, alphaValue.value, 
                        #                                           low_betaValue.value, high_betaValue.value, gammaValue.value)
                     
        elif state == 0x0600:
            print "Internal error in Emotiv Engine ! "
        time.sleep(0.1)

    return

# -------------------------------------------------------------------------
print "==================================================================="
print "|                           Mind Control                          |"
print "|                                                                 |"
print "|         Created by: Darwin, Eric, Sebastien and Zhengqi         |"
print "==================================================================="

# -------------------------------------------------------------------------
if libEDK.IEE_EngineConnect("Emotiv Systems-5") != 0:
        print "Emotiv Engine start up failed."
        exit();

while (1):

    print "Welcome to Mind Control."
    print "What would you like to do?"
    print "1) Train up command"
    print "2) Train down command"
    print "3) Test your superpowers"

    choice = input("Choice: ")

    if choice == 1:
        readtrain(1)
        training(1, avgtheta, avgalpha, avglbeta, avghbeta, avggamma)

    elif choice == 2:
        readtrain(0)
        training(0, avgtheta2, avgalpha2, avglbeta2, avghbeta2, avggamma2)

    elif choice == 3:
        readtrain(0)
        readtrain(1)
        running()

    print "\n\n\n"


# -------------------------------------------------------------------------
libEDK.IEE_EngineDisconnect()
libEDK.IEE_EmoStateFree(eState)
libEDK.IEE_EmoEngineEventFree(eEvent)
