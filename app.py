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
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["FILE_UPLOADS"] = "./tmp"
app.config["SECRET_KEY"] = "Your_secret_string"    
app.config["SESSION_TYPE"] = "filesystem"
############################ MAIN INITIALIZATION #############################

##############################################################################

# instantiate index page
@app.route("/",methods = ["POST","GET"])
def index():
	if request.method == "POST":
		# Create variable for uploaded file
		os.makedirs("tmp", exist_ok=True)
		f = request.files["filename"]  
		filepath = os.path.join(app.config["FILE_UPLOADS"], f.filename)
		f.save(filepath)

		#store the file contents as a string
		# f = open(filepath, "r")
		# fstring = [l.decode("utf-8").split(",") for l in f.read().splitlines()]
		# df = pd.DataFrame(data=fstring[1:],columns=fstring[0]
		df = pd.read_csv(filepath)

		n_inputs = max(2,int(request.form["n_inputs"]))
		n_outputs = max(1,int(request.form["n_outputs"]))

		if n_inputs + n_outputs > len(df.columns):
			n_inputs = len(df.columns) - 1
			n_outputs = 1

		input_columns = []; output_columns = []
		dict_in = {}; dict_out = {}
		for col in df.columns[1:n_inputs+1]:
			input_columns += [col]
			dict_in[col] = list(df[col])

		for col in df.columns[n_inputs+1:n_inputs+n_outputs+1]:
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
		input_columns = session.get("input_columns")
		output_columns = session.get("output_columns")
		dims = {"nx" : nx, "nf" : nf, "i_labels" : input_columns, "o_labels" : output_columns}
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
	resolution = int(jsonData["resolution"])
	intersect = bool(jsonData["intersect"])

	p = np.array(jsonData["change_effect"],dtype=float)
	m = np.array(jsonData["monotonicity"],dtype=float)
	s = scalability(p,m,model,"Himmelblau")
	X,Y,Z,F,grad_F = s.compute_scalability([x1_i,x2_i],z_i,n_levels=resolution)

	J = np.array(jsonData["Jacobian"]).reshape((session["nx"],session["nf"]))

	if not intersect:
		cstrs = []
		for i in range(J.shape[0]):	
			for j in range(J.shape[1]):
				if J[i,j]:
					c = np.zeros(s.cstrs[(i,j)].shape)
					c[s.cstrs[(i,j)]] = None
					c[~s.cstrs[(i,j)]] = 1

					c_lines = np.zeros(s.cstrs[(i,j)].shape)
					c_lines[s.cstrs[(i,j)]] = 1
					c_lines[~s.cstrs[(i,j)]] = 0

					if x1_i < x2_i:
						c = c.reshape(Z.shape).T.tolist()
						c_lines = c_lines.reshape(Z.shape).T.tolist()
					else:
						c = c.reshape(Z.shape).tolist()
						c_lines = c_lines.reshape(Z.shape).tolist()
					for ii in range(Z.shape[0]):
						for jj in range(Z.shape[1]):
							c[ii][jj] = c[ii][jj] if c[ii][jj] == 1 else None
							c_lines[ii][jj] = c_lines[ii][jj] if c_lines[ii][jj] == 1 else 0
					cstrs += [{"values":c,"values_line":c_lines,"label":"J%i%i"%(i+1,j+1),"order":(i*J.shape[1]+j)}]
	else:
		cstrs = []
		arrays = ()
		for i in range(J.shape[0]):	
			for j in range(J.shape[1]):
				if J[i,j]:
					arrays += (s.cstrs[(i,j)],)
					
		c_bool = np.logical_or.reduce(arrays)

		c = np.zeros(c_bool.shape)
		c[c_bool] = None
		c[~c_bool] = 1

		c_lines = np.zeros(c_bool.shape)
		c_lines[c_bool] = 1
		c_lines[~c_bool] = 0

		if x1_i < x2_i:
			c = c.reshape(Z.shape).T.tolist()
			c_lines = c_lines.reshape(Z.shape).T.tolist()
		else:
			c = c.reshape(Z.shape).tolist()
			c_lines = c_lines.reshape(Z.shape).tolist()
		for ii in range(Z.shape[0]):
			for jj in range(Z.shape[1]):
				c[ii][jj] = c[ii][jj] if c[ii][jj] == 1 else None
				c_lines[ii][jj] = c_lines[ii][jj] if c_lines[ii][jj] == 1 else 0
		cstrs += [{"values":c,"values_line":c_lines,"label":"scalable region","order":0}]


	if x1_i < x2_i:
		x_vector=X[:,0]
		y_vector=Y[0,:]
		Z = Z.T
	else:
		x_vector=X[0,:]
		y_vector=Y[:,0]

	labels = {
		"xlabel" : session.get("input_columns")[x1_i],
		"ylabel" : session.get("input_columns")[x2_i],
		"zlabel" : session.get("output_columns")[z_i],
	}
	return jsonify(x=x_vector.tolist(),y=y_vector.tolist(),z=Z.tolist(),cstrs=cstrs,labels=labels)   

@app.route("/download/")
def download():
    return render_template("download.html")

if __name__ == "__main_":
	app.debug = False
	from werkzeug.serving import run_simple
	run_simple("localhost", 5000, app)