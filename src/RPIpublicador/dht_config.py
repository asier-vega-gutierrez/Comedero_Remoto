#@Laura Arjona
#@Sistemas Embebidos. 2021

#Ejemplo de configuracion de lectura del sensor de temperatura y humedad DHT111

# La lectura de los datos del sensor, se realiza teniendo en cuenta 
# las estrictas restricciones temporales 
#https://files.seeedstudio.com/wiki/Grove-TemperatureAndHumidity_Sensor/res/DHT11.pdf

import time
import RPi.GPIO as GPIO

class DHT():

    MAX_CNT = 320
    PULSES_CNT = 41
        
    def __init__(self,pin):
        
        print("Inicializando sensor ...")
        
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)

        
        GPIO.setup(pin,GPIO.IN)
        self.pin = pin
        self._last_temp = 0.0
        self._last_humi = 0.0

    def _read(self):
            if self.pin == "":
                print("No olvides indicar el GPIO")
            else:
                GPIO.setup(self.pin,GPIO.OUT)
              
                GPIO.output(self.pin,GPIO.HIGH)
                time.sleep(.2)

                GPIO.output(self.pin,GPIO.LOW)
                time.sleep(.018)

                GPIO.setup(self.pin,GPIO.IN)
               
                
                # a short delay needed
                for i in range(10):
                    pass

                # pullup by host 20-40 us
                count = 0
                while GPIO.input(self.pin):
                    count += 1
                    if count > self.MAX_CNT:
                        #print("pullup by host 20-40us failed")
                        return None, "pullup by host 20-40us failed"

                pulse_cnt = [0] * (2 * self.PULSES_CNT)
                fix_crc = False
                for i in range(0, self.PULSES_CNT * 2, 2):
                    while not GPIO.input(self.pin):
                        pulse_cnt[i] += 1
                        if pulse_cnt[i] > self.MAX_CNT:
                            #print("pulldown by DHT timeout %d" % i)
                            return None, "pulldown by DHT timeout %d" % i
                    
                    while GPIO.input(self.pin):
                        pulse_cnt[i + 1] += 1
                        if pulse_cnt[i + 1] > self.MAX_CNT:
                            #print("pullup by DHT timeout %d" % (i + 1))
                            if i == (self.PULSES_CNT - 1) * 2:
                                # fix_crc = True
                                # break
                                pass
                            return None, "pullup by DHT timeout %d" % i


                total_cnt = 0
                for i in range(2, 2 * self.PULSES_CNT, 2):
                    total_cnt += pulse_cnt[i]

                # Low level ( 50 us) average counter
                average_cnt = total_cnt / (self.PULSES_CNT - 1)
                # print("low level average loop = %d" % average_cnt)
            
                data = ''
                for i in range(3, 2 * self.PULSES_CNT, 2):
                    if pulse_cnt[i] > average_cnt:
                        data += '1'
                    else:
                        data += '0'
                
                data0 = int(data[ 0: 8], 2)
                data1 = int(data[ 8:16], 2)
                data2 = int(data[16:24], 2)
                data3 = int(data[24:32], 2)
                data4 = int(data[32:40], 2)

                if fix_crc and data4 != ((data0 + data1 + data2 + data3) & 0xFF):
                    data4 = data4 ^ 0x01
                    data = data[0: self.PULSES_CNT - 2] + ('1' if data4 & 0x01 else '0')

                if data4 == ((data0 + data1 + data2 + data3) & 0xFF):
                    humi = int(data0)
                    temp = int(data2)

                else:
                    return None, "0"

                return humi, temp

    def read(self, retries = 15):
        for i in range(retries):
            humi, temp = self._read()
            if not humi is None:
                break
        if humi is None:
            return self._last_humi, self._last_temp
        self._last_humi,self._last_temp = humi, temp
        return humi, temp



