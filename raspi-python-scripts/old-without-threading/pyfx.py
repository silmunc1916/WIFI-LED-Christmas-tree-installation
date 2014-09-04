#!/usr/bin/env python

import socket
import os
import smbus as smbus
import time
import random

import ledconfig

print "pyfx: frisch importiertes ledconfig.showmode = ", ledconfig.showmode

#----- Definitionen -------------

TCP_PORT = 8003  # Serverport am Pi
BUFFER_SIZE = 64 # maximale Befehlslaenge
fertig = 0
i2c_addr1 = 0x0e # 1. LED-Controller
i2c_addr2 = 0x06 # 2. LED-Controller
i2c_addrall = 0x70 # 1.+2. LED-Controller
v = 0x30 # Testwert (nicht zu hell, wg. Leistung!)
fasendauer = 10 # 300s = 5min ohne Veraenderung

#---------------------------------

def monochrome(c):
    try:
        i2c.write_i2c_block_data(i2c_addrall,0x82,[c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c]) # alle Segmente einfaerbig
    except IOError:
        print "Ausgabefehler beim Initialisieren!"
    time.sleep(0.1)

def monorand():
    time.sleep(0.1)
    r = random.randint(0,31)
    b = random.randint(0,31)
    g = random.randint(0,31)
    try:
        i2c.write_i2c_block_data(i2c_addrall,0x82,[b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,c]) 
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)
        
def i2cinit():
    #derzeit nur fuer den 1. Chip
    # Mode1 register sleep auf off stellen
    try:
        i2c.write_byte_data(i2c_addrall,0x00,0x81)
        #i2c.write_byte_data(i2c_addr2,0x00,0x81)
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

    stunde = time.localtime().tm_hour
    ledconfig.maxhell = 128
    oldshow = ledconfig.showmode
    ledconfig.showmode = 2

    if stunde >= 8:
        ledconfig.maxhell = 255
    if stunde >= 9:
        ledconfig.showmode = 0
    if stunde >= 15:
        if ledconfig.showmode < 2: # showmode nur starten, wenn noch nix laeuft
            ledconfig.showmode = 2
    if stunde >= 17:
        ledconfig.maxhell = 127
        
    i2c.write_byte_data(i2c_addrall,0x12,ledconfig.maxhell)
    if oldshow != ledconfig.showmode:
        if ledconfig.showmode > 1:
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
    r = random.randint(0,31)
    b = random.randint(0,31)
    g = random.randint(0,31)
    try:
        i2c.write_i2c_block_data(i2c_addr2,0x88,[b,r,g,b,r,g])
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.1)


def lightup():
    time.sleep(0.1)
    stufe = ledconfig.maxhell / 15
    for r in range(0, 15):
        try:
            i2c.write_byte_data(i2c_addrall,0x12,r*stufe)
        except IOError:
            print "Ausgabefehler!"
        time.sleep(0.05)
    try:
        i2c.write_byte_data(i2c_addrall,0x12,ledconfig.maxhell)
    except IOError:
        print "Ausgabefehler!"
    time.sleep(0.05)

def lightdown():
    time.sleep(0.1)
    stufe = ledconfig.maxhell / 15
    for r in range(0, 15):
        try:
            i2c.write_byte_data(i2c_addrall,0x12,ledconfig.maxhell-r*stufe)
        except IOError:
            print "Ausgabefehler!"
        time.sleep(0.05)
    try:
        i2c.write_byte_data(i2c_addrall,0x12,0)
    except IOError:
        print "Ausgabefehler!"

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
    
    for r in range(0, 15):
        sternrand()
        time.sleep(fasendauer)

    lightdown()
    monochrome(v)
    sternrand()
    lightup()
    time.sleep(fasendauer)
    
    for r in range(0, 15):
        sternrand()
        time.sleep(fasendauer)


def lshow2():
    lightdown()
    monorand()
    lightup()
    time.sleep(fasendauer)

#---- Hauptprogramm -----------------

i2c = smbus.SMBus(0) # i2c-Bus 0 ansprechen
i2cinit()

while fertig == 0:

    timecheck()

    print "pyfx: ledconfig.showmode = ", ledconfig.showmode

    if ledconfig.showmode == 2:
        print "Lightshow1"
        lshow1()
    if ledconfig.showmode == 3:
        print "Lightshow2"
        lshow2()
    elif ledconfig.showmode == 0:
        print "nix tun"
        time.sleep(900) # alle 15min checken



    
    


