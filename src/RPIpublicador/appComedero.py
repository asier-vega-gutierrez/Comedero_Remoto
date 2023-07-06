#Importacion de librerias
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import json
import time
import random
import dht_config
import measure_width

#SETUP------------------------------

#GPIO y setup
GPIO.cleanup()
GPIO.setmode(GPIO.BCM) #numeracion de pines basada en numeros GPIO

#Sensor de humedad temperatura 
gpio_pin_sensor_humedad_1 = 16 #GPIO 16 conectamos el pin SIG del sensor
sensorHumi_1 = dht_config.DHT(gpio_pin_sensor_humedad_1) #Pasar por argumento el número del GPIO


#Sensor de ultrasonidos
gpio_pin_sensor_ultrasonic_1 = 18


#Servo
GPIO.setup(5, GPIO.OUT) #pin 5 como salida, y pin_pwm como el pin 5 como PWM 
pin_pwm = GPIO.PWM(5, 50) #el pin es el 5, 50 = 50Hz de frecuencia de pulso
pin_pwm.start(0) #esta corriendo PWM, pero con el valor 0 (sin pulso)
grados = 0

#Rele
pin_rele = 22
GPIO.setup(pin_rele, GPIO.OUT, initial=GPIO.LOW) # Rele, inicializado a 

#Direccion del broker
hostname = 'test.mosquitto.org'

#Definimos los topics para MQTT
topic_pub_COMEDERO = "pub/comedero/1"


#APP--------------------------------

def main():

    distancia_1 = measure_width.leer_distancia(gpio_pin_sensor_ultrasonic_1) #llamamos a la funcion leer_distancia del measure_width.py
    print("Distancia: "+ str(distancia_1))

    #leemos los valores de la humedad
    humi_1, temp = sensorHumi_1.read()
    print("Humedad: " + str(humi_1))

    #control de la comida
    if distancia_1 > 100:
        grados = 90
        #calculamos el duty-cycle para los grados
        duty = ((grados/180) + 1.0)*5.0 
        pin_pwm.ChangeDutyCycle(duty) 
        print("---Rellenando comida")
        time.sleep(3)
        grados = 0 
        duty = ((grados/180) + 1.0)*5.0 
        pin_pwm.ChangeDutyCycle(duty) 
    else:
        grados = 0
        duty = ((grados/180) + 1.0)*5.0 
        pin_pwm.ChangeDutyCycle(duty) 
    
    #control de agua
    if humi_1 < 50:
        GPIO.output(pin_rele, GPIO.HIGH) #activación del rele, deja pasar el agua
        print("---Rellenando agua")
        time.sleep(3)
        GPIO.output(pin_rele, GPIO.LOW) #desactivacion del rele, no deja pasar el agua
    else:
        GPIO.output(pin_rele, GPIO.LOW) #desactivacion del rele, no deja pasar el agua
    
    #actualizo los valores para comprobar los cambios
    humi_1, temp = sensorHumi_1.read()
    distancia_1 = measure_width.leer_distancia(gpio_pin_sensor_ultrasonic_1)
    print("Distancia actual: " + str(distancia_1))
    print("Humedad actual: " + str(humi_1))

    #en el caso de que el rellenado a se haya completado con correcion se activa el bit de alarma
    if distancia_1 > 100:
        alarma_comida = 1
    else:
        alarma_comida = 0
    
    if humi_1 < 50:
        alarma_agua = 1
    else:
        alarma_agua = 0

#mirar pines y apuntarlos
    mensaje_COMEDERO = {
        "id": 1,
        "humedad": humi_1,
        "distancia": distancia_1,
        "alarma_comida": alarma_comida,
        "alarma_agua": alarma_agua
    }
    print("Alarma agua: " + str(alarma_agua))
    print("Alarma comida: " + str(alarma_comida))

    #Convertimos el mensaje en tipo JSON
    mensaje_json_COMEDERO = json.dumps(mensaje_COMEDERO)

    #Publicamos los valores por MQTT, para que los reciva el servidor FLASK
    publish.single(topic_pub_COMEDERO, mensaje_json_COMEDERO, hostname=hostname)
    print("---Publico")

    time.sleep(3)

main()

