import urllib2
import json
import time
import datetime
import os

from sys import argv
import webiopi
GPIO = webiopi.GPIO
POWER = 8 #Change this integer to match the control pin

GPIO.setFunction(POWER, GPIO.OUT)

wundergroundKey = "12345abcde" ## Enter your Wunderground key acquired by joining weather underground api program
lastRain = 0 ## Hold epoch of last rain - float
checkIncrement = 0  ## Amount of time between weather.com forecast requests - integer
daysDisabled = 0 ## Days to disable systems prior to and after rain - integer
zipCode = 0 ## Zip code for weather request - integer
rainForecasted = False ## Is rain forecasted within daysDisabled forecast range - Boolean, global

## Define conditions that will disable watering.  This includes Light/Heavy prefix on any of the following conditions
## Weather.com Condition Phrases: http://www.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary
possibleConditions = ["Rain",
                      "Rain Showers",
                      "Thunderstorm",
                      "Thunderstorms and Rain",
                      ]

## Prefix each possible condition with 'Heavy' and 'Light', since these are possible conditions
for x in possibleConditions[:]: ## Use slice notation to iterate loop inside slice copy of list
    possibleConditions.insert(0,'Light ' + x)
    possibleConditions.insert(0,'Heavy ' + x)

##This funtion gets the path of this file.  When run at startup, we need full path to access config file
##To run this file automatically at startup, change permission of this file to execute
##If using wireless for network adapter, make sure wireless settings are configured correctly in wlan config so wifi device is available on startup
##edit /etc/rc.local file 'sudo pico /etc/rc.local'
##add "python /home/pi/working-python/weather-json.py &" before line "exit 0"
def GetProgramDir():
   try:  ## If running from command line __file__ path is defined
      return os.path.dirname(os.path.abspath(__file__)) + "/"
   except:  ## If __file__ is undefined, we are running from idle ide, which doesn't use this var
      return os.getcwd() + "/"

## Load values from config file, or create it and get values
try: ## see if config file exists
	configFile = open(GetProgramDir() + "rain-bypass.cfg","r")  ## Attempt to open existing cfg file
	print "Config file found, loading previous values..."
	zipCode = int(configFile.readline()) ## Convert zip to int to remove unicode formatting, store in zipCode
	daysDisabled = int(configFile.readline()) ## Convert second line to int and store in daysDisabled var
	checkIncrement = int(configFile.readline()) ## Conver third line to int and store in checkIncrement variable
	configFile.close()
	
except: ## Exception: config file does not exist, create new
    WriteLog("Config file not found, creating new...")
    print "Config file not found, creating new..."

    ## Request zip code for request
    zipCode = int(raw_input("Enter Zip Code: "))

    ## input number of days system will be disabled prior to rain, and after rain
    daysDisabled = int(raw_input("Enter number of days to disable system prior/after rain (between 1 and 9): "))

    ## request number of checks in 24 hour period
    checkIncrement = int(raw_input("Enter number of times you want to check forecast per 24-hour period (no more than 500, try 24, or once per hour): "))
    checkIncrement = 86400/checkIncrement ## This is the wait interval between each check in seconds
    
    ## Save user input to new config file
    configFile = open(GetProgramDir() + "rain-bypass.cfg","w")
    configFile.write(str(zipCode) + "\n" + str(daysDisabled) + "\n" + str(checkIncrement) + "\n") ## Write each item to new line
    configFile.close()

