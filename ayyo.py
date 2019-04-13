import csv
from appAlgoTime import Algo
algo = Algo()
with open('confidence_compare.txt') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    for row in csv_reader:
        algo.point_process(row['user'], row['bikeID'], row['lon'], row['lat'], 0, row['time'], 10)
