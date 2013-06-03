#flask Framework
from flask import Flask, jsonify, render_template, request
app = Flask(__name__)

#these lines import SQLite - for the database, and CV2 - for the webcam, 
import sqlite3 as lite
import os
import sys
import cv2
import pyaudio
import wave

#establishes a connection to the DB
con = None
con = lite.connect('inDB.db', check_same_thread = False) 

#sets cur to be a cursor
with con:
    cur = con.cursor()    	
	
#THESE. ARE. MY. Functions!
@app.route('/')
def index():
    return render_template('index.html')
	
@app.route('/claimSave/')
def claimSave():
#gets information from the webpage and sets it into the DBdata Dictionary...
	DBdata = {"Type": request.args.get('pyClaimType'),
	"Amount": request.args.get('pyClaimAmt'),
	"Date": request.args.get('pyClaimDate'),
	"Desc": request.args.get('pyClaimDesc')}
	#this sets the insert string for the database
	insertString = 'INSERT INTO claims VALUES("%s", "%s", "%s", "%s")' %(DBdata['Type'], DBdata['Amount'], DBdata['Date'], DBdata['Desc'])
	with con:
	#actually inserts the insertString into the database
		cur.execute(insertString)
		#prints confirmation
		print "Claim successfully Added"
		#Returns nothing, because I don't know any other way to do this.
		return ""

@app.route('/validation/')
def validation():
#gets the userID and passwword form the page
	DBdata = {"Name": request.args.get('pyAccName'), "Password": request.args.get('pyAccPass')}
	#sets and executes the query string
	queryString = 'select userid and password from accounts where userid is "%s" and password is "%s"' %(DBdata['Name'], DBdata['Password'])
	cur.execute(queryString)
	#stores the results of the query into a var
	results = cur.fetchall()
	results = str(results)
	#checks to see if the results were null or not null.
	if str(results) != '[]':
		loggedIn = 'true'
		print "Login successful!"
	else:
		loggedIn = 'false'
		print "login unsuccessful :("
		#returns the var loggedIn for use in HTML
	return loggedIn

@app.route('/saveVideo/')
def saveVideo():
	exit = False
	#stuff for microphone recording
	p = pyaudio.PyAudio()
	
	home_dir = os.path.expanduser("~")
	
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RATE = 10000
	WAVE_OUTPUT_FILENAME = home_dir + "/output.wav"
	
	stream = p.open(format = FORMAT,
                channels = CHANNELS, 
                rate = RATE, 
                input = True,
                output = True,
                frames_per_buffer = CHUNK)
				
	
	
	print "* recording"
	#captures video until esc is pressed
	
	frames = []
	while exit != True:
	
	#the 0 means live feed from a webcam
		cam = cv2.VideoCapture(0)
		s, img = cam.read()
		winName = "Big Brother is watching!"
		cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)
		#the writing writer writes the movie to the hard drive
		writer = cv2.VideoWriter(home_dir + "/movie.avi", cv2.cv.CV_FOURCC('i','Y','U','V'), 10,(640, 480))
		
		while s:		
		#this displays the video being recorded in a window
			cv2.imshow( winName,img )
			s, img = cam.read()
			#here is where the writing writer writes. Individual frames at 24 fps.
			writer.write(img)	
			
			data = stream.read(CHUNK)
			frames.append(data)
			
			wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
			wf.setnchannels(CHANNELS)
			wf.setsampwidth(p.get_sample_size(FORMAT))
			wf.setframerate(RATE)
			wf.writeframes(''.join(frames))
			
			#key 27 is esc
			key = cv2.waitKey(10)
			if key == 27:
				cv2.destroyWindow(winName)	
				print "recording is finished!"
				stream.stop_stream()
				stream.close()
				p.terminate()
				
				
				wf.close()

				print "Goodbye"
				exit=True
				break
				
		return ""
#These lines keep the server running
if __name__ == '__main__':
    app.run(port=5000, debug=True)
