#!/usr/bin/python

import os
import smbus as smbus
import socket
import subprocess
import time


import ledconfig

#----- Definitionen -------------------------------

TCP_PORT = 8003  # Serverport am Pi
BUFFER_SIZE = 64 # maximale Befehlslaenge
fertig = 0
i2c_addr1 = 0x0e # 1. LED-Controller
i2c_addr2 = 0x06 # 2. LED-Controller
i2c_addrall = 0x70 # 1.+2. LED-Controller
i2c_addreset = 0x03 # die Software-Reset Adresse
v = 0x30 # Testwert

fxprocess = None # der Prozess des ledfx scripts
bcprocess = None # der Prozess des ledudp (broadcast) scripts

showmode = 2
maxhell = 255
fasendauer = 10 # 300s = 5min ohne Veraenderung

#-------------------------------------------------
#import sqlite3 nicht vergessen
##def initdb():
##    con = None
##    try:
##        con = sqlite.connect('led.db')
##        cur = con.cursor()    
##        # create a table
##        cur.execute("""CREATE TABLE IF NOT EXISTS ledconfig (showmode integer, maxhell integer, fasendauer integer)""")
##
##        # insert data
##        cursor.execute("INSERT INTO ledconfig VALUES (2, 255, 10)")
## 
##        conn.commit() # save data to database
##
##    except lite.Error, e:
##    
##        print "Error %s:" % e.args[0]
##    
##    finally: # db schliessen
##        if con:
##            con.close()

#showmode = 1

# showmode Werte:
# 0 : keine Anzeige - LED-Outputs abgedreht (tagueber)
# 1 : aktuelles Effekt-Programm wird beendet (aktuelle Anzeige bleibt aber)
# 2 : Effekt-Programm "lshow1"


# maxhell = 255 # maximale Helligkeit (in der Nacht halbieren: 127)

#fasendauer in sekunden - Wartezeit nach den Effekten

#-----------------------------------------------------------------

# Werte aus db lesen

##    #showmode = 1
##    #maxhell = 255
##    #fasendauer = 10
##
##    # Konfig-Werte aus DB lesen
##    
##    con = None
##    try:
##        con = sqlite.connect('led.db')
##        cur = con.cursor()    
##        # create a table
##        cur.execute("SELECT * FROM ledconfig")
##        row = cur.fetchone()
##        showmode = row[0]
##        maxhell = row[1]
##        fasendauer = row[3]
##
##    except lite.Error, e:
##    
##        print "Error %s:" % e.args[0]
##    
##    finally: # db schliessen
##        if con:
##            con.close()

#---------------------------------------------------------------

def i2creset():
    i2c.write_i2c_block_data(i2c_addreset,0xa5,[0x5a])
    time.sleep(0.5)

def i2cinit():
    # Mode1 register sleep auf off stellen
    try:
        i2c.write_byte_data(i2c_addrall,0x00,0x81)
    except IOError:
        print "Ausgabefehler beim Initialisieren!"
        time.sleep(0.1)
        try:
            i2c.write_byte_data(i2c_addrall,0x00,0x81)
        except IOError:
            print "Ausgabefehler beim Initialisieren!"
    
    # Wert 0xaa nach register 14h-17h "LED output state 0-3" schreiben
    try:
        i2c.write_i2c_block_data(i2c_addrall,0x94,[0xff,0xff,0xff,0xff]) # 94h = Register 14h mit auto-increment
        #i2c.write_i2c_block_data(i2c_addr2,0x94,[0xaa,0xaa,0xaa,0xaa])
    except IOError:
        print "Ausgabefehler beim Initialisieren!"
        time.sleep(0.1)
        try:
            i2c.write_i2c_block_data(i2c_addrall,0x94,[0xff,0xff,0xff,0xff])
        except IOError:
            print "Ausgabefehler beim Initialisieren!"

    #hier wird noch keine Farbe gesetzen (nach -reset alles auf 00 (schwarz)



