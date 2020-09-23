from datetime import datetime

import pandas as pd
import numpy as np

import json
import time
import os

class WeatherAnomalyDetection(object):

    def __init__(self):

        self.detectsDict = {}

        workingDir = os.getcwd()

        self.weatherDataFolder = os.path.join(workingDir, "OUTPUT")

        self.pressLevels = np.arange(100, 1000 + 50, 50)  # pressure levels from 100 to 1000mb
        self.latLevels = np.arange(34, 44 + 0.25, 0.25)  # lats from 34 to 44
        self.lonLevels = np.arange(23, 47 + 0.25, 0.25)  # lons from 23 to 47

        print("Number of Weather Data Levels:", len(self.pressLevels))
        print(len(self.latLevels), "x", len(self.lonLevels), "grids")

        self.thresholdDict = {'cloud': 90, 'temp': 310, 'humidity': 95, 'vorticity': 0.0005, 'wind': 30}

    def readWeatherFile(self, filePath):

        try:
            dataFrame = pd.read_csv(filePath, header=None)
            dataFrame = dataFrame.values.reshape(len(self.pressLevels), len(self.latLevels), len(self.lonLevels))

            return dataFrame

        except Exception as e:

            print(e, "Weather, Reading " + filePath + " failed!")

            return np.array([])

    def startDetectForSingleWeatherType(self, weatherType):

        f = np.frompyfunc(self.getCoordsOfIndex, 3, 1)

        for file in os.listdir(self.weatherDataFolder):

            if file.endswith("_" + weatherType + ".csv"):

                timestamp = self.getTimestamp(file)

                weahterFilePath = os.path.join(self.weatherDataFolder, file)

                df = self.readWeatherFile(weahterFilePath)

                threshold = self.thresholdDict[weatherType]

                result = np.where(df > threshold)

                #print(file, len(result[0]))

                coordList = f(result[0], result[1], result[2])

                if len(coordList > 0):

                    if str(timestamp) not in self.detectsDict.keys():
                        self.detectsDict[str(timestamp)] = {}

                    self.detectsDict[str(timestamp)][weatherType] = list(coordList)

    def getCoordsOfIndex(self, pressIndex, latIndex, lonIndex):

        altitude = (1.0 - (self.pressLevels[pressIndex] / 1013.25) ** (0.190284)) * 145366.45

        return {'Alt': int(altitude), 'Lon': self.latLevels[latIndex], 'Lat': self.lonLevels[lonIndex]}

    def getTimestamp(self, fileName):

        datePart = fileName.split('_')[0]

        year = int(datePart[0:4])
        month = int(datePart[4:6])
        day = int(datePart[6:8])
        hour = int(datePart[8:10])

        # create two dates with year, month, day, hour, minute, and second
        date = datetime(year, month, day, hour, 0, 0)

        timestamp = int(time.mktime(date.timetuple()))

        return timestamp

    def exportToJson(self):

        with open('WeatherDetects.json', 'w') as fp:
            json.dump(self.detectsDict, fp)

wad = WeatherAnomalyDetection()
wad.startDetectForSingleWeatherType('cloud')
wad.startDetectForSingleWeatherType('vorticity')
wad.startDetectForSingleWeatherType('wind')
wad.exportToJson()
