##for the pour robot
## writen by Jun. Ou
## junmse.ou@gmail.com

import serial
import time
import msvcrt


try:
    ser = serial.Serial(3,timeout=1) # connect to the serial port COM N for the mega and COM3 for the uno
    print("Successful connection to the serial port!")
except:
    print("Failed connection to the serial port!")

#read data from file and translate to a list
#set the mode.
#'g' for controlling ouput by the sensor and save data into a .dat file
#'r' for controlling output from the input.txt file
    
mode = 'none'
try:
    mode = raw_input("Mode Setup. d or c?\n")
except:
    print("Not Valid!")
    
if mode == 'c':
    #open file and read into a list
    inputfile = raw_input("input or raw_read? i/w \n")
    ser.write('r')
    if inputfile == 'i':
        try:
            f = open('input.txt','r')
        except:
            print("Error when read from file!")
    elif inputfile == 'w':
        try:
            f = open('raw_read.txt','r')
        except:
            print("Error when read from file!")
    try:   
        lines = f.readlines()
        for i in range(len(lines)):
            ser.write(lines[i])
            time.sleep(.5) # must have this time.
            print lines[i]
        ser.write("QUIT")
        print ("Finished communicating with Arduino. Exit!")
    except:
        print("Error!")
    
elif mode== 'd':
    try:
        #send a start command to arduino. g/h/m/l
        startCommand = 'g'
        startCommand = raw_input("Input the command send to arduino:\n")
        f = open("./raw_read.txt",'w')
        ser.write(startCommand)
        while msvcrt.kbhit()!=True and startCommand =='g':
            va1 = ser.readline()
            print va1
            f.write(va1)
            pass
        ser.write('s')
        f.close()
    except:
        print("Error!")
else:
    print("Not Valid Mode Input!")

#shut down the port
#ser.write('s')
#ser.close()
