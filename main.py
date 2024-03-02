from flask import Flask, render_template, jsonify
import csv
import datetime
import os
import re

app = Flask(__name__)
PYTHONANYWHERE = False
file_prefix = ['../', '../'][PYTHONANYWHERE]
@app.route('/')
def home():
    return render_template('main.html')    

@app.route('/get_data')
def get_data():
    file_name = file_prefix + 'marketplaceScraper/data'
    files = os.listdir(file_name)

    files_list = sorted([file for file in files if len(file) == 14])
    list_names = []
    data = {}
    location = ''
    for f in files_list:
        with open(file_name + '/' + f) as csv_file:
            csv_reader = csv.reader(csv_file)
            list_names.append(f[:7])
            data[f[:7]] = []        
            for row in csv_reader:
                if len(row) >= 4 and row[0] != 'NAME':
                    if row[0] == '-':
                        location = row[2]
                    if row[0] != '-':
                        row.append(location)
                        data[f[:7]].append(row)
    return jsonify(data)

@app.route('/get_loc')
def get_loc():
    locations = []
    file_name = file_prefix + 'marketplaceScraper/locations.txt'
    with open(file_name) as f:
        for line in f:
            locations.append(re.search(r'^(.*),(.*)', line).group(1))
    print(locations)
    return jsonify(locations)

if __name__ == "__main__":
    app.run(debug= True)