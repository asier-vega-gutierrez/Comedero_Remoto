import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import time
import eventlet
import json

from flask import Flask, render_template, request
from flask import request, redirect
from flask_mqtt import Mqtt
from time import sleep
eventlet.monkey_patch()

#SETUP------------------------------

#GPIO y setup
GPIO.cleanup()
GPIO.setmode(GPIO.BCM) #numeracion de pines basada en numeros GPIO

#Direccion del broker
hostname = 'test.mosquitto.org'

#Topic de la aplicacion web a subscribirme
topic_sub_COMEDERO = "pub/comedero" 


#APP--------------------------------



#RECEPTOR MQTT----------------------

#Callback que se llama cuando el cliente recibe el CONNACK del servidor 
#Result code 0 significa, conexion sin errores
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #Nos subscribirmos al topic 
    client.subscribe(topic_sub_COMEDERO)

#Callback que se llama "automaticamente" cuando se recibe un mensaje del Publiser
def on_message(client, userdata, msg):
    msg_rec = msg.payload.decode("utf-8")
    print("topic:  "+ msg.topic)
    msg_rec = json.loads(msg_rec)
    print(msg_rec)

#Creamos un cliente MQTT 
client = mqtt.Client()

#Definimos los callbacks para conectarnos y subscribirnos al topic
client.on_connect = on_connect
client.on_message = on_message

#Conectamos al hosntame que se debe definir arriba
client.connect(hostname, 1883, 60)

#Inicialmos el loop de la siguiente manera:
client.loop_forever()



