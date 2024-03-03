from flask import Flask, render_template, jsonify, request, session
import csv
import statistics
import os
import re

app = Flask(__name__)
app.secret_key = '73902611249295568032813045560628'

PYTHONANYWHERE = False
file_prefix = ['../', '../'][PYTHONANYWHERE]
@app.route('/')
def home():
    if session['KEYS'] != 0 and not session.get('KEYS'):
        session['KEYS'] = 10
    return render_template('main.html')    

@app.route('/get_data', methods=['POST', 'GET'])
def get_data():
    if session['KEYS'] <= 0:
        return jsonify({'keys': session['KEYS']})
    session['KEYS'] = session['KEYS'] - 1
    if request.form.get('vehicle', 'n/a') != '':
        vehicle = request.form.get('vehicle', 'n/a')
    else:
        vehicle = 'n/a'
    if request.form.get('location', 'n/a') != '':
        location = request.form.get('location', 'n/a')
    else:
        location = 'n/a'  
    names = {'minPrice': -1, 'minMiles': -1, 'minYear': -1, 'maxPrice': 999999, 'maxMiles': 999999, 'maxYear': 999999}
    for i in range(len(list(names.keys()))):
        if request.form.get(list(names.keys())[i], str(list(names.values())[i])) != '':
            names[(list(names.keys()))[i]] = int(request.form.get(list(names.keys())[i], list(names.values())[i]))
        else:
            names[(list(names.keys()))[i]] = list(names.values())[i]
    
    file_name = file_prefix + 'marketplaceScraper/data'
    files = os.listdir(file_name)
    files_list = sorted([file for file in files if len(file) == 14])
    list_names = []
    data = {}
    stats = {'avg_price_time': {}, 'avg_price_loc': {}, 'num_listings_time': {}, 'num_listings_loc': {}, 'location': location, 'vehicles': [], 'keys': session['KEYS']}
    add_location = ''
    for f in files_list:
        with open(file_name + '/' + f) as csv_file:
            csv_reader = csv.reader(csv_file)
            list_names.append(f[:7])
            data[f[:7]] = []
            for row in csv_reader:
                if len(row) >= 4 and row[0] != 'NAME':
                    if row[0] == '-':
                        add_location = row[2]
                    if row[0] != '-' and row[2].isdigit() and row[3].isdigit() and row[1].isdigit():
                        row.append(add_location)
                        if ((vehicle == 'n/a' or vehicle.lower() in row[0].lower()) 
                            and (location == 'n/a' or location != row[4]) 
                            and (int(row[2]) >= names['minPrice'] and int(row[2]) <= names['maxPrice']) 
                            and (int(row[3]) >= names['minMiles'] and int(row[3]) <= names['maxMiles'])
                            and (int(row[1]) >= names['minYear'] and int(row[1]) <= names['maxYear'])):
                            data[f[:7]].append(row)
                        stats['vehicles'].append(row[0])

        if [int(d[2]) for d in data[f[:7]] if d[2].isdigit()]:
            stats['avg_price_time'][f[:7]] = statistics.mean([int(d[2]) for d in data[f[:7]] if d[2].isdigit()])
        else:
            stats['avg_price_time'][f[:7]] = 0
        stats['num_listings_time'][f[:7]] = len(data[f[:7]])
        locations = []
        location_file_name = file_prefix + 'marketplaceScraper/locations.txt'
        with open(location_file_name) as file:
            for line in file:
                locations.append(re.search(r'^(.*),(.*)', line).group(1))
        for l in locations:
            if [int(d[2]) for d in data[f[:7]] if d[4] == l and d[2].isdigit()]:
                stats['avg_price_loc'][l] = statistics.mean([int(d[2]) for d in data[f[:7]] if d[4] == l and d[2].isdigit()])
            else:
                stats['avg_price_loc'][l] = 0
            stats['num_listings_loc'][l] = len([d for d in data[f[:7]] if d[4] == l])
    return jsonify(stats)

@app.route('/get_loc')
def get_loc():
    locations = []
    file_name = file_prefix + 'marketplaceScraper/locations.txt'
    with open(file_name) as f:
        for line in f:
            locations.append(re.search(r'^(.*),(.*)', line).group(1))
    return jsonify(locations)

if __name__ == "__main__":
    app.run(debug= True)