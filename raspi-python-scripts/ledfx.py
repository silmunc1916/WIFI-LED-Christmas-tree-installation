#!/usr/bin/python

import socket
import os
import smbus as smbus
import time
import random
import sys


#print "Aufrufoptionen: ", sys.argv

#----- Definitionen -------------

TCP_PORT = 8003  # Serverport am Pi
BUFFER_SIZE = 64 # maximale Befehlslaenge
fertig = 0
i2c_addr1 = 0x0e # 1. LED-Controller
i2c_addr2 = 0x06 # 2. LED-Controller
i2c_addrall = 0x70 # 1.+2. LED-Controller
i2c_addreset = 0x03 # die Software-Reset Adresse
v = 0x30 # Testwert (nicht zu hell, wg. Leistung!)
x = 0x31 # Testwert um 1 erhoeht fuer die Range-Funktionen - nur aus Bequemlichekeit
vf = 0x30 # Testwert fuer colorfadingrand
#showmode = 2
#maxhell = 128
#fasendauer = 10 # 10s ohne Veraenderung

try:
    showmode = int(sys.argv[1])
except ValueError:
    showmode = 2

try:
    maxhell = int(sys.argv[2])
except ValueError:
    maxhell = 128

try:
    fasendauer = int(sys.argv[3])
except ValueError:
    fasendauer = 10

#print "fxstart: showmode=", showmode
#---------------------------------

def monochrome(c):
    try:
        i2c.write_i2c_block_data(i2c_addrall,0x82,[c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c]) # alle Segmente einfaerbig
    except IOError:
        print "Ausgabefehler beim Initialisieren!"
    time.sleep(0.1)

def monorand():
    time.sleep(0.1)
    r = random.randint(0,x)
    b = random.randint(0,x)
    g = random.randint(0,x)
    try:
        i2c.write_i2c_block_data(i2c_addrall,0x82,[b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,v]) 
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)

def baumrand(): # wie monorand, nur Stern und Kerzen andere rand. Farbe
    time.sleep(0.1)
    r = random.randint(0,x)
    b = random.randint(0,x)
    g = random.randint(0,x)
    sr = random.randint(0,x) # stern
    sb = random.randint(0,x) # stern
    sg = random.randint(0,x) # stern
    kr = random.randint(0,x) # kerzen
    kb = random.randint(0,x) # kerzen
    kg = random.randint(0,x) # kerzen
    
    try:
        i2c.write_i2c_block_data(i2c_addr1,0x82,[b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,v])
        i2c.write_i2c_block_data(i2c_addr2,0x82,[b,r,g,b,r,g,sb,sr,sg,sb,sr,sg,kb,kr,kg,v]) 
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)

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

    #Farben setzen
    monochrome(v)

def ledalloff(): #alles aus
    try:
        i2c.write_i2c_block_data(i2c_addrall,0x94,[0x00,0x00,0x00,0x00]) # 94h = Register 14h mit auto-increment
    except IOError:
        print "Ausgabefehler!"
    #i2c.write_i2c_block_data(i2c_addr2,0x94,[0x00,0x00,0x00,0x00])
    
def ledallon(): #alles ein
    try:
        i2c.write_i2c_block_data(i2c_addrall,0x94,[0xff,0xff,0xff,0xff]) # 94h = Register 14h mit auto-increment
    except IOError:
        print "Ausgabefehler!"    
    #i2c.write_i2c_block_data(i2c_addr2,0x94,[0xaa,0xaa,0xaa,0xaa])
    

def timecheck():
    # zwischen 17 und 8 Uhr die Helligkeit reduzieren
    global showmode
    global maxhell

    stunde = time.localtime().tm_hour
    maxhell = 128
    oldshow = showmode
    modeoff = 0 # LEDs nicht ausschalten
	
    if stunde >= 2:
	modeoff = 1
    if stunde >= 5:
        modeoff = 0
    if stunde >= 8:
        maxhell = 255
    if stunde >= 9:
        modeoff = 1
    if stunde >= 15:
        modeoff = 0
        if showmode < 2: # showmode starten, wenn noch nix laeuft
            showmode = 2
    if stunde >= 17:
        maxhell = 127
        
    i2c.write_byte_data(i2c_addrall,0x12,maxhell) #  globale Helligkeit setzen

    if modeoff == 1:
        showmode = 0
    
    if oldshow != showmode:
        if showmode > 1:
            ledallon()
        else:
            ledalloff()

    

def baumstd():
    time.sleep(0.1)
    try:
        i2c.write_i2c_block_data(i2c_addr1,0x82,[0,0,v,0,0,v,0,0,v,0,0,v,0,0,v,0])
        i2c.write_i2c_block_data(i2c_addr2,0x82,[0,0,v,0,0,v,0,v,v,0,v,v,0,v,0,v])
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)
                             
def baumclear():
    time.sleep(0.1)
    try:
        i2c.write_i2c_block_data(i2c_addr1,0x82,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        i2c.write_i2c_block_data(i2c_addr2,0x82,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)

def stern (red, green, blue):
    time.sleep(0.1)
    try:
        i2c.write_i2c_block_data(i2c_addr2,0x88,[blue,red,green,blue,red,green])
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)

