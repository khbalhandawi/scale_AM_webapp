# web app packages
# from asyncio.windows_events import NULL
import requests
from flask import Flask, render_template, redirect, session, url_for, request, jsonify
from werkzeug.wrappers import Request, Response
import os
import csv

import codecs, json 

# for data loading and transformation
import numpy as np 
import pandas as pd

# models
from scale_AM.src.surrogateLib import KSModel
from scale_AM.src.scaleLib import scalability

# to bypass warnings in the jupyter notebook
import warnings
warnings.filterwarnings("ignore",category=UserWarning)
warnings.filterwarnings("ignore",category=DeprecationWarning)
warnings.filterwarnings("ignore",category=FutureWarning)
warnings.filterwarnings("ignore",category=PendingDeprecationWarning)

app=Flask(__name__,template_folder="./templates/")
app.config["DEBUG"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["FILE_UPLOADS"] = "./static/file/uploads"
app.config["SECRET_KEY"] = "Your_secret_string"    
app.config["SESSION_TYPE"] = "filesystem"
############################ MAIN INITIALIZATION #############################

##############################################################################

# instantiate index page
@app.route("/",methods = ["POST","GET"])
def index():
	if request.method == "POST":
		# Create variable for uploaded file
		f = request.files["filename"]  
		filepath = os.path.join(app.config["FILE_UPLOADS"], f.filename)
		f.save(filepath)

		#store the file contents as a string
		# f = open(filepath, "r")
		# fstring = [l.decode("utf-8").split(",") for l in f.read().splitlines()]
		# df = pd.DataFrame(data=fstring[1:],columns=fstring[0]
		df = pd.read_csv(filepath)

		input_columns = []; output_columns = []
		dict_in = {}; dict_out = {}
		for col in df.columns:
			if len(col) > 0:
				if col[0] == "x":
					input_columns += [col]
					dict_in[col] = list(df[col])
				if col[0] == "f":
					output_columns += [col]
					dict_out[col] = list(df[col])

		# store variables in the session
		session["nx"] = len(dict_in)
		session["input_columns"] = input_columns
		session["nf"] = len(dict_out)
		session["output_columns"] = output_columns
		session["filepath"] = filepath
		return redirect(request.referrer)

	if request.method == "GET":
		return render_template("index.html")  

# get problem size
@app.route("/api/define", methods=["POST"])
def get_map():
		if session.get("nx") and session.get("nf"):
			nx = session.get("nx")
			nf = session.get("nf")
			dims = {"nx" : nx, "nf" : nf}
			return jsonify(dims)

# return model predictions
@app.route("/api/predict", methods=["GET","POST"])
def predict():

	# Read data
	data_df = pd.read_csv(session["filepath"])

	msg_data={}
	print("======================================")
	jsonData = request.get_json()
	print(jsonData)

	x = np.array(data_df[session["input_columns"]])
	f = np.array(data_df[session["output_columns"]])

	model = KSModel("PSpace")
	model.train(x,f,bandwidth=float(jsonData["bandwidth"]))
	# model.view([0,1],0)

	# scalability assessment
	x1_i = jsonData["x-axis"]
	x2_i = jsonData["y-axis"]
	z_i = jsonData["z-axis"]

	p = np.array(jsonData["change_effect"],dtype=float)
	m = np.array(jsonData["monotonicity"],dtype=float)
	s = scalability(p,m,model,"Himmelblau")
	X,Y,Z,F,grad_F = s.compute_scalability([x1_i,x2_i],z_i,n_levels=15)

	J = np.array(jsonData["Jacobian"]).reshape((session["nx"],session["nf"]))

	cstrs = []
	for i in range(J.shape[0]):	
		for j in range(J.shape[1]):
			if J[i,j]:
				c = np.zeros(s.cstrs[(i,j)].shape)
				c[s.cstrs[(i,j)]] = 1
				c[~s.cstrs[(i,j)]] = 0
				c = c.reshape(Z.shape).tolist()
				for i in range(Z.shape[0]):
					for j in range(Z.shape[1]):
						c[i][j] = c[i][j] if c[i][j] == 1 else 0
				cstrs += [c]

	if x1_i < x2_i:
		x_vector=X[:,0]
		y_vector=Y[0,:]
		Z = Z.T
	else:
		x_vector=X[0,:]
		y_vector=Y[:,0]

	return jsonify(x=x_vector.tolist(),y=y_vector.tolist(),z=Z.tolist(),cstrs=cstrs)   

if __name__ == "__main_":
	app.config["DEBUG"] = True
	from werkzeug.serving import run_simple
	run_simple("localhost", 5000, app)