def WriteLog(value):
	logName = GetProgramDir() + "rain-bypass.log"
	logSize = os.path.getsize(logName)
	if logSize >  102400: #keep the log file size under control
		os.remove(logName)
	logFile = open(logName,"a")
	ts = time.time()
	logFile.write(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') + " : " + value + "\n")
	logFile.close()
	#print value

	
## Show values/interval used to check weatherc
WriteLog("Checking forecast for zip code: " + str(zipCode))
print "Checking forecast for zip code: " + str(zipCode)
print "System will be disabled for " + str(daysDisabled) + " days prior to and after rain"
print "System will wait " + str(checkIncrement) + " seconds between checks"
print "     or " + str(float(checkIncrement) / 60) + " minute(s) between checks"
print "     or " + str(float(checkIncrement) / 3600) + " hour(s) between checks"

def CheckWeather():

    ## This function will modify the following variables in the main scope
    global rainForecasted
    global lastRain
    
    while True: ## Loop this forever
        try:
            ##Request Weather Data
            request = urllib2.Request("http://api.wunderground.com/api/" + wundergroundKey +"/forecast10day/q/" + str(zipCode) + ".json") ## 10-day forecast
            response = urllib2.urlopen(request)

            ## Create array to hold forecast values
            dateArray = []

            ## Parse XML into array with only pretty date, epoch, and conditions forecast
            jsonData = json.load(response)
            for x in jsonData['forecast']['simpleforecast']['forecastday']:
                dateArray.append([x['date']['pretty'],x['date']['epoch'],x['conditions']])
            
            WriteLog("Current Forecast for current day, plus next 9 is:")
            for x in dateArray:
                WriteLog(x[0] + ", " + x[1] + ", " + x[2])
                #print x[0] + ", " + x[1] + ", " + x[2]

            ##Check current day for rain
            WriteLog("### START Checking if raining TODAY ###")
            if(CheckCondition(dateArray[0][2])): ## If is raining today
				lastRain = float(dateArray[0][1]) ## Save current rain forecast as last rain globally
				WriteLog("It will rain today. Storing current epoch as 'last rain': " + str(lastRain))
				#print "It will rain today. Storing current epoch as 'last rain': " + str(lastRain)
            else:
                WriteLog("No rain today")
                WriteLog("### END Checking if raining now ###\n")

            ##Check if rain is forecast within current range
            WriteLog("### START Checking for rain in forecast range ###")  
            for x in range(1, daysDisabled+1):
                WriteLog("Checking " + dateArray[x][0] + " for rain conditions:")
                if(CheckCondition(dateArray[x][2])):
                   WriteLog("Rain has been forecast. Disabling watering" )
                   rainForecasted = True ##Set global variable outside function scope
                   break
                else:
					WriteLog("No rain found for current day. Watering may commence")
					rainForecasted = False ##Set global variable outside function scope
            WriteLog("### END Checking if rain in forecast ###\n")

            ## Now that we know current conditions and forecast, modify watering schedule
            ModifyWatering()
			
            WriteLog("Checking forecast again in " + str(checkIncrement / 60) + " minute(s)")
            time.sleep(checkIncrement)
            
        except: ## Data unavailable - either connection error, or network error
            WriteLog("Error contacting weather.com. Trying again in " + str(checkIncrement / 60) + " minute(s)")
            time.sleep(checkIncrement)  ## Reattempt connection in 1 increment

def CheckCondition(value):
    for x in possibleConditions:
        if value == x:
            WriteLog('Rain condition found')		
            return True

def ModifyWatering():
    WriteLog("Last rain from forecast timestamp: " + str(lastRain))
    WriteLog("Current Time: " + str(time.time()))
    WriteLog("Days since last rain: " + str((time.time() - lastRain)/86400 ))
    WriteLog("Seconds since last rain: " + str(time.time() - lastRain))
    WriteLog("Days disabled in seconds: " + str(daysDisabled * 86400))
    WriteLog("Has NOT rained within daysDisabled range: " + str(time.time() - lastRain >= daysDisabled * 86400))

    if(rainForecasted == False and time.time() - lastRain >= daysDisabled * 86400):
		WriteLog("Hasn't rained in a while, and not expected to rain. Watering enabled.")
		GPIO.digitalWrite(POWER, GPIO.HIGH)
    else:
        GPIO.digitalWrite(POWER, GPIO.LOW)
        if(rainForecasted):
            WriteLog("Rain has been forecast. Disabling watering" )
        else:
            WriteLog("Rain not in forecast, but it has rained recently. Watering Disabled")
	
## Init Forecast method
CheckWeather()
