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


        avgtheta = float(lines[0].rstrip())
        avgalpha = float(lines[1].rstrip())
        avglbeta = float(lines[2].rstrip())
        avghbeta = float(lines[3].rstrip())
        avggamma = float(lines[4].rstrip())

    elif direct == 0:

        target = open("trainfiled.txt", "r")
        lines = target.readlines()

        avgtheta2 = float(lines[0].rstrip())
        avgalpha2 = float(lines[1].rstrip())
        avglbeta2 = float(lines[2].rstrip())
        avghbeta2 = float(lines[3].rstrip())
        avggamma2 = float(lines[4].rstrip())

    


    return

def logtrain(direct, the, alp, lbet, hbet, gam):

    print "Logging Data...."

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
    print "done..."
    return

def training(direct, the, alp, lbet, hbet, gam):

    ready = 1

    count = 0

    depth = 1000

    w, h = 5 , depth

    mtrx = [[0 for x in range(w)] for y in range(h)]

    while (1):
        state = libEDK.IEE_EngineGetNextEvent(eEvent)
        
        if state == 0:
            eventType = libEDK.IEE_EmoEngineEventGetType(eEvent)
            libEDK.IEE_EmoEngineEventGetUserId(eEvent, user)
          
            if ready == 1:
                for i in channelList: 
                    result = c_int(0)
                    result = libEDK.IEE_GetAverageBandPowers(userID, i, theta, alpha, low_beta, high_beta, gamma)
                    
                    if result == 0:    #EDK_OK

                        #print "Matrix: ",
                        #print mtrx

                        mtrx[count][0] = thetaValue.value
                        mtrx[count][1] = alphaValue.value
                        mtrx[count][2] = low_betaValue.value
                        mtrx[count][3] = high_betaValue.value
                        mtrx[count][4] = gammaValue.value

                        count += 1

                        print "Count: ", count

                        if count == depth:

                            #sums = np.sum(mtrx, axis=0)
                            sums = [sum(mtrx[x]) for x in range(0,depth-1) ]


                            the = (float(the)+sums[0])/(depth)
                            alp = (float(alp)+sums[1])/(depth)
                            lbet = (float(lbet)+sums[2])/(depth)
                            hbet = (float(hbet)+sums[3])/(depth)
                            gam = (float(gam)+sums[4])/(depth)

                            print "Training complete"
                            count = 0
                            logtrain(direct, str(the), str(alp), str(lbet), str(hbet), str(gam))
                            ready = 0
                            return


                        #print "Theta: %.6f, Alpha: %.6f, Low beta: %.6f, High beta %.6f, Gamma: %.6f \n" % (thetaValue.value, alphaValue.value, 
                        #                                           low_betaValue.value, high_betaValue.value, gammaValue.value)
                     
        elif state == 0x0600:
            print "Loading..."
        time.sleep(0.01)
    return

def running():

    ready = 1

    while (1):
        state = libEDK.IEE_EngineGetNextEvent(eEvent)
        
        if state == 0:
            eventType = libEDK.IEE_EmoEngineEventGetType(eEvent)
            libEDK.IEE_EmoEngineEventGetUserId(eEvent, user)
            if ready == 1:
                for i in channelList: 
                    result = c_int(0)
                    result = libEDK.IEE_GetAverageBandPowers(userID, i, theta, alpha, low_beta, high_beta, gamma)
                    
                    if result == 0:    #EDK_OK

                        up = [x for x in range(0,5)]

                        up[0] = abs(thetaValue.value - avgtheta)
                        up[1] = abs(alphaValue.value - avgalpha)
                        up[2] = abs(low_betaValue.value - avglbeta)
                        up[3] = abs(high_betaValue.value - avghbeta)
                        up[4] = abs(gammaValue.value - avggamma)

                        down = [x for x in range(0,5)]

                        down[0] = abs(thetaValue.value - avgtheta2)
                        down[1] = abs(alphaValue.value - avgalpha2)
                        down[2] = abs(low_betaValue.value - avglbeta2)
                        down[3] = abs(high_betaValue.value - avghbeta2)
                        down[4] = abs(gammaValue.value - avggamma2)

                        if sum(up) > sum(down):
                            print "up"

                        else:
                            print "down"


                        #print "Theta: %.6f, Alpha: %.6f, Low beta: %.6f, High beta %.6f, Gamma: %.6f \n" % (thetaValue.value, alphaValue.value, 
                        #                                           low_betaValue.value, high_betaValue.value, gammaValue.value)
                     
        elif state == 0x0600:
            print "Loading..."
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
user_logged = False
while (1):
    if not user_logged:
        while(1):
            state = libEDK.IEE_EngineGetNextEvent(eEvent)
            if state == 0:
                eventType = libEDK.IEE_EmoEngineEventGetType(eEvent)
                libEDK.IEE_EmoEngineEventGetUserId(eEvent, user)
                if eventType == 16:  # libEDK.IEE_Event_enum.IEE_UserAdded

                    libEDK.IEE_FFTSetWindowingType(userID, 1);  # 1: libEDK.IEE_WindowingTypes_enum.IEE_HAMMING
                    print "User added"
                    user_logged = True
                    break

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
