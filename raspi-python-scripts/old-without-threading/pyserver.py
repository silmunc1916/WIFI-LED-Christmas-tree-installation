#!/usr/bin/env python

import os
import smbus as smbus
import socket
import subprocess
import time

import ledconfig

#----- Definitionen -------------

TCP_PORT = 8003  # Serverport am Pi
BUFFER_SIZE = 64 # maximale Befehlslaenge
fertig = 0
i2c_addr1 = 0x0e # 1. LED-Controller
i2c_addr2 = 0x06 # 2. LED-Controller
i2c_addrall = 0x70 # 1.+2. LED-Controller
v = 0x30 # Testwert
fxprocess = None # der Prozess des pyfx scripts
#---------------------------------

def auswertung(text=None):
    global fxprocess
    text = text.lower()

    cstart = text.find("<")
    cend = text.find(">")

    if cstart > -1:
        if cend > -1:
            command = text[cstart+1:cend]
            print "command: ", command

            if command == "exit":
                fertig = 1
                print "end!!!!!"
            elif command == "shutdown":
                os.system("sudo -s shutdown -h now")
                fertig = 1
            elif command == "reboot":
                os.system("sudo -s shutdown -r now")
                fertig = 1

            elif command == "start":
                i2cinit()
                
            elif command == "lt0":
                ledalloff()
                
            elif command == "lt1":
                ledallon()
                             
            elif command == "baum1":
                baumstd()
            elif command == "baum0":
                baumclear()

            elif command == "fx1":
                fx1()

            elif command == "fx2":
                fx2()
            elif command == "prog0":    # ablaufendes Effekt-Programm beenden
                ledconfig.showmode = 1
                if fxprocess is not None:
                    fxprocess.terminate()   # Effektscript beenden
                    fxprocess.wait()        # warten auf Beendigung
                
            elif command == "prog1":    # Effekt-Programm starten

                if ledconfig.showmode < 2:
                    ledconfig.showmode = 2
                fxprocess = subprocess.Popen(['python', '/home/pi/led/pyfx.py'])

            elif command.startswith("setshow"):
                cdata = command.split(':')
                print "Setshow auf ", cdata[1]
                try:
                    i = int(cdata[1])
                    print "converted: ", i
                except ValueError:
                    i = 2
                ledconfig.showmode = i
                print "pyserver: ledconfig.showmode = ", ledconfig.showmode
                ledconfig.showmode = 3
                fxprocess = subprocess.Popen(['python', '/home/pi/led/pyfx.py'])
    
            else:
                fertig = 0
                #dummy


#--------------------------------------------------------------

#---- Hauptprogramm -----------------

i2c = smbus.SMBus(0) # i2c-Bus 0 ansprechen
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.bind((TCP_IP, TCP_PORT))
s.bind(("", TCP_PORT))  # "" fuer alle lokalen Adressen
s.listen(1)

# fxprocess = subprocess.Popen("/home/pi/led/pyfx.py") # Effektscript starten
fxprocess = subprocess.Popen(['python', '/home/pi/led/pyfx.py'])

if fxprocess is None:
    print "fxstart fehlgeschlagen"

while fertig == 0:
    print "fertig=", fertig
    connection, address = s.accept()

    try:
        print 'Connection address:', address

        while 1:
            data = connection.recv(BUFFER_SIZE)
            if data:
                print "received data:", data
                auswertung(data)
            else:
                break
    finally:
        connection.close()
s.close()   # ende

if fxprocess is not None:
    fxprocess.terminate() # Effektscript beenden
    fxprocess.wait() # warten auf Beendigung

print "pyserver wird beendet"


    # Antwort: conn.send(data)  # echo


