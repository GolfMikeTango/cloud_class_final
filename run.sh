pip install wheel
pip install -r requirements.txt
nohup waitress-serve --call 'flaskapp:create_app' | tee log.txt &