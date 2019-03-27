import mysql.connector
import numpy as np
import scipy
from scipy.stats import f
from scipy.stats import multivariate_normal
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

mydb = mysql.connector.connect(
host="satellitesidecaruserhistory.c701a5j4aycw.us-east-1.rds.amazonaws.com",
user="admin",
passwd="design2019",
database="ssHistory"
)

mycursor = mydb.cursor()
mydb.set_converter_class(NumpyMySQLConverter)


def f_lookup(n, p=2, conf=0.05):
    return scipy.stats.f.ppf(q=(1 - conf), dfn=p, dfd=n - p)

def mvn_confidence(pop, means, covarMat, newMeans):
    if(pop <= 2):
        pop = 3
    meanDiffMat = [[means[0][0] - newMeans[0][0]], [means[1][0] - newMeans[1][0]]]
    # print("Heck: ", meanDiffMat)
    matMultOne = np.matmul(np.transpose(meanDiffMat), np.linalg.inv(covarMat))
    matMultTwo = np.matmul(matMultOne, meanDiffMat)
    firstCompare = pop * matMultTwo

    fVal = f_lookup(pop, 2)
    # print("FVal: ", fVal)
    secondCompare = ((pop - 1) * 2) / (pop - 2) * fVal

    # print(firstCompare)
    # print(secondCompare)
    conf = 1 / (firstCompare / (secondCompare / 100.0))

    if (firstCompare > secondCompare):
        return [0, conf]  # print("Greater")
    else:
        return [1, conf]  # print("Lesser")

def cluster_calc(cluster_id):
    sql = "SELECT * FROM sensorData WHERE clusterID = %s"
    vals = (cluster_id,)
    mycursor.execute(sql, vals)
    result = mycursor.fetchall()

    lons = []
    lats = []
    for row in result:
        lons.append(row[3])
        lats.append(row[4])
    lons = np.array(lons)
    lats = np.array(lats)

    print(lons)
    print(lats)

    meanLon = np.mean(lons)
    meanLat = np.mean(lats)
    covarMat = np.cov(lons.astype(float), lats.astype(float))

    print(meanLon, "\n", meanLat, "\n", covarMat[0][0], "\n", covarMat[1][1], "\n", covarMat[0][1], "\n", cluster_id)
    sql = "UPDATE clusters SET mean_x = %s, mean_y = %s, var_x = %s, var_y = %s, covar = %s WHERE CID = %s"
    vals = (meanLon, meanLat, covarMat[0][0], covarMat[1][1], covarMat[0][1], cluster_id)
    mycursor.execute(sql, vals)
    mydb.commit()

    return [covarMat, meanLon, meanLat]

def average_var():
    sql = "SELECT var_x, var_y FROM clusters"
    mycursor.execute(sql)
    result = mycursor.fetchall()

    var_x_tot = 0
    var_y_tot = 0
    for row in result:
        var_x_tot += row[0]
        var_y_tot += row[1]
    var_x_avg = var_x_tot/len(result)
    var_y_avg = var_y_tot/len(result)

    return [var_x_avg, var_y_avg]

def get_next_ID(mode):
    if(mode == 'c'):
        sql = "SELECT MAX(CID) FROM clusters"
    elif(mode == 'd'):
        sql = "SELECT MAX(dataID) FROM sensorData"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    for row in result:
        return row[0]+1

def dist_to(x, y, x2, y2):
    dist = np.sqrt(np.power((x-x2),2)+np.power((y-y2), 2))
    return dist

def get_size(clusterID):
    sql = "SELECT COUNT(dataID) FROM sensorData WHERE clusterID = %s"
    vals = (clusterID,)
    mycursor.execute(sql, vals)
    result = mycursor.fetchall()

    for row in result:
        return row[0]

def new_point(new_x, new_y):
    sql = "SELECT * FROM clusters"
    mycursor.execute(sql)
    result = mycursor.fetchall()

    minDist = -1
    for row in result:
        tempDist = dist_to(new_x, new_y, row[1], row[2])
        print(tempDist)
        if(tempDist < minDist or minDist == -1):
            minDist = tempDist
            closestID = row[0]
            closestIndex = row

    closestMeans = [[float(closestIndex[1])], [float(closestIndex[2])]]
    closestCovar = [[float(closestIndex[3]), float(closestIndex[5])], [float(closestIndex[5]), float(closestIndex[4])]]
    cluster_size = get_size(closestID)
    in_cluster = mvn_confidence(cluster_size, closestMeans, closestCovar, [[new_x],[new_y]])[0]

    if(in_cluster):
        sql = "UPDATE sensorData SET clusterID = %s WHERE dataID IN(SELECT MAX(dataID) FROM(SELECT * FROM sensorData) AS sd)"
        vals = (closestID,)
        mycursor.execute(sql, vals)
        mydb.commit()
        cluster_calc(closestID)
    else:
        variences = average_var()
        var_x_avg = variences[0]
        var_y_avg = variences[1]
        sql = "INSERT INTO clusters VALUES(%s, %s, %s, %s, %s, 0)"
        nextID = get_next_ID('c')
        vals = (nextID, new_x, new_y, var_x_avg, var_y_avg)
        mycursor.execute(sql, vals)
        mydb.commit()
        sql = "UPDATE sensorData SET clusterID = %s WHERE dataID IN(SELECT MAX(dataID) FROM(SELECT * FROM sensorData) AS sd)"
        vals = (nextID,)
        mycursor.execute(sql, vals)
        mydb.commit()
