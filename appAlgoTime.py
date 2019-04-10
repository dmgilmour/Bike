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

class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        return float(value)

    def _float64_to_mysql(self, value):
        return float(value)

    def _int32_to_mysql(self, value):
        return int(value)

    def _int64_to_mysql(self, value):
        return int(value)

class Algo(object):

    _mydb = None
    _mycursor = None
    converter = NumpyMySQLConverter()

    def __init__(self):

        
        self.PI = math.pi

        self._mydb = mysql.connector.connect(
                host="designdbv2.cfzhptvfng6g.us-east-1.rds.amazonaws.com",
                user="admin",
                passwd="AWS4SeniorDesign!",
                database="ssHistory"
        )

        self._mycursor = self._mydb.cursor()
        self._mydb.set_converter_class(NumpyMySQLConverter)

    def f_lookup(self, n, p=2, conf=0.05):
        return 3.3158


    def mvn_confidence(self, pop, means, covarMat, newMeans):
        meanDiffMat = [[means[0][0] - newMeans[0][0]], [means[1][0] - newMeans[1][0]]]
        try:
            matMultOne = np.matmul(np.transpose(meanDiffMat), np.linalg.inv(covarMat))
            matMultTwo = np.matmul(matMultOne, meanDiffMat)
            firstCompare = pop*matMultTwo
        except:
            print("Exception")
            return [0, 1]
        if(pop < 30):
            pop = 30
        fVal = self.f_lookup(pop, 2)
        secondCompare = ((pop-1)*2)/(pop-2)*fVal

        conf = 1/(firstCompare / (secondCompare / 100.0))

        if(firstCompare > secondCompare):
            print("Greater")
            return [1, conf]
        else:
            print("Lesser")
            return [0, conf]

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
        firstSelect = self.select_from_window(stringWindowStart, stringWindowEnd, user)
        firstMeans = [[float(firstSelect[1])], [float(firstSelect[2])]]
        meanArr = [[meanLon], [meanLat]]
        firstConfidence = self.mvn_confidence(60, firstMeans, firstSelect[0], meanArr)

        return firstConfidence
                
    def ayyyyyyo(self, bikeid):
        sql = "SELECT coordX, coordY, pullTime FROM sensorData WHERE bikeID = 0 ORDER BY pullTime desc"
        #vals = (str(bikeid),)
        self._mycursor.execute(sql)
        result = self._mycursor.fetchall()
        return result[0]

    def new_bike(self, user, bikeID):
        # nextBike = self.get_next_ID('b')
        sql = "INSERT INTO bikes VALUES(%s, %s)"
        vals = (user, bikeID)
        self._mycursor.execute(sql, vals)
        self._mydb.commit()

    def dbWrite_location(self, user, bikeID, coordX, coordY, accel, pullTime):
        sql = "INSERT INTO sensorData VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        dataID = self.get_next_ID('d')
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
        val = (dataID, user, bikeID, -1,  coordX, coordY, accel, 0, pullTime, day)
        self._mycursor.execute(sql, val)
        self._mydb.commit()

    def dbWrite_user(self, userID, password, salt):
        sql = "INSERT INTO users VALUES (%s, %s, %s)"
        val = (userID, password, salt)
        self._mycursor.execute(sql, val)
        self._mydb.commit()

    def get_user_history(self, user):
        sql = "SELECT coordX, coordY, pullTime FROM sensorData WHERE user = %s ORDER BY pullTime desc"
        val = (user,)
        self._mycursor.execute(sql, val)
        
        result = self._mycursor.fetchall()
        return result

    def get_user(self, username):
        sql = "SELECT * FROM users WHERE user = %s"
        vals = (username,)
        self._mycursor.execute(sql, vals)

        result = self._mycursor.fetchall()
        for row in result:
            return row

    def cluster_calc(self, cluster_id):
        sql = "SELECT * FROM sensorData WHERE clusterID = %s"
        vals = (cluster_id,)
        self._mycursor.execute(sql, vals)
        result = self._mycursor.fetchall()

        lons = []
        lats = []
        for row in result:
            lons.append(row[3])
            lats.append(row[4])
        lons = np.array(lons)
        lats = np.array(lats)

        #print(lons)
        #print(lats)
        if(np.mean(lons) != 0):
            meanLon = np.mean(lons)
        if(np.mean(lats) != 0):
            meanLat = np.mean(lats)
			
        covarMat = np.cov(lons.astype(float), lats.astype(float))

        #print(meanLon, "\n", meanLat, "\n", covarMat[0][0], "\n", covarMat[1][1], "\n", covarMat[0][1], "\n", cluster_id)
        sql = "UPDATE clusters SET mean_x = %s, mean_y = %s, var_x = %s, var_y = %s, covar = %s WHERE CID = %s"
        vals = (float(meanLon), float(meanLat), float(covarMat[0][0]), float(covarMat[1][1]), float(covarMat[0][1]), cluster_id)
        self._mycursor.execute(sql, vals)
        self._mydb.commit()

        return [covarMat, meanLon, meanLat]

    def average_var(self):
        sql = "SELECT var_x, var_y FROM clusters"
        self._mycursor.execute(sql)
        result = self._mycursor.fetchall()
        if (self._mycursor.rowcount == 0):
            return [.00015,.00015]

        var_x_tot = 0
        var_y_tot = 0
        for row in result:
            var_x_tot += row[0]
            var_y_tot += row[1]
        var_x_avg = var_x_tot / len(result)
        var_y_avg = var_y_tot / len(result)
        if(var_x_avg == 0 and var_y_avg ==0):
            return [.00015, .00015]
        return [var_x_avg, var_y_avg]

    def get_next_ID(self, mode):
        print(mode)
        if (mode == 'c'):
            sql = "SELECT MAX(CID) FROM clusters"
        elif (mode == 'd'):
            sql = "SELECT MAX(dataID) FROM sensorData"
            
        elif (mode == 'b'):
            sql = "SELECT MAX(bike) FROM bikes"
        self._mycursor.execute(sql)
        result = self._mycursor.fetchall()
        if(self._mycursor.rowcount == 0):
            return 0

        for row in result:
            if row[0] == None:
                return 1
            return row[0] + 1

    def dist_to(self, x, y, x2, y2):
        dist = np.sqrt(np.power((x - x2), 2) + np.power((y - y2), 2))
        return dist

    def get_size(self, clusterID):
        sql = "SELECT COUNT(dataID) FROM sensorData WHERE clusterID = %s"
        vals = (clusterID,)
        self._mycursor.execute(sql, vals)
        result = self._mycursor.fetchall()

        for row in result:
            return row[0]

    def group_point(self, new_x, new_y):
        sql = "SELECT * FROM clusters"
        self._mycursor.execute(sql)
        result = self._mycursor.fetchall()
        if(self._mycursor.rowcount == 0):
            in_cluster = 0
        else:
            minDist = -1
            for row in result:
                tempDist = self.dist_to(new_x, new_y, row[1], row[2])
                if (tempDist < minDist or minDist == -1):
                    minDist = tempDist
                    closestID = row[0]
                    closestIndex = row

            closestMeans = [[float(closestIndex[1])], [float(closestIndex[2])]]
            closestCovar = [[float(closestIndex[3]), float(closestIndex[5])],
							[float(closestIndex[5]), float(closestIndex[4])]]
            cluster_size = self.get_size(closestID)
            if((closestMeans[0][0] - new_x == 0 ) and (closestMeans[1][0] - new_y == 0)):
                in_cluster = 1
            else:
                in_cluster = self.mvn_confidence(cluster_size, closestMeans, closestCovar, [[new_x], [new_y]])[0]

        if (in_cluster):
            sql = "UPDATE sensorData SET clusterID = %s WHERE dataID IN(SELECT MAX(dataID) FROM(SELECT * FROM sensorData) AS sd)"
            vals = (closestID,)
            self._mycursor.execute(sql, vals)
            self._mydb.commit()
            self.cluster_calc(closestID)
            return [0, closestID]
        else:
            variences = self.average_var()
            var_x_avg = variences[0]
            var_y_avg = variences[1]
            sql = "INSERT INTO clusters VALUES(%s, %s, %s, %s, %s, 0)"
            nextID = self.get_next_ID('c')
            vals = (nextID, new_x, new_y, var_x_avg, var_y_avg)
            self._mycursor.execute(sql, vals)
            self._mydb.commit()
            sql = "UPDATE sensorData SET clusterID = %s WHERE dataID IN(SELECT MAX(dataID) FROM(SELECT * FROM sensorData) AS sd)"
            vals = (nextID,)
            self._mycursor.execute(sql, vals)
            self._mydb.commit()
            return [1, nextID]
        
    def point_process(self, user, bike, lon, lat, accel, time, delta):
        g_resp = 0
                
        windowStart = time - timedelta(minutes=delta)
        windowEnd = time + timedelta(minutes=delta)
                
        self.dbWrite_location(user, bike, lon, lat, accel, time)
        if (True):
            g_resp = self.group_point(lon, lat)
                
            t_resp = self.time_slice(lon, lat, windowStart, windowEnd, user)
                
            if (t_resp[0] and g_resp[0]):
                return True
                
            return False
        return True
