#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, shutil, json

Exception_Folder_Names = ['AppIcon.appiconset', 'LaunchImage.launchimage']

def consoleLog(type, message):
	if type == 'Error':
		print('\033[1;31m' + str(message) + '\033[0m')
	elif type == 'Warning':
		print('\033[1;33m' + str(message) + '\033[0m')
	elif type == 'Success':
		print('\033[1;32m' + str(message) + '\033[0m')
	else:
		print(str(message))

class BAOCImgsOrganizer(object):

	def __init__(self):
		super(BAOCImgsOrganizer, self).__init__()

	def __getFileSuffix(self, fileName):
		if fileName == None or len(fileName) == 0:
			return None
		(realName, suffix) = os.path.splitext(fileName)
		return suffix

	def __getRealFileName(self, fileName):
		if fileName == None or len(fileName) == 0:
			return None
		(realName, suffix) = os.path.splitext(fileName)
		return realName
	
	def __needSkipFolder(self, folderPath):
		folderName = os.path.basename(folderPath)
		if folderName in Exception_Folder_Names:
			return True
		else:
			return False

	def __handleImageSetFolder(self, rootDir, currentDir, targetDir, namePathsDic):
		currentPathName = os.path.basename(currentDir)
		currentPathSuffix = self.__getFileSuffix(currentPathName)
		if currentPathSuffix != ".imageset":
			return True

		paths = []
		if currentPathName in namePathsDic:
			paths = namePathsDic[currentPathName]
		paths.append(currentDir)
		namePathsDic[currentPathName] = paths

		contentJsonFilePath = os.path.join(currentDir, "Contents.json")
		if os.path.exists(contentJsonFilePath) == False or os.path.isdir(contentJsonFilePath) == True:
			consoleLog("Error", "🚫 Analysize Contents.json file error!(Can't find it) " + currentDir)
			return True

		fileHandler = open(contentJsonFilePath, 'r')
		if fileHandler == None:
			fileHandler.close()
			consoleLog("Error", "🚫 Analysize Contents.json file error!(Can't open it) " + currentDir)
			return True

		jsonContent = json.load(fileHandler)
		fileHandler.close()

		if jsonContent == None:
			consoleLog("Error", "🚫 Analysize Contents.json file error!(Can't read it) " + currentDir)
			return True

		if "images" not in jsonContent:
			consoleLog("Error", '🚫 Imageset empty! ' + currentDir)
			return True
		imgsArray = jsonContent["images"]
		if imgsArray == None or len(imgsArray) == 0:
			consoleLog("Error", '🚫 Imageset empty! ' + currentDir)
			return True
		
		imgName3x = None
		imgName2x = None
		imgName1x = None
		for i in range(len(imgsArray)):
			imgItem = imgsArray[i]
			imgFileName = None
			if "filename" in imgItem:
				imgFileName = imgItem["filename"]
			imgScale = imgItem["scale"]
			if imgFileName == None:
				consoleLog("Warning", "⚠️  Can't find filename record for " + str(imgScale) + " " + currentDir)
			elif os.path.exists(os.path.join(currentDir, imgFileName)) == False or os.path.isdir(os.path.join(currentDir, imgFileName)) == True:
				consoleLog("Warning", "⚠️  Can't find image file for " + str(imgScale) + " " + currentDir)
			else :
				if imgScale == "3x":
					imgName3x = imgFileName
				elif imgScale == "2x":
					imgName2x = imgFileName
				elif imgScale == "1x":
					imgName1x = imgFileName
		
		baseImgFileName = None
		if imgName3x != None:
			baseImgFileName = imgName3x
		elif imgName2x != None:
			baseImgFileName = imgName2x
		elif imgName1x != None:
			baseImgFileName = imgName1x

		img3xItem = {"idiom": "universal", "scale": "3x"}
		img2xItem = {"idiom": "universal", "scale": "2x"}
		img1xItem = {"idiom": "universal", "scale": "1x"}

		imageSetName = self.__getRealFileName(currentPathName)
		targetImageSetDir = os.path.join(targetDir, currentDir[len(rootDir) + 1 : len(currentDir)])
		if os.path.exists(targetImageSetDir) == False or os.path.isdir(targetImageSetDir) == False:
			os.makedirs(targetImageSetDir)

		sourceName3x = imgName3x
		if sourceName3x == None:
			sourceName3x = baseImgFileName
		if sourceName3x != None:
			oldImgFilePath = os.path.join(currentDir, sourceName3x)
			newImgName = imageSetName + "@3x.png"
			newImgFilePath = os.path.join(targetImageSetDir, newImgName)
			shutil.copyfile(oldImgFilePath, newImgFilePath)
			img3xItem["filename"] = newImgName

		sourceName2x = imgName2x
		if sourceName2x == None:
			sourceName2x = baseImgFileName
		if sourceName2x != None:
			oldImgFilePath = os.path.join(currentDir, sourceName2x)
			newImgName = imageSetName + "@2x.png"
			newImgFilePath = os.path.join(targetImageSetDir, newImgName)
			shutil.copyfile(oldImgFilePath, newImgFilePath)
			img2xItem["filename"] = newImgName

		sourceName1x = imgName1x
		if sourceName1x == None:
			sourceName1x = baseImgFileName
		if sourceName1x != None:
			oldImgFilePath = os.path.join(currentDir, sourceName1x)
			newImgName = imageSetName + "@1x.png"
			newImgFilePath = os.path.join(targetImageSetDir, newImgName)
			shutil.copyfile(oldImgFilePath, newImgFilePath)
			img1xItem["filename"] = newImgName
		
		infoDic = {}
		infoDic["version"] = 1
		infoDic["author"] = "xcode"
		newContentJson = {}
		newContentJson["info"] = infoDic
		imgsArray = []
		imgsArray.append(img3xItem)
		imgsArray.append(img2xItem)
		imgsArray.append(img1xItem)
		newContentJson["images"] = imgsArray
		
		newFileHandler = open(os.path.join(targetImageSetDir, "Contents.json"), 'w', encoding='utf-8')
		if newFileHandler == None:
			newFileHandler.close()
			consoleLog("Error", "🚫 Write Contents.json file error!(Can't open it) " + currentDir)
			return False
		json.dump(newContentJson, newFileHandler)
		newFileHandler.close()
		return False

	def __organizeAction(self, rootDir, currentDir, targetDir, namePathsDic):
		targetImageSetDir = os.path.join(targetDir, currentDir[len(rootDir) + 1 : len(currentDir)])
		needFullCopy = False
		if self.__needSkipFolder(currentDir) == False:
			needFullCopy = self.__handleImageSetFolder(rootDir, currentDir, targetDir, namePathsDic)

			for fileName in os.listdir(currentDir):
				filePath = os.path.join(currentDir, fileName)
				fileSuffix = self.__getFileSuffix(fileName)
				if (os.path.isdir(filePath)):
					self.__organizeAction(rootDir, filePath, targetDir, namePathsDic)
		else:
			consoleLog(None, "Skip " + currentDir)
			needFullCopy = True

		if needFullCopy == True and (os.path.exists(targetImageSetDir) == False or os.path.isdir(targetImageSetDir) == False):
			shutil.copytree(currentDir, targetImageSetDir)

	def startOrganize(self, sourceDir, targetDir):
		consoleLog(None, "👉  Organize action, here we go!")

		namePathsDic = {}
		self.__organizeAction(sourceDir, sourceDir, targetDir, namePathsDic)
		for key, paths in namePathsDic.items():
			if len(paths) > 1:
				consoleLog("Error", "🚫 Imageset repeated! " + key + ":")
				for pathItem in paths:
					consoleLog("Error", "    " + pathItem)
		consoleLog(None, "✌️  Finished!")
	
	def __extractAction(self, currentDir, targetDir):
		if self.__needSkipFolder(currentDir) == True:
			return
		for fileName in os.listdir(currentDir):
			filePath = os.path.join(currentDir, fileName)
			if (os.path.isdir(filePath)):
				self.__extractAction(filePath, targetDir)
			else:
				fileSuffix = self.__getFileSuffix(fileName)
				if fileSuffix == '.png' or fileSuffix == '.jpg':
					shutil.copyfile(filePath, os.path.join(targetDir, fileName))

	def startExtract(self, sourceDir, targetDir):
		consoleLog(None, "👉  Extract action, here we go!")
		os.makedirs(targetDir)
		self.__extractAction(sourceDir, targetDir)
		consoleLog(None, "✌️  Finished!")

if __name__ == '__main__':
	if len(sys.argv) < 2:
		quit()
	action = sys.argv[1]
	if action != '-organize' and action != '-extract' and action != '-o' and action != '-e':
		quit()
	if len(sys.argv) < 4:
		quit()
	sourceDir = sys.argv[2]
	targetDir = sys.argv[3]

	if os.path.exists(sourceDir) == False or os.path.isdir(sourceDir) == False:
		consoleLog("Warning", '⚠️  Source directory path invalid!')
		quit()

	if os.path.exists(targetDir) == True and os.path.isdir(targetDir) == True:
		nextStep = input("️Target directory already existed, remove and continue?(Y/N)")
		if nextStep == 'Y' or nextStep == 'y' or nextStep == 'YES' or nextStep == 'yes':
			shutil.rmtree(targetDir)
		else:
			quit()

	if action == '-organize' or action == '-o':
		organizer = BAOCImgsOrganizer()
		organizer.startOrganize(sourceDir, targetDir)
	elif action == '-extract' or action == '-e':
		organizer = BAOCImgsOrganizer()
		organizer.startExtract(sourceDir, targetDir)