def sternrand():
    time.sleep(0.1)
    r = random.randint(0,x)
    b = random.randint(0,x)
    g = random.randint(0,x)
    try:
        i2c.write_i2c_block_data(i2c_addr2,0x88,[b,r,g,b,r,g])
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)


def lightup():
    time.sleep(0.1)
    stufe = maxhell / 15
    for r in range(0, 15):
        try:
            i2c.write_byte_data(i2c_addrall,0x12,r*stufe)
        except IOError:
            print "Ausgabefehler!"
        time.sleep(0.05)
    try:
        i2c.write_byte_data(i2c_addrall,0x12,maxhell)
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.05)

def lightdown():
    time.sleep(0.1)
    stufe = maxhell / 15
    for r in range(0, 15):
        try:
            i2c.write_byte_data(i2c_addrall,0x12,maxhell-r*stufe)
        except IOError:
            print "Ausgabefehler!"
        time.sleep(0.05)
    try:
        i2c.write_byte_data(i2c_addrall,0x12,0)
    except IOError:
        print "Ausgabefehler!"


def colorfadingrand(oldr, oldg, oldb, limit): # fadet von einem vorgegebenen (alten) Farbwert zu einem neuen random-Wert
    # limit: fadingdurchlaeufe (0= ewig)
    end = 0
    counter = 0

    while end == 0: 

        time.sleep(0.1)
        newr = random.randint(0,vf)
        newg = random.randint(0,vf)
        newb = random.randint(0,vf)

        for i in range(0, 20):
            r = ((oldr * (20 - i)) + (newr * i)) / 40;
            g = ((oldg * (20 - i)) + (newg * i)) / 40;
            b = ((oldb * (20 - i)) + (newb * i)) / 40;
            try:
                i2c.write_i2c_block_data(i2c_addrall,0x82,[b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,v]) 
            except IOError:
                print "Ausgabefehler!"
            time.sleep(0.1)

        oldr = newr
        oldg = newg
        oldb = newb
        if limit > 0:
            if counter >= limit:    # beenden, wenn limit erreicht ist
                end = 1
def colorfx():

    for r in range(0, 64):
        for g in range(0, 64):
            for b in range(0, 64):
                try:
                    i2c.write_i2c_block_data(i2c_addrall,0x82,[b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,v]) 
                except IOError:
                    print "Ausgabefehler!"
                time.sleep(0.1)

    

def fx1():
    #i2c.write_i2c_block_data(i2c_addrall,0x94,[0xff,0xff,0xff,0xff])
    lightup()
    lightdown()

def fx2():
    #i2c.write_i2c_block_data(i2c_addrall,0x94,[0xff,0xff,0xff,0xff])
    lightdown()
    lightup()


def lshow1():
    
    time.sleep(fasendauer)
    lightdown()
    baumstd()
    sternrand()
    lightup()
    time.sleep(fasendauer)
    
    for r in range(0, 16):
        sternrand()
        time.sleep(fasendauer)

    lightdown()
    monochrome(v)
    sternrand()
    lightup()
    time.sleep(fasendauer)
    
    for r in range(0, 16):
        sternrand()
        time.sleep(fasendauer)


    for r in range(0, 16):
        lightdown()
        monorand()
        lightup()
        time.sleep(fasendauer)

    for r in range(0, 16):
        lightdown()
        baumrand()
        lightup()
        time.sleep(fasendauer)


def lshow2():

    for r in range(0, 16):
        lightdown()
        monorand()
        lightup()
        time.sleep(fasendauer)

    for r in range(0, 16):
        lightdown()
        baumrand()
        lightup()
        time.sleep(fasendauer)

def lshow3b():
    r = random.randint(0,x)
    g = random.randint(0,x)
    b = random.randint(0,x)
    try:
        i2c.write_i2c_block_data(i2c_addrall,0x82,[b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,v]) 
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)

    colorfadingrand(r, g, b, 0)


def lshow3():

    colorfadingrand(0, 0, 0, 0)
    

def lshow4():

    for r in range(0, 16):
        monorand()
        #time.sleep(0.1) #2x time.sleep(0.1) ist in monorand() schon enthalten

#---- Hauptprogramm -----------------

i2c = smbus.SMBus(0) # i2c-Bus 0 ansprechen
i2cinit()

while fertig == 0: # laeuft eigentlich ewig, wird von aussen (ledserver.py) terminiert

    #print "loop: vor timecheck: showmode=", showmode
    timecheck()
    i2creset()
    i2cinit()
    #print "loop: nach timecheck: showmode=", showmode

    if showmode == 2:
        print "Lightshow1"
        lshow1()
    if showmode == 3:
        print "Lightshow2"
        lshow2()
    if showmode == 4:
        print "Lightshow3"
        lshow3()
    if showmode == 5:
        print "Lightshow4"
        lshow4()
    if showmode == 6:
        print "Lightshow5"
        colorfx()


    elif showmode == 0:
        print "nix tun"
        time.sleep(900) # alle 15min checken


    


