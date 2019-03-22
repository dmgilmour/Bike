import mysql.connector
import math
import numpy as np
from numpy import linalg
from datetime import datetime
from datetime import timedelta
# import matplotlib.pyplot as plt
# import scipy.stats
# from scipy.stats import f
# from scipy.stats import multivariate_normal
# from mpl_toolkits.mplot3d import Axes3D


class Algo(object):

    _mydb = None
    _mycursor = None


    def __init__(self):
        self.PI = math.pi

        self._mydb = mysql.connector.connect(
                host="satellitesidecaruserhistory.c701a5j4aycw.us-east-1.rds.amazonaws.com",
                user="admin",
                passwd="design2019",
                database="ssHistory"
        )

        self._mycursor = self._mydb.cursor()

    def f_lookup(self, n, p=2, conf=0.05):
        return scipy.stats.f.ppf(q=(1-conf), dfn=p, dfd=n-p)


    def mvn_confidence(self, pop, means, covarMat, newMeans):
        return [0, 0]



        """
        meanDiffMat = [[means[0][0] - newMeans[0][0]], [means[1][0] - newMeans[1][0]]]
        #print("Heck: ", meanDiffMat)
        matMultOne = np.matmul(np.transpose(meanDiffMat), np.linalg.inv(covarMat))
        matMultTwo = np.matmul(matMultOne, meanDiffMat)
        firstCompare = pop*matMultTwo

        fVal = self.f_lookup(pop, 2)
        #print("FVal: ", fVal)
        secondCompare = ((pop-1)*2)/(pop-2)*fVal

        #print(firstCompare)
        #print(secondCompare)

        conf = 1/(firstCompare / (secondCompare / 100.0))

        if(firstCompare > secondCompare):
                return [0, conf] #print("Greater")
        else:
                return [1, conf] #print("Lesser")
        """

    def select_from_window(self, stringWindowStart, stringWindowEnd, user):
        sql = "SELECT * FROM sensorData WHERE dataID IN (SELECT dataID FROM sensorData WHERE TIME(pullTime) > %s AND TIME(pullTime) < %s) AND user = %s"
        vals = (stringWindowStart, stringWindowEnd, user)
        self._mycursor.execute(sql, vals)
        result = self._mycursor.fetchall()

        lons = []
        lats = []
        for row in result:
                lons.append(row[3])
                lats.append(row[4])
        lons = np.array(lons)
        lats = np.array(lats)

        meanLon = np.mean(lons)
        meanLat = np.mean(lats)
        covarMat = np.cov(lons.astype(float), lats.astype(float))

        return [covarMat, meanLon, meanLat]


    def time_slice(self, meanLon, meanLat, stringWindowStart, stringWindowEnd, user):
        return 0


        """
        firstSelect = self.select_from_window(stringWindowStart, stringWindowEnd, user)
        firstMeans = [[float(firstSelect[1])], [float(firstSelect[2])]]
        meanArr = [[meanLon], [meanLat]]
        firstConfidence = self.mvn_confidence(60, firstMeans, firstSelect[0], meanArr)

        return firstConfidence
        """
		
    def dbWrite_location(self, dataID, user, coordX, coordY, accel, orient):
        sql = "INSERT INTO sensorData VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        pullTime = datetime.now() + timedelta(minutes=(1*dataID))
        dayInt = pullTime.weekday()
        if(dayInt == 0):
            day = 'Monday'
        elif(dayInt == 1):
            day = 'Tuesday'
        elif (dayInt == 2):
            day = 'Wednesday'
        elif (dayInt == 3):
            day = 'Thursday'
        elif (dayInt == 4):
            day = 'Friday'
        elif (dayInt == 5):
            day = 'Saturday'
        elif (dayInt == 6):
            day = 'Sunday'
        val = (dataID, user, -1,  coordX, coordY, accel, orient, pullTime, day)
        self._mycursor.execute(sql, val)
        self._mydb.commit()

    def dbWrite_user(self, userID, password, salt):
        sql = "INSERT INTO users VALUES (%s, %s, %s)"
        val = (userID, password, salt)
        self._mycursor.execute(sql, val)
        self._mydb.commit()

    def get_user(self, username):
        sql = "SELECT * FROM users WHERE user = %s"
        vals = (username,)
        self._mycursor.execute(sql, vals)

        result = self._mycursor.fetchall()
        for row in result:
            return row