def auswertung(text=None):
    global fxprocess
    global fertig
    global showmode
    global maxhell
    global fasendauer

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

    elif command == "reset":
        i2creset()
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
        showmode = 1
        if fxprocess is not None:
            fxprocess.terminate()   # Effektscript beenden
            fxprocess.wait()        # warten auf Beendigung
            fxprocess = None
        
    elif command == "prog1":    # Effekt-Programm starten
        if showmode < 2:
            showmode = 2
        if fxprocess is not None:
            fxprocess.terminate()   # Effektscript beenden
            fxprocess.wait()        # warten auf Beendigung
        fxprocess = subprocess.Popen(['python', '/home/pi/led/ledfx.py', str(showmode), str(maxhell), str(fasendauer)])

    elif command.startswith("setshow"):
        cdata = command.split(':')
        try:
            i = int(cdata[1])
            print "converted: ", i
        except ValueError:
            i = 2
        showmode = i
        if fxprocess is not None:
            print "fxprocess wird beendet"
            fxprocess.terminate()   # Effektscript beenden
            fxprocess.wait()        # warten auf Beendigung
            print "fxprocess wurde beendet"
        fxprocess = subprocess.Popen(['python', '/home/pi/led/ledfx.py', str(showmode), str(maxhell), str(fasendauer)])

    elif command.startswith("setcolor"):    # Farbe (monochrome) live setzen (prog0 sollte vorher gesendet worden sein)
        cdata = command.split(':')
        try:
            r = int(cdata[1])
            print "converted: ", r
        except ValueError:
            r = 0
        try:
            g = int(cdata[2])
            print "converted: ", g
        except ValueError:
            g = 0
        try:
            b = int(cdata[3])
            print "converted: ", b
        except ValueError:
            b = 0
        try:
            i2c.write_i2c_block_data(i2c_addrall,0x82,[b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,v]) 
        except IOError:
            print "Ausgabefehler!"
        time.sleep(0.1)


    else:
        fertig = 0
        #dummy



#--------------------------------------------------------------

#---- Hauptprogramm -----------------

#initdb()    # db einrichten

##con = None
##try:
##    con = sqlite.connect('led.db')
##    cur = con.cursor()    
##    # create a table
##    cur.execute("""CREATE TABLE config (showmode integer, maxhell integer, fasendauer integer""")
##
##    # insert data
##    cursor.execute("INSERT INTO config VALUES (2, 255, 10)")
##
##    conn.commit() # save data to database
##
##except lite.Error, e:
##
##    print "Error %s:" % e.args[0]
##
##finally: # db schliessen
##    if con:
##        con.close()



i2c = smbus.SMBus(0) # i2c-Bus 0 ansprechen#

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.bind((TCP_IP, TCP_PORT))
s.bind(("", TCP_PORT))  # "" fuer alle lokalen Adressen
s.listen(1)

# fxprocess = subprocess.Popen("/home/pi/led/pyfx.py") # Effektscript starten
fxprocess = subprocess.Popen(['python', '/home/pi/led/ledfx.py', str(showmode), str(maxhell), str(fasendauer)])
bcprocess  = subprocess.Popen(['python', '/home/pi/led/ledudp.py'])



#fxthread = threading.Thread(fxloop, args=())
#fxthread.daemon = True
#fxthread.start()

if fxprocess is None:
    print "fxstart fehlgeschlagen"

while fertig == 0:

    connection, address = s.accept()

    try:
        print 'Connection address:', address
        text = ""   # zum Aufheben der abgeschnittenen Befehle

        while 1:
            data = connection.recv(BUFFER_SIZE)
            if data:
                print "received data:", data
                text = text + data.lower() # Rest mitnehmen fuer naechste Auswertung
                print "received data+rest:", text
                cstart = text.find("<")
                cend = text.find(">")

                while cstart > -1 and cend > -1 and cend > cstart:
                    command = text[cstart+1:cend]
                    rend = len(text)
                    text = text[cend+1:rend]    # der Rest
                    print "command: ", command
                    print "rest: ", text
                    auswertung(command)
                    cstart = text.find("<") # falls noch ein Befehl vorhanden ist
                    cend = text.find(">")   # -> weitermachen
                

            else:
                break
    finally:
        connection.close()

    print "fertig=", fertig
        
s.close()   # ende

if bcprocess is not None:
    bcprocess.terminate()
    bcprocess.wait()

if fxprocess is not None:
    fxprocess.terminate() # Effektscript beenden
    fxprocess.wait() # warten auf Beendigung


print "ledserver wird beendet"


    # Antwort: conn.send(data)  # echo


