#!bin/bash
source .env/Scripts/activate.bat
echo off
export FLASK_APP=app
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run -p 5000