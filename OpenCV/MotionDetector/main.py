# IMPORT NECESSARY PACKAGES
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from imgsearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import pytz
import imutils
import json
import time
import cv2
 
# ARGUMENT PARSER
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, default="/root/OpenCV/MotionDetector/conf.json",
	help="PATH TO THE JSON CONFIGURATION FILE")
args = vars(ap.parse_args())
 
# FILTER WARNINGS AND LOAD CONFIGURATION FILE
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
client = None

if conf["use_dropbox"]:
	# CONNECT TO DROPBOX AND AUTHENTICATE
	flow = DropboxOAuth2FlowNoRedirect(conf["dropbox_key"], conf["dropbox_secret"])
	print "[INFO] AUTHORIZE THE APP... {}".format(flow.start())
	authCode = raw_input("ENTER AUTH CODE: ").strip()
 
	# FINISH AUTH AND GRAB CLIENT
	(accessToken, userID) = flow.finish(authCode)
	client = DropboxClient(accessToken)
	print "[SUCCESS] DROPBOX ACCOUNT LINKED"

# INITIALIZE CAMERA AND REFERENCE IT TO RAWCAPTURE
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))
 
# CAMERA WARMUP AND LAST IMG UPLOADED TIMESTAMP
print "[INFO] WARMING UP CAMERA..."
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

# FRAMES CAPTURE
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# SET ARRAY AND CLEAR TEXT VARIABLE
	frame = f.array
	timestamp = datetime.datetime.now(pytz.timezone('America/Mexico_City'))
	text = ""
 
	# GREYSCALE AND BLUR
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
 
	# INITIALIZE FRAME IF NOT INITIALIZED
	if avg is None:
		print "[INFO] STARTING FEEDBACK STREAMING..."
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue
 
	# ACCUMULATE WEIGHT OF CURRENT FRAME AND COMPUTE DIFFERENCE
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	# THRESHOLD IMAGE, FILL HOLES AND FIND CONTOURS TO DRAW
	thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
		cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
 
	# LOOP CONTOURS
	for c in cnts:
		# IF SMALL IGNORE IT
		if cv2.contourArea(c) < conf["min_area"]:
			continue
 
		# DRAW CONTOUR AND SET TEXT
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
		text = "MOTION DETECTED"
 
	# DRAW TEXT AND TIMESTAMP
	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame, "{}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (255, 255, 255), 1)

	# IF MOTION DETECTED
	if text == "MOTION DETECTED":
		# ENOUGH TIME BETWEEN UPLOADS? ###DISABLED TO USE TIMEZONE###
		# if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:

		# ++ MOTION COUNTER ###UNINDENTED ONCE BECAUSE OF ABOVE###
		motionCounter += 1
 
		# CHECK IF MOTION IS HIGH ENOUGH
		if motionCounter >= conf["min_motion_frames"]:
			# DROPBOX?
			if conf["use_dropbox"]:
				# WITE TO TMP
				t = TempImage()
				cv2.imwrite(t.path, frame)
 					# UPLOAD AND CLEAN
				print "[UPLOAD] {}".format(ts)
				path = "{base_path}/{timestamp}.jpg".format(
					base_path=conf["dropbox_base_path"], timestamp=ts)
				client.put_file(path, open(t.path, "rb"))
				t.cleanup()

			# RESET COUNTER AND UPDATE TIMESTAMP
			lastUploaded = timestamp
			motionCounter = 0

	# NO MOTION DETECTED
	else:
		motionCounter = 0

	# FRAMES DISPLAYED?
	if conf["show_video"]:
		# DISPLAY STREAMING
		cv2.imshow("REMOTE STREAMING", frame)
		key = cv2.waitKey(1) & 0xFF
 
		# QUIT IF "Q" KEY PRESSED
		if key == ord("q"):
			break
 
	# CLEAR STREAM FOR NEXT FRAME
	rawCapture.truncate(0)
