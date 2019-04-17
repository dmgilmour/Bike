
import json
import sys
import time
import datetime
import bcrypt
from getpass import getpass
from appAlgoTime import Algo
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash, jsonify

new_list = []

with open("../Locations2.json") as jfile:
    data = json.load(jfile)['locations']
    for loc in data:
        
        new_list.append({'lon':(loc['longitudeE7']/10000000.0-270)*-1, 'lat':loc['latitudeE7']/10000000.0, 'time':loc['timestampMs']})
        #print(new_list[len(new_list) - 1])


with open("../Locations3.json", 'w') as outfile:
    json.dump(new_list, outfile)
