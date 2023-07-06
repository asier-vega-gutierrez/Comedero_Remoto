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

app = Flask(__name__)
app = Flask(__name__, template_folder='./templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'test.mosquitto.org'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
mqtt = Mqtt(app)

#GPIO y setup
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
pin_led_agua = 24
GPIO.setup(pin_led_agua, GPIO.OUT) #led
pin_led_comida = 26
GPIO.setup(pin_led_comida, GPIO.OUT) #led

#Topic de la aplicacion web a subscribirme (general)
topic_sub_COMEDERO = "pub/comedero/#"

#APP--------------------------------

#clase para definir un comedero y sus datos identificativos
class comedero():
    def __init__(self,id,humedad,distancia,alarma_agua,alarma_comida):
        self.id = id
        self.humedad = humedad
        self.distancia = distancia
        self.alarma_agua = alarma_agua
        self.alarma_comida = alarma_comida

#numero de comederos de la aplicacion
global comederos
comederos = [comedero(0,0,0,0,0),comedero(1,0,0,0,0),comedero(2,0,0,0,0)]

#Al recibir un mensaje de mqtt añado al objeto de comedero con el respectivo identificador sus datos
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print("---Recivo")
    #descodifico el mensaje recivido
    payload = message.payload.decode()
    payload = json.loads(payload)
    #print("Mensaje recibido del topic: "+message.topic)
    #print(message.payload.decode())
    
    #si el topic del mensaje coincide con el topic de comedero
    if message.topic[:12] == "pub/comedero":
        id = payload["id"]
        humedad = str(payload["humedad"])
        distancia = str(payload["distancia"])
        alarma_agua = str(payload["alarma_agua"])
        alarma_comida = str(payload["alarma_comida"])

    #guardo los datos
    comedero_temp = comedero(int(id),humedad,distancia,alarma_agua,alarma_comida)
    comederos.insert(comedero_temp.id,comedero_temp)
    #print("--------")
    #print(comederos[0].humedad)
    #print(comederos[1].humedad)
    #print(comederos[2].humedad)

    #enciendo o apago la led
    if alarma_comida == "1":
        GPIO.output(pin_led_comida, GPIO.HIGH)
    elif alarma_comida == "0":
        GPIO.output(pin_led_comida, GPIO.LOW)

    if alarma_agua == "1":
        GPIO.output(pin_led_agua, GPIO.HIGH)
    elif alarma_agua == "0":
        GPIO.output(pin_led_agua, GPIO.LOW)

#Ruta principal, para acceder a las opciones de los comederos
@app.route("/home/")
def home():
    return render_template('home.html')

#Ruta para acceder a la visualizacion de los datos 
@app.route("/datos/<device>")
def mSelect(device):
    #en funcion de la alarma sabesmos is hay o no agua
    if int(comederos[int(device)].alarma_agua) == 0:
        agua = 1
    else:
        agua = 0

    templateData = {
      'humedad': agua,
      'comida': round(float(comederos[int(device)].distancia))
    }
    return render_template('datos.html', **templateData)

#me suscribo al topic general
mqtt.subscribe(topic_sub_COMEDERO)

#ejecuto el servidor
if __name__ == "__main__":
   app.run(host='0.0.0.0', debug=True)