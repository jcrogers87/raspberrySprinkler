import webiopi
import time
import datetime

GPIO = webiopi.GPIO
POWER = 8 #GPIO Pin that reports weather
TIME = 1 #time in minutes to run
zoneOne = 2
zoneTwo = 3 
zoneThree = 4
zoneFour = 17
zoneFive = 27

GPIO.setFunction(zoneOne, GPIO.OUT)
GPIO.setFunction(zoneTwo, GPIO.OUT)
GPIO.setFunction(zoneThree, GPIO.OUT)
GPIO.setFunction(zoneFour, GPIO.OUT)
GPIO.setFunction(zoneFive, GPIO.OUT)

ts = time.time()
print datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def Run():
		if GPIO.digitalRead(POWER) == True: #check if it's okay to water
			print "No rain in forecast. Beginning watering cycle for " + str(TIME) +" minutes"
			GPIO.digitalWrite(zoneOne, GPIO.HIGH)
			GPIO.digitalWrite(zoneTwo, GPIO.HIGH)
			GPIO.digitalWrite(zoneThree, GPIO.HIGH)
			GPIO.digitalWrite(zoneFour, GPIO.HIGH)
			GPIO.digitalWrite(zoneFive, GPIO.HIGH)

			time.sleep(TIME * 60) #sleep minutes

			GPIO.digitalWrite(zoneOne, GPIO.LOW) 
			GPIO.digitalWrite(zoneTwo, GPIO.LOW)
			GPIO.digitalWrite(zoneThree, GPIO.LOW)
			GPIO.digitalWrite(zoneFour, GPIO.LOW)
			GPIO.digitalWrite(zoneFive, GPIO.LOW)
		else: 
			print "Rain is in the forecast, no watering today."

Run()

