# raspberrySprinkler
This project allows control of a number of "zones" using WebIOPi and a little python. Thanks to thirdeyevis for the start on some code, and the idea.

  Instructions:

1. Install raspbian on your Pi
  https://www.raspberrypi.org/documentation/installation/installing-images/README.md

2. Install WebIOPi
  http://webiopi.trouch.com/INSTALL.html

3. Copy the sprinklers.html file to the WebIOPi doc-root "HTML" directory (default: /usr/share/webiopi/htdocs/)
  
4. Edit the integers in the js to change the active GPIO pins: 
  var btnZone1 = webiopi().createGPIOButton(2, "Zone 1");
  var weatherCheck.. needs to be changed to the pin that will be assigned to the bypass script (more below)

  You should now be able to turn on and off the "zones" via the WebIOPi interface: http://raspi.home:8000/sprinklers.html
  
4. Clone the sprinklerCon.py file to ~/ 

5. chmod the file (chmod +x sprinklerCon.py) 

6. Add an entry in crontab for sprinklerCon.py : 0 8 * * 1,3,6 root /usr/bin/python /scripts/sprinklerCon.py >> /var/log/sprinklers.log

7. Clone the "rain-bypass.py file into a working directory. Edit the "POWER" variable to assign a pin that will allow watering. Thanks to http://www.thirdeyevis.com/pi-page-3.php for the initial script. 

8. Chmod the rain-bypass file (chmod +x rain-bypass.py)

9. Create a Wunderground Developer account and make note of your "key". This needs to be added to the rain-bypass.py script on line 14.

10. Execute the file for the first time and follow the prompts. (it will create a cfg file)

11. Add an entry into rc.local to start the rain-bypass on system start: /usr/bin/python /media/tank/files/pi/projects/sprinkler/rain-bypass.py &

12. Using a "2N2222" transitor, create a circuit that will allow a "low" gpio signal to turn off a standard sainsmart relay.
  https://docs.google.com/file/d/0B5-HND9HJkXWSTQtYlFTZ3VyODA/edit

13. Wire the relay to your circuit. 
  http://www.sainsmart.com/sainsmart-relay-module-for-arduino-raspberry-pi.html

14. Reboot

The result should be a working webpage to control your GPIO pins per "zone" manually, a cron job that will start the zones only if the weather permits, and a log file being generated with the weeks forecast.

Plans: 
  1. Integrate some weather sensors/webcam into the mix for display on the sprinklers.html webpage
  2. rewrite the java in the sprinklers.html file (my java is very rusty) 
