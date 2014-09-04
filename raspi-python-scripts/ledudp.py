#!/usr/bin/python

import os
import socket
import subprocess
import time


import ledconfig

#----- Definitionen -------------------------------

UDP_PORT = 8002  # UDP-Port fuer Broadcasts
BROADCAST_IP = "10.0.0.255"
MSG = "<iamledc:raspi01>"

#---- Hauptprogramm -----------------

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(("", 0))

while 1:
    s.sendto(MSG, (BROADCAST_IP, UDP_PORT))
    time.sleep(10)




# fxprocess = subprocess.Popen("/home/pi/led/pyfx.py") # Effektscript starten
fxprocess = subprocess.Popen(['python', '/home/pi/led/ledfx.py', str(showmode), str(maxhell), str(fasendauer)])

#fxthread = threading.Thread(fxloop, args=())
#fxthread.daemon = True
#fxthread.start()

if fxprocess is None:
    print "fxstart fehlgeschlagen"

while fertig == 0:

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

    print "fertig=", fertig
        
s.close()   # ende

if fxprocess is not None:
    fxprocess.terminate() # Effektscript beenden
    fxprocess.wait() # warten auf Beendigung

print "ledserver wird beendet"


    # Antwort: conn.send(data)  # echo


