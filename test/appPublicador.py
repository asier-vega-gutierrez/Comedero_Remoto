import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import json
import time
import random

#SETUP------------------------------

#GPIO y setup
GPIO.cleanup()
GPIO.setmode(GPIO.BCM) #numeracion de pines basada en numeros GPIO

#Direccion del broker
hostname = 'test.mosquitto.org'

#Definimos los topics para MQTT
topic_pub_COMEDERO = "pub/comedero/1"


#APP--------------------------------




#EMISOR MQTT------------------------

while True:

    #leemos el valores
    humedad = 3
    mensaje_COMEDERO = {
        "id": 1,
        "humedad": humedad,
    }

    #Convertimos el mensaje en tipo JSON
    mensaje_json_COMEDERO = json.dumps(mensaje_COMEDERO)

    #Publicamos los valores por MQTT, para que los reciva el servidor FLASK
    publish.single(topic_pub_COMEDERO, mensaje_json_COMEDERO, hostname=hostname)
    print("publico")

    time.sleep(10)



   
 
