import torch
import torch.nn as nn
import torchvision
import dlib
import numpy as np
import logging


model = None
transform = None
cnn_face_detector = None
shape_predictor = None
device = None


race_map = {
	0: "White",
	1: "Black",
	2: "Latino_Hispanic",
	3: "East Asian",
	4: "Southeast Asian",
	5: "Indian",
	6: "Middle Eastern"
}

gender_map = {
	0: "Male",
	1: "Female",
}

age_map = {
	0: "0-2",
	1: "3-9",
	2: "10-19",
	3: "20-29",
	4: "30-39",
	5: "40-49",
	6: "50-59",
	7: "60-69",
	8: "More than 70",
}


def init():
	global model
	global transform
	global cnn_face_detector
	global shape_predictor
	global device

	transform = torchvision.transforms.Compose([
	    torchvision.transforms.ToPILImage(),
	    torchvision.transforms.Resize((224, 224)),
	    torchvision.transforms.ToTensor(),
	    torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

	device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
	logging.info("Using device {}".format(device))
	#device = torch.device("cpu")

	model = torchvision.models.resnet34(pretrained=False)
	model = model.to(device)
	model.fc = nn.Linear(model.fc.in_features, 18)
	model.load_state_dict(torch.load('data/res34_fair_align_multi_7_20190809.pt')) # , map_location='cpu'
	model = model.to(device)
	model.eval()

	cnn_face_detector = dlib.cnn_face_detection_model_v1('data/mmod_human_face_detector.dat')
	shape_predictor = dlib.shape_predictor('data/shape_predictor_5_face_landmarks.dat')


def load_and_predict(image_path):
	try:
		face_rows = []

		img, width, height = load_image(image_path)
        
		dets = cnn_face_detector(img, 1)
		
		if len(dets) > 0:
			for i, d in enumerate(dets):
				top,bottom,left,right = max(d.rect.top(), 0), max(d.rect.bottom(), 0), max(d.rect.left(), 0), max(d.rect.right(), 0)
				faces = dlib.full_object_detections()
				rect = dlib.rectangle(left, top, right, bottom)
				faces.append(shape_predictor(img, rect))
				images = dlib.get_face_chips(img, faces, size=224, padding=0.25)

				
				# Make prediction
				race,gender,age = predict(images[0])

				result = {
                	"rectangle": {
                		"top": top / height,
                		"height": (bottom-top) / height,
                		"left": left / width,
                		"width": (right-left) / width,
                	},
                	"attributes": {
                		"gender": gender,
                		"age": age,
                		"race": race
                	}
                }
				face_rows.append(result)
		return face_rows

    
	# catch invalid image type error
	except Exception as e:
		logging.warn("Exception: {}".format(e))
		return []


def load_image(image_path):
	img = dlib.load_rgb_image(image_path)

	height, width = img.shape[0], img.shape[1]

	max_size = 2000

	# if height or width >= max_size, recale
	if height >= width and height > max_size:
		scale = height / max_size
		height = max_size
		width = int(width / scale)         
		img = dlib.resize_image(img = img, rows = height, cols = width)

	elif width > height and width > max_size:
		scale = width / max_size
		width = max_size
		height = int(height / scale)         
		img = dlib.resize_image(img = img, rows = height, cols = width)

	return img, width, height


def predict(image):
	image = transform(image)
	image = image.view(1, 3, 224, 224) # reshape image to match model dimensions (1 batch size)
	image = image.to(device)

	outputs = model(image)
	outputs = outputs.cpu().detach().numpy()
	outputs = np.squeeze(outputs)
    
	race_outputs = outputs[:7]
	gender_outputs = outputs[7:9]
	age_outputs = outputs[9:18]
    
	race_score = np.exp(race_outputs) / np.sum(np.exp(race_outputs))
	gender_score = np.exp(gender_outputs) / np.sum(np.exp(gender_outputs))
	age_score = np.exp(age_outputs) / np.sum(np.exp(age_outputs))
    
	race_pred = np.argmax(race_score)
	gender_pred = np.argmax(gender_score)
	age_pred = np.argmax(age_score)

	return race_map[race_pred], gender_map[gender_pred], age_map[age_pred]