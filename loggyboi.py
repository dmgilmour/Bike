
import csv
import json
import sys
import time
import datetime
import bcrypt
from getpass import getpass
from appAlgoTime import Algo
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash, jsonify

algo = Algo()
new_list = []

with open("../Locations2.json") as jfile:
    with open('../5000_points.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        data = json.load(jfile)
        i = 0
        cluster_list = []
        for clusterboi in csv_reader:
            cluster_list.append({'lat':clusterboi['lat'], 'lon':clusterboi['lon'], 'cluster':clusterboi['cluster']})
        for loc in data:

            new_list.append({'lat':float(cluster_list[i]['lat']), 'lon':float(cluster_list[i]['lon']), 'time':loc['time'], 'cluster':cluster_list[i]['cluster']})
            i += 1

        for loc in new_list:
            print(loc)

            # new_list.append({'longitudeE7':loc['longitudeE7'], 'latitudeE7':loc['latitudeE7'], 'lat':loc['longitudeE7']/10000000, 'lon':loc['latitudeE7']/10000000, 'time':loc['timestampMs']})
            
            #new_list.append({'lat':loc['latitudeE7']/10000000.0, 'lon':(loc['longitudeE7']/10000000.0-270)*-1, 'time':loc['timestampMs']})
            #if i == 10000 or i == 14999:
            #    print(datetime.datetime.fromtimestamp(int(loc['timestampMs'])//1000))

            # algo.dbWrite_location("ayyo", 22, loc['latitudeE7']/10000000.0, (loc['longitudeE7']/10000000.0-270)*-1 - 0.41, 0, datetime.datetime.fromtimestamp(int(loc['timestampMs'])//1000), 0)


    with open("../Locations3.json", 'w') as outfile:
        json.dump(new_list, outfile)
