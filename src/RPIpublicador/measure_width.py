# -----------------------------------------------
#                           Curso 2021/2022
# 						  	Sistemas Embebidos. Universidad de Deusto. GDID
# Laura		Oct 25		    LABORATORIO 2
                            
#
# NOTE:
# 	No usar libreria de Grove.

import sys
import time
import RPi.GPIO as GPIO
import smbus


rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

#------------------------------------------------------------------
      # '''' TO DO '''''    
# Establecemos los pines a usar, y los definimos como entrada o salida
# segun el sensor
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)


GPIO.setup(18, GPIO.OUT) #buzzer
#------------------------------------------------------------------

#------------------------------------------------------------------
#       Funcion para medir la distancia al objeto
#------------------------------------------------------------------
usleep = lambda x: time.sleep(x / 1000000.0)

_TIMEOUT1 = 1000

_TIMEOUT2 = 10000

def leer_distancia(pin):
    GPIO.setup(pin, GPIO.OUT)  
    GPIO.output(pin, GPIO.LOW)  
    usleep(2)
    GPIO.output(pin, GPIO.HIGH)  
    usleep(10)
    GPIO.output(pin, GPIO.LOW)  
    GPIO.setup(pin, GPIO.IN)  

    t0 = time.time()
    count = 0
    while count < _TIMEOUT1:
        if GPIO.input(pin):
            break
        count += 1
    if count >= _TIMEOUT1:
        return None

    t1 = time.time()
    count = 0
    while count < _TIMEOUT2:
        if not GPIO.input(pin):
            break
        count += 1
    if count >= _TIMEOUT2:
        return None

    t2 = time.time()

    dt = int((t1 - t0) * 1000000)
    if dt > 530:
        return None

    distancia = ((t2 - t1) * 1000000 / 30 / 2)    # distancia en cm

    return distancia

#while True:
    #print("Distancia: " + str(leer_distancia()) + " cm") #Distancia actual de la comida en le comedero


