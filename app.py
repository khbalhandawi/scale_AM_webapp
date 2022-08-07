# web app packages
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

app=Flask(__name__,template_folder='./templates/')
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
		session["nf"] = len(dict_out)
		return redirect(request.referrer)

	if request.method == "GET":
		return render_template("index.html")  

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
	msg_data={}
	print("======================================")
	jsonData = request.get_json()
	for k in jsonData.keys():
		val=jsonData.get(k)
		msg_data[k]=val

	input_df=pd.DataFrame(msg_data)
	print(input_df)

	# # Get X values from dataframe
	# N_cases_in = np.reshape(input_df["ncases"].to_numpy(dtype=float),(len(input_df),1))
	# Ct_in = np.reshape(input_df["Ct"].to_numpy(dtype=float),(len(input_df),1))

	# # Standardize X values and convert to tensor
	# data_X = (np.concatenate((N_cases_in,Ct_in,),axis=1) - mean_in.to_numpy())/ std_in.to_numpy()
	# data_X = torch.from_numpy(data_X).unsqueeze(0).float()

	# # Set first value of Y tensor to last N_cases (yesterday) and standardize
	# data_y = torch.ones((1,OUTPUT_DIM+1,NUM_FEATURES_OUT)) * N_cases_in[-1]
	# data_y[:,1:,:] =  np.NaN
	# data_y = (data_y - mean_out.to_numpy())/ std_out.to_numpy()
	# data_y = data_y.float()

	# # Perform inference
	# [pred_mean, data_y_mean, pred_seq] = TestRun.predict(data_X.to(device), data_y.to(device), mean=mean_out, std=std_out, return_seq=True)

	# projection = pred_seq.squeeze().numpy().round().tolist()
	# mean_pred = np.mean(projection)
	# sum_pred = np.sum(projection)
	# print("projection:")
	# print(projection)
	# print("average:")
	# print(mean_pred)
	# print("======================================")

	# # file_path = "models/Y_response.json"
	# # json.dump(projection, codecs.open(file_path, "w", encoding="utf-8"), separators=(",", ":"), sort_keys=True, indent=4) ### this saves the array in .json format

	# return jsonify(projection=projection,average=mean_pred,sum=sum_pred)   

if __name__ == "__main_":
	app.config["DEBUG"] = True
	from werkzeug.serving import run_simple
	run_simple("localhost", 5000, app)