import os
import pygrib
import numpy as np

class WeatherService(object):

    def __init__(self):

        self.workingDir = os.getcwd()

        self.inputFolder = os.path.join(self.workingDir, "INPUT")
        self.outputFolder = os.path.join(self.workingDir, "OUTPUT")

        self.pressLevels = None
        self.latLevels = None
        self.lonLevels = None

    def start(self):

        fileList = os.listdir(self.inputFolder)

        for fileName in fileList:

            self.outputFileDateTime = self.generateOutputFileDateTime(fileName)

            filePath = os.path.join(self.inputFolder, fileName)

            grbs = pygrib.open(filePath)

            self.parseGrib(grbs)

    def generateOutputFileDateTime(self, fileName):

        fileNameDataList = fileName.split(".")

        outputFileName = ""

        analyse = fileNameDataList[2]
        foreCast = fileNameDataList[3]

        if foreCast == "f000":
            outputFileName = analyse

        else:

            analyseHour = analyse[-2:]
            foreCastHour = foreCast[-2:]

            hour = int(analyseHour) + int(foreCastHour)

            hour = "{:02}".format(hour)

            analyse = analyse[0:8] + hour
            outputFileName = analyse

        return outputFileName

    def parseGrib(self, grb):

        absVorticitySet = grb.select(name="Absolute vorticity")
        tempDataSet = grb.select(name="Temperature")
        totalCloudCoverSet = grb.select(name="Total Cloud Cover")
        uWindDataSet = grb.select(name="U component of wind")
        vWindDataSet = grb.select(name="V component of wind")

        self.parseTemperature(tempDataSet)
        self.parseVorticity(absVorticitySet)
        self.parseCloud(totalCloudCoverSet)
        self.parseWind(uWindDataSet, vWindDataSet)


        # left = tempDataSet[0]['longitudes'][0]
        # right = tempDataSet[0]['longitudes'][-1]
        #
        # bottom = tempDataSet[0]['latitudes'][0]
        # top = tempDataSet[0]['latitudes'][-1]

        # self.pressLevels = np.arange(100, 1050, 50)
        # self.latLevels = np.arange(bottom, top + 0.25, 0.25)
        # self.lonLevels = np.arange(left, right + 0.25, 0.25)

        #tempDataSet = tempDataSet[0].values - 273.15

        #print(absVorticitySet[0].values.shape)
        #print(tempDataSet[0].values.shape)
        #print(totalCloudCoverSet[0].values.shape)
        #print(uCompDataSet[0].values.shape)
        #print(vCompDataSet[0].values.shape)

    def parseTemperature(self, dataSet):

        tempDataArray = None

        level = 0

        for tempLevel in dataSet:

            if level == 0:
                tempDataArray = np.array(tempLevel.values)
                level += 1

            else:
                tempDataArray = np.concatenate((tempDataArray, tempLevel.values), axis=0)
                level += 1

        tempDataArray = tempDataArray.round(decimals=1)

        outputFileName = self.outputFileDateTime + "_temp.csv"

        outputFilePath = os.path.join(self.outputFolder, outputFileName)

        np.savetxt(outputFilePath, tempDataArray, delimiter=",")

    def parseVorticity(self, dataSet):

        vorticityDataArray = None

        level = 0

        for vorticityLevel in dataSet:

            if level == 0:
                vorticityDataArray = np.array(vorticityLevel.values)
                level += 1

            else:
                vorticityDataArray = np.concatenate((vorticityDataArray, vorticityLevel.values), axis=0)
                level += 1

        vorticityDataArray = vorticityDataArray.round(decimals=1)

        outputFileName = self.outputFileDateTime + "_vorticity.csv"

        outputFilePath = os.path.join(self.outputFolder, outputFileName)

        np.savetxt(outputFilePath, vorticityDataArray, delimiter=",")

    def parseCloud(self, dataSet):

        cloudDataArray = None

        level = 0

        for cloudLevel in dataSet:

            if level == 0:
                cloudDataArray = np.array(cloudLevel.values)
                level += 1

            else:
                cloudDataArray = np.concatenate((cloudDataArray, cloudLevel.values), axis=0)
                level += 1

        cloudDataArray = cloudDataArray.round(decimals=1)

        outputFileName = self.outputFileDateTime + "_cloud.csv"

        outputFilePath = os.path.join(self.outputFolder, outputFileName)

        np.savetxt(outputFilePath, cloudDataArray, delimiter=",")

    def parseWind(self, uDataSet, vDataSet):

        windDataArray = None

        level = 0

        for uLevel, vLevel in zip(uDataSet, vDataSet):

            windLevel = np.sqrt(uLevel.values**2 + vLevel.values**2)

            if level == 0:
                windDataArray = np.array(windLevel)
                level += 1

            else:
                windDataArray = np.concatenate((windDataArray, windLevel), axis=0)
                level += 1

        windDataArray = windDataArray.round(decimals=1)

        outputFileName = self.outputFileDateTime + "_wind.csv"

        outputFilePath = os.path.join(self.outputFolder, outputFileName)

        np.savetxt(outputFilePath, windDataArray, delimiter=",")

weatherService = WeatherService()
weatherService.start()