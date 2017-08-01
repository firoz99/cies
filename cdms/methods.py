import cv2


def detect_n_predict(url):
	face_cascade = cv2.CascadeClassifier("media/xmls/haarcascade_frontalface_default.xml")
	recognizer = cv2.createLBPHFaceRecognizer()
	recognizer.load("media/xmls/trainingData.yml")

	img = cv2.imread(url)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
	IDs = []
	x=0
	y=0
	w=0
	h=0
	ID = 0
	for (x, y, w, h) in faces:
		cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
		img2 = gray[y:y+h, x:x+w]
		img2 = cv2.resize(img2, (128, 128))
		ID, conf = recognizer.predict(img2)
		IDs.append(ID)
	
	return IDs