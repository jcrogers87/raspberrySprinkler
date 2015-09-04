import webiopi
import time
import datetime

GPIO = webiopi.GPIO
POWER = 8 #GPIO Pin that reports weather
TIME = 1 #time in minutes to run
zoneList = [9, 10, 11, 25]

for x in zoneList:
	GPIO.setFunction(x, GPIO.OUT)



ts = time.time()
print datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def Run():
		if GPIO.digitalRead(POWER) == True: #check if it's okay to water
			print "No rain in forecast. Beginning watering cycle for " + str(TIME) +" minutes"
			for x in zoneList:
				GPIO.digitalWrite(x, GPIO.HIGH) 

			time.sleep(TIME * 60) #sleep minutes

			for x in zoneList:
				GPIO.digitalWrite(x, GPIO.LOW) 
		else: 
			print "Rain is in the forecast, no watering today."

Run()

