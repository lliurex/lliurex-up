#!/usr/bin/python3
# -*- coding: utf-8 -*

import os
import shutil
import subprocess
import socket
import threading
import datetime
import math
import ssl
import pwd
import grp
import configparser
import psutil

from pathlib import Path

#from math import pi

import lliurex.lliurexup as LliurexUpCore
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import gettext
gettext.textdomain("lliurex-up")
_=gettext.gettext

class LliurexUpConnect():

	def __init__(self):

		self.llxUpCore = LliurexUpCore.LliurexUpCore()

		self.preactionsToken = self.llxUpCore.processPath / "preactions_token"
		self.upgradeToken = self.llxUpCore.processPath / "upgrade_token"
		self.installflavourToken = self.llxUpCore.processPath / "installflavour_token"
		self.postactionsToken = self.llxUpCore.processPath / "postactions_token"
		self.errorPostactionToken = self.llxUpCore.errorpostaction_token
		self.errorUpgradeToken = self.llxUpCore.errorupgrade_token
		self.errorFinalMetapackageToken = self.llxUpCore.errorfinalmetapackage_token
		self.finalUpgradeToken = self.llxUpCore.finalupgrade_token
		self.packagesData = []
		self.desktopsPath = Path("/usr/share/applications")
		self.standardIconPath = Path("/usr/share/lliurex-up/rsrc")
		self.systemIconPath = Path("/usr/share/icons/hicolor/48x48/apps")
		self.systemScalableIconPath = Path("/usr/share/icons/hicolor/scalable")
		self.disableSystrayPath = Path("/etc/lliurex-up-indicator")
		self.disableSystrayToken = self.disableSystrayPath / "disableIndicator.token"
		self.isSystrayEnabled = True
		self.numberPackagesDownloaded = []
		self.numberPackagesUnpacked = []
		self.numberPackagesInstalled = []
		self.initialNumberPackages = []
		self.packagesInstalled = []
		self.progressDownload = 0
		self.progressDownloadPercentaje = 0.00
		self.progressInstallation = 0
		self.progressInstallationPercentage = 0.00
		self.progressUnpacked = 0
		self.progressUnpackedPercentage = 0.00
		self.aptCachePath = Path("/var/cache/apt/archives")
		self.currentConfig = {"systraryEnabled":self.isSystrayEnabled}
		self.runPkexec = True
		self.flatpakActionsToken = self.llxUpCore.processPath / 'flatpakActions_token'
		self._isRunPkexec()
		self._clearCache()

	#def __init__

	def _isRunPkexec(self):

		if 'PKEXEC_UID' not in os.environ:
			self.runPkexec=False

	#def _isRunPkexec

	def checkLocks(self):

		self.llxUpCore.checkLocks()

	#def checkLocks

	def isLliurexUpLocked(self):

		code = self.llxUpCore.isLliurexUpLocked()
		msgLog = f"------------------------------------------\nLLIUREX-UP-GUI STARTING AT: {datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S")}\n------------------------------------------"

		if code == 1:
			msgLog = "Lliurex-Up is running"
		elif code == 2:
			msgLog = "Lliurex-Up is locked"
			
		self.log(msgLog)

		return code		

	#def isLliurexUpLocked	

	def isAptLocked(self):
	
		code = self.llxUpCore.isAptLocked()

		if code == 0:
			return code

		if code == 1:
			msgLog = "Apt is running"
		elif code == 2:
			msgLog = "Apt is locked"

		self.log(msgLog)

		return 	code

	#def isAptLocked 	

	def isDpkgLocked(self):

		code = self.llxUpCore.isDpkgLocked()

		if code == 0:
			return code

		if code == 1:
			msgLog = "Dpkg is running"
		elif code == 2:
			msgLog = "Dpkg is locked"
		elif code == 3:
			msgLog = "Apt is running"	

		self.log(msgLog)
	
		return 	code	

	#def isDpkgLocked	

	def unlockingProcess(self):

		cmd = self.llxUpCore.unlockerCommand()
		
		try:
			process = subprocess.run(
				cmd,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=False
			)

			result = process.returncode

			if result != 0:
				errorDetails = process.stderr.strip()
				msgLog = f"The unlocking process has failed. Code: {result} - Details: {errorDetails}"
			else:
				msgLog = "The unlocking process finished successfully"

		except Exception as e:
			result = -1
			msgLog = f"Unexpect error running unlocking process. Error: {e}"
			
		self.log(msgLog)

		return result

	#def unlockingProcess	

	def startLliurexUp(self):

		self.llxUpCore.startLliurexUp()

	#def startLliurexUp	

	def freeSpaceCheck(self):

		try:
			usage = psutil.disk_usage("/")
			freeSpace=round(usage.free / (1024**3),2)
		except Exception as e:
			self.log(f"Error checking disk space on /: {e}")
			return {"enoughSpace": False,"freeSpace": 0,0}

		if freeSpace < 2: 
			self.log(f"Not enough space on disk to upgrade (2 GB needed): {freeSpace} GB available")
			return {"enoughSpace": False,"freeSpace": freeSpace}

		return {"enoughSpace": True,"freeSpace": freeSpace}
	
	#def freeSpaceCheck		

	def checkInitialN4dStatus(self):

		self.statusN4d = self.llxUpCore.n4dStatus

		if not self.statusN4d:
			self.log("N4d is not working")

		return self.statusN4d	

	#def checkInitialN4dStatus	

	def checkInitialFlavour(self):

		self.targetMetapackage = self.llxUpCore.checkInitialFlavour()
		self.log(f"Initial check metapackage. Metapackage to install: {self.targetMetapackage}")
		
		self.previousFlavours = self.llxUpCore.previousFlavours
		self.log(f"Get initial metapackage: {self.previousFlavours}")

		return self.targetMetapackage

	#def checkFlavoour

	def canConnectToLliurexNet(self):

		canConnect = self.llxUpCore.canConnectToLliurexNet()
		self.log(f"Checking connection to lliurex.gva.es: {canConnect}")

		if canConnect.get('status'):
			self.log("Can connect to lliurex.gva.es: True")
			return True

		self.log("Can connect to lliurex.gva.es: False")
		return False		

	#def canConnectToLliurexNet

	def initActionsScript(self):

		token = "dpkg --configure -a"
		arg="initActions"

		command = self.llxUpCore.initActionsScript(arg)

		customEnv = os.environ.copy()
		customEnv["DEBIAN_FRONTEND"] = "kde"
		customEnv["DEBIAN_PRIORITY"] = "high"

		try:
			process = subprocess.run(
				command,
				env=customEnv,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				errors="replace",
				check=False
			)

			perror = process.stderr.strip()

			if token in perror:
				self.log( f"Exec Init-Actions. Error: {perror}")
				return {"status": False, "data": perror}

		 	if process.returncode != 0:
		 		self.log(f"Exec Init-Actions. Error: (Code: {process.returncode} - Details: {perror})")
		 		return {"status": False ,"data": perror}

	 		self.log("Exec Init-Actions")
	 		return {"status": True, "data":""}

		except Exception as e:
			errorMsg = str(e)
		 	self.log(f"Exec Init-Actions.Error: {errorMsg}")
		 	return {"status": False, "data":errorMsg}	

	#def initActionsScript	

	def addSourcesListLliurex(self):

		self.llxUpCore.addSourcesListLliurex()

	#def addSourcesListLliurex	

	def isLliurexUpIsUpdated(self):

		try:
			isLliurexupUpdated=self.llxUpCore.isLliurexUpIsUpdated()
			self.log(f"Checking lliurex-up. Is lliurex-up updated: {isLliurexupUpdated}")
			return isLliurexupUpdated
		except Exception as e:
			self.log(f"Checking lliurex-up. Error: {e}")
			return True

	#def isLliurexUpIsUpdated

	def isLliurexUpIsUpdated(self):

		try:
			isLliurexupInstalled = self.llxUpCore.installLliurexUp()
			returncode = isLliurexupInstalled.get('returncode')
			error = isLliurexupInstalled.get('stderrs')
			self.log(f"Installing lliurex-up. Returncode: {returncode}. Error: {error}")

			if returncode == 0:
				return {"status": True,"data": ""}

			
			isLliurexupUpdated = self.llxUpCore.isLliurexUpIsUpdated()
			if isLliurexupUpdated:
				return {"status": True,"data": ""}

			return {"status": False, "data":error}
			
		except Exception as e:
			errorMsg=str(e)
			self.log(f"Installing lliurex-up. Error: {errorMsg}")
			return {"status": False, "data": errorMsg}

	#def installLliurexUp	

	def getLliurexVersionLocal(self):
		
		defaultVersion={
			"installed": None,
			"candidate": None,
			"updataSouce": None
		}
		
		try:
			
			self.lliurexVersionLocal = self.llxUpCore.getLliurexVersionLocal()

			logLines=[
				f"Get LliurexVersion installed: {self.lliurexVersionLocal.get("installed")}",
				f"Get LliurexVersion candidate from local repository: {self.lliurexVersionLocal.get("candidate")}",
				f"Get Update source:{self.lliurexVersionLocal.get("updateSource")}"]

			self.log("\n".join(logLines))

		except Exception as e:
			self.log(f"Get LliurexVersion from local repository. Error: {e}")
			self.lliurexVersionLocal = defaultVersion

		return self.lliurexVersionLocal

	#def getLliurexVersionLocal(
	
	def getLliurexVersionNet(self):
		
		self.lliurexVersionNet = None
		try:
			self.lliurexVersionNet = self.llxUpCore.getLliurexVersionLliurexNet().get("candidate")
			self.log(f"Get LliurexVersion candidate from lliurex.gva.es: {self.lliurexVersionNet}")
		except Exception as e:
			self.log(f"Get LliurexVersion from lliurex.gva.es. Error: {e}")

		return self.lliurexVersionNet	

	#def getLliurexVersionNet
	
	def installInitialFlavour(self,flavourToInstall):

		try:
			isFlavourInstalled = self.llxUpCore.installInitialFlavour(flavourToInstall)
			returncode = isFlavourInstalled.get('returncode')
			error = isFlavourInstalled.get('stderrs')
			self.log(f"Install initial metapackage: {flavourToInstall}: Returncode: {returncode} Error: {error}")
			return {"status":returncode,"data":error}
		except Exception as e:
			self.log(f"Install initial metapackage: {flavourToInstall}. Error: {error}")
			return {"status": 1, "data":str(e)}
			
	#def installInitialFlavour

	def getPackagesToUpdate(self):
		
		packagesParsed = []
		totalBytes = 0
		
		try:
			packages=self.llxUpCore.getPackagesToUpdate()

			for item,info in packages.items():
				version = info.get("candidate")
				rawSize = info.get("size",0)
				totalBytes += rawSize
				sizeStr = self.convertSize(rawSize)

				install = info.get("installed")
				architecture = info.get("architecture")

				packagesParsed.append(f"{item};{version};{size};{install};{architecture}")
					
			self.log(f"Get packages to update. Number of packages: {len(packages)}") 

		except Exception as e:
			self.log(f"Get packages to update. Error: {e}")

		self.totalSize = self.convertSize(self.totalSize)
		self.getPackagesData(packagesParsed)	

		return {"packages":packagesParsed,"upgradeSize":self.totalSize}
			
	#def getPackagesToUpdate
	
	'''
	def getSizePackagesToUpdate(self,pkg):
		
		size=0
		try:
			command='apt-cache show ' + pkg + ' |grep "^Size:" |cut -d " " -f2 |head -1'
			p=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
			size=p.stdout.readline()
			if type(size) is bytes:
				size=size.decode()
			size=size.strip()
			self.totalSize=(self.totalSize)+int(size)
			size=self.convertSize(size)
			return size

		except Exception as e:
			print(e)
			return self.convertSize(size) 

	#def getSizePackagesToUpdate
	'''
	def convertSize(self,sizeBytes):

		try:
			sizeBytes = float(sizeBytes)
		except (ValueError,TypeError):
			return "0 B"

		if sizeBytes <= 0:
			return "0 B"

		sizeName = ("B", "KB", "MB", "GB" , "TB")
		i = min(int(math.floor(math.log(sizeBytes, 1024))),len(sizeName) -1)
		p = math.pow(1024, i)
		s = round(sizeBytes/p, 1) if i >= 2 else int(round(sizeBytes / p))

		return f"{s} {sizeName[i]}"

	#def convertSize

	def getPackagesData(self,packages):

		self.newPackages = 0
		self.packagesData = []
		self.numberPackagesDownloaded = []
		self.numberPackagesUnpacked = []
		self.numberPackagesInstalled = []
		self.initialNumberPackages = []

		for item in packages:
			parts = item.split(";")
			if len(parts) < 5:
				continue

			pkgId,pkgVersion,pkgSize,installStatus,arch = parts[:5]

			if installStatus == "None":
				self.newPackages += 1

			pkgInfo = {
				"pkgId": pkgId,
				"pkgVersion": pkgVersion,
				"pkgSize": pkgSize,
				"pkgIcon": self._parseDesktop(installStatus,pkgId),
				"pkgStatus": 0,
				"showStatus": False
			}

			self.packagesData.append(tmp)
			pkgFullId = f"{pkgId}_{pkgVersion}"
			self.numberPackagesDownloaded.append(f"{pkgVersion}_{arch}.deb")
			self.numberPackagesUnpacked.append(pkgFullId)
			self.numberPackagesInstalled.append(pkgFullId)
			self.initialNumberPackages.append(pkgFullId)

	#def getPackagesData

	def _parseDesktop(self,installed,name):

		defaultPkgIcon = self.standardIconPath / "package.png"

		if installed is None or str(installed) == "None":
			newPkgIcon = self.standardIconPath / "new_package.png"
			return str(newPkgIcon if newPkgIcon,exists() else defaultPkgIcon)


		desktopFile=self.desktopsPath / f"{name}.desktop"

		if not desktopFile.is_file():
			return str(defaultPkgIcon)

		try:
			config = configparser.ConfigParser()
			config.optionxform=str
			config.read(desktopFile,encodiing="utf-8")

			if not config.has_section("Desktop Entry"):
				return str(defaultPkgIcon)

			entryType = config.get("Desktop Entry","Type",fallback="").lower()
			rawIcon = config.get("Desktop Entry","Icon",fallback="").strip()

			if not rawIcon or entryType == "zomando":
				return str(defaultPkgIcon)

			iconPath = Path(rawIcon)

			if len(iconPath.parts) > 1 or iconPath.is_absolute():
				return str(iconPath if iconPath.exists() else defaultPkgIcon)

			iconExt = iconPath.suffix.lower()
			systemIconDir = self.systemIconPath
			scalablaIconDir = self.systemScalableIconPath

			if iconExt ==".xpm":
				return str(defaultPkgIcon)
			elif iconExt == ".png":
				candidate == systemIconDir / iconPath.name
			elif iconExt == ".svg":
				candidate = scalablaIconDir / iconPath.name
			elif iconExt == "":
				pngCandidate = systemIconDir / f"{iconPath.name}.png"
				svgCandidate = scalablaIconDir / f"{iconPath.name}.svg"
				candidate = pngCandidate  if pkgCandidate,exists() else svgCandidate
			else:
				candidate = systemIconDir / iconPath.name

			return str(candidate if candidate.exists() else defaultPkgIcon)
				
		except Exception as e:
			return str(defaultPkgIcon)

	#def parseDesktop

	def checkIncorrectFlavours(self):

		incorrectFlavours = self.llxUpCore.checkIncorrectFlavours()

		if incorrectFlavours,get('status'):
			self.log(f"Checking incorrect metapackages. Others metapackages detected: {incorrectFlavours.get('status')}. Detected flavours: {incorrectFlavours.get('data')}")
		else:
			self.log("Checking incorrect metapackages. Others metapackages not detected")

		return incorrectFlavours	

	#def checkIncorrectFlavours	

	def getPackageChangelog(self,package):

		changelogFile= self.llxUpCore.changelogsPath / package
		changelog="Changelog not found"

		if not changelogFile.is_file():
			customEnv = os.environ.copy()
			customEnv["LANG"] = "C"
			customEnv["LANGUAGE"] = "en"

			try:
				result = subprocess.run(
					["apt-get","changelog", package],
					env=customEnv,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True,
					errors="replace",
					check=False
				)

				if result.returncode != 0 or not result.stdout.strip():
					return changelog

				cleanLines = [
					line for line in result.stdout.splitlines()
					if not line.starswith("Get:")
				]

				cleanText = "\n".join(cleanLines).replace("\n","\n")

				self.llxUpCore.changelogsPath.mkdir(parents=True,exists_ok=True)
				changelogFile.write_text(cleanText,encodiing="utf-8")

				return cleanText

			except Exception as e:
				return changelog

		try:
			return changelogFile.read_text(encoding="utf-8",errors="replace")
		except Exception:
			return changelog

	#def getPackageChangelog

	def manageSettingsOptions(self):

		showSettings = True
		
		return showSettings

	#def manageSettinsgOptions

	def getSystrayStatus(self):

		if self.disableSystrayToken.exists():
			self.isSystrayEnabled=False
		else:
			self.isSystrayEnabled=True

		self.currentConfig["systraryEnabled"] = self.isSystrayEnabled

	#de isSystrayEnabled

	def manageSystray(self,enable):

		try:
			if enable:
				self.disableSystrayToken.unlink(missing_ok=True)
			else:
				self.disableSystrayToken.mkdir(parents=True,exist_ok=True)
				self.disableSystrayToken.touch(exist_ok=True)
		
			return True
		except OSError as e:
			return False

	#def manageSystray

	def preActionsScript(self):

		self.preActions = self.llxUpCore.preActionsScript()
		self.preActions = f'DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high {self.preActions} ;touch {self.preactionsToken}\n'
		self.log("Exec Pre-Actions")

		return self.preActions

	#def preActionsScript	

	def distUpgradeProcess(self):
		
		self.distupgrade = self.llxUpCore.distUpgradeProcess()	
		self.distupgrade = f'DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high {self.distupgrade} ;touch {self.upgradeToken}\n'
		self.log("Exec Dist-uggrade")

		return self.distupgrade

	#def distUpgradeProcess
	
	def checkErrorDistUpgrade(self):

		try:
			checkDistUpgrade = self.llxUpCore.checkErrorDistUpgrade()
			hasError = checkDistUpgrade.get("status")
			errorDetails = checkDistUpgrade.get("data")

			if hasError or self.errorCheckFlavour:
				error = True
				self.log(f"Dist-upgrade process ending with errors. {errorDetails}")
			else:			
				self.log("Dist-upgrade process ending OK")
				return False

		except Exception as e:
			self.log(f"Error checking distupgrade. Error: {e}")
			return True
	
	#def checkErrorDistUpgrade
	
	def checkInstalledStatus(self):

		self.packagesInstalled=[]

		try:
			result = subprocess.run(
				["dpkg-query","-W","-f=${db:Status-Abbrev}\t${Package}\t{Version}\n"],newConfig
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				errors="replace",
				check=False
			)

			for line in result.stdout.splitlines():
				parts = line.split("\n")

				if len(parts) == 3 and pars[0].strip() == "ii":
					pkgName = parts[1].split(":")[0]
					pkgVersion = parts[2].strip()
					self.packagesInstalled.append(f"{pkgName}_{pkgVersion}")

		except Exception as e:
			print(str(e))
			pass

	#def checkInstalledStatus						

	def checkFinalFlavour(self):

		self.errorCheckFlavour=False
		flavourToInstall=None
		
		self.checkFinalN4dStatus()

		try:
			flavourToInstall=self.llxUpCore.checkFlavour(True)
			msgLog="Final check metapackage. Metapackage to install: %s"%str(flavourToInstall)
			self.log(msgLog)

		except Exception as e:
			self.errorCheckFlavour=True
			msgLog="Final check metapackage. Error: %s"%str(e)
			self.log(msgLog)

		return flavourToInstall	
	
	#def checkFinalFlavour
	
	def installFinalFlavour(self,flavourToInstall):

		self.command=self.llxUpCore.installFinalFlavour(flavourToInstall)
		self.command='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high %s 2> >(tee %s );touch %s\n'%(self.command,self.errorFinalMetapackageToken,self.installflavourToken)
		msgLog="Install final metapackage"
		self.log(msgLog)
		return self.command

	#def installFinalFlavour

	def postActionsScript(self):

		self.postActions=self.llxUpCore.postActionsScript()
		self.postActions='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high %s 2> >(tee %s); touch %s\n'%(self.postActions,self.errorPostactionToken,self.postactionsToken)

		msgLog="Exec Post-Actions"
		self.log(msgLog)
		return self.postActions

	#def postActionsScript

	def checkFinalN4dStatus(self):

		self.llxUpCore.checkN4dStatus()

		if not self.llxUpCore.n4dStatus:
			msgLog="N4d is not working"

			self.log(msgLog)

	#def checkFinalN4dStatus

	def updatePackagesData(self,finalUpdate=False):

		if finalUpdate:
			self.checkInstalledStatus()

		for item in self.packagesData:
			pkgName=item["pkgId"]
			pkgVersion=item["pkgVersion"]
			tmpName=pkgName+"_"+pkgVersion
			if finalUpdate:
				if tmpName not in self.packagesInstalled:
					item["pkgStatus"]=-1

				item["showStatus"]=True
			else:
				if tmpName in self.packagesInstalled:
					item["showStatus"]=True

	#def updatePackagesData		

	def cleanEnvironment(self):
		
		try:
			self.llxUpCore.cleanEnvironment()
			msgLog="Clean environment: OK"
			self.log(msgLog)

		except Exception as e:
			msgLog="Clean environment. Error: %s"%str(e)
			self.log(msgLog)				

	#def cleanEnvironment

	def cleanLliurexUpLock(self):

		try:
			self.llxUpCore.cleanLliurexUpLock()
		
		except Exception as e:
			print(e)
	
	#def cleanLliurexUpLock		

	def searchMeta(self,meta):
		
		match=False
		try:
			match=self.llxUpCore.search_meta(meta)
			return match
		except Exception as e:
			return match

	#def searchMeta			

	def log(self,msg):
		
		logFile="/var/log/lliurex-up.log"
		f=open(logFile,"a+")
		f.write(msg + '\n')
		f.close()

	#def log

	def checkUser(self):
		
		return self.llxUpCore.isUserAdmin()

	#def checkUser

	def checkProgressDownload(self):

		for i in range(len(self.numberPackagesDownloaded)-1,-1,-1):
			if os.path.exists(os.path.join(self.aptCachePath,self.numberPackagesDownloaded[i].replace(":","%3a"))):
				self.numberPackagesDownloaded.pop(i)

		self.progressDownload=len(self.initialNumberPackages)-len(self.numberPackagesDownloaded)
		self.progressDownloadPercentage=round(self.progressDownload/len(self.initialNumberPackages),2)

	#def checkProgressDownload

	def checkProgressUnpacked(self):

		checkInstalledPkg=False
		tmpPackagesUnpacked=self.checkUnpackedStatus()

		if self.progressUnpacked>=len(self.numberPackagesUnpacked):
			self.checkProgressInstallation()
			checkInstalledPkg=True
		
		for i in range(len(self.numberPackagesUnpacked)-1,-1,-1):
			if self.numberPackagesUnpacked[i] in tmpPackagesUnpacked:
				self.numberPackagesUnpacked.pop(i)
			else:
				if checkInstalledPkg:
					if self.numberPackagesUnpacked[i] in self.packagesInstalled:
						self.numberPackagesUnpacked.pop(i)

		if checkInstalledPkg and len(self.numberPackagesUnpacked)<10:
			if self.progressInstallation > len(self.numberPackagesUnpacked):
				self.numberPackagesUnpacked=[]

		self.progressUnpacked=len(self.initialNumberPackages)-len(self.numberPackagesUnpacked)
		self.progressUnpackedPercentage=round(self.progressUnpacked/len(self.initialNumberPackages),2)

	#def checkProgressUnpacked

	def checkProgressInstallation(self):

		self.checkInstalledStatus()
		for i in range(len(self.numberPackagesInstalled)-1,-1,-1):
			if self.numberPackagesInstalled[i] in self.packagesInstalled:
				self.numberPackagesInstalled.pop(i)

		self.progressInstallation=len(self.initialNumberPackages)-len(self.numberPackagesInstalled)
		self.progressInstallationPercentage=round(self.progressInstallation/len(self.initialNumberPackages),2)

	#def checkProgressInstallation
	
	def checkUnpackedStatus(self):
		
		cmd="dpkg -l | awk '/^.U/'"

		tmpPackages=[]

		try:
			p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
			for line in iter(p.stdout.readline,b""):
				if type(line) is bytes:
					line=line.decode()

				tmp=str(line.strip().split()[1].split(":")[0])+"_"+str(line.strip().split()[2])
				tmpPackages.append(tmp)

		except Exception as e:
			print(str(e))
			pass

		return tmpPackages
	
	#def checkUnpackedStatus

	def applySettingsChanges(self,newConfig):
		
		'''
			-0: Systray
		'''
		CHANGES_APPLY_OK=0
		SYSTRAY_ERROR=-1
		
		retSystray=True
		error=False

		if newConfig[0]!=self.currentConfig[0]:
			retSystray=self.manageSystray(newConfig[0])
			if retSystray:
				changesInSystray=True

		if newConfig[1]!=self.currentConfig[1]:
			retEnableService=self.manageAutoUpgrade(newConfig[1])
			if retEnableService:
				changesInAutoUpdate=True

		if retEnableService:
			if newConfig[2]!=self.currentConfig[2]:
				pauseNeedUpdate=True
			elif newConfig[3]!=self.currentConfig[3]:
				pauseNeedUpdate=True
			elif newConfig[4]!=self.currentConfig[4]:
				pauseNeedUpdate=True

		if pauseNeedUpdate:
			retPauseUpdate=self.manageUpdatePause(newConfig[2],newConfig[3],newConfig[4])
			if retPauseUpdate:
				changesInAutoUpdate=True

		if changesInSystray:
			self.getSystrayStatus()
		
		if changesInAutoUpdate:
			self.getAutoUpgradeInfo()
		
		if retSystray and retEnableService and retPauseUpdate:
			return [error,CHANGES_APPLY_OK]

		elif not retSystray and retEnableService and retPauseUpdate:
			error=True
			return [error,SYSTRAY__ERROR]
		elif retSystray and not retEnableService and retPauseUpdate:
			error=True
			return [error,AUTOUPGRADE_ERROR]
		elif retSystray and retEnableService and not retPauseUpdate:
			error=True
			return [error,AUTOUPGRADE_PAUSE_ERROR]
		else:
			error=True
			return [error,CHANGES_APPLY_ERROR]

	#def applySettingsChanges

	def flatpakActionsScript(self):

		self.flatpakActions=self.llxUpCore.flatpakActionsScript()
		self.flatpakActions='%s ;touch %s;exit\n'%(self.flatpakActions,self.flatpakActionsToken)

		msgLog="Exec Update-Flatpak"
		self.log(msgLog)
		return self.flatpakActions

	#def flatpakActionsScript
	
	def getFlapakUpdateInfo(self):
		
		flatPakUpdateInfo=[0,"0"]

		flatPakUpdateInfo=self.llxUpCore.getFlatpakUpdateInfo()
		msgLog="Flatpak update info: %s"%str(flatPakUpdateInfo)
		self.log(msgLog)
		
		return flatPakUpdateInfo
	
	#def getFlapakUpdateInfo

	def _clearCache(self):
		
		clear=False
		installedVersion=self._getPackageVersion()

		versionFile="/root/.lliurex-up.conf"
		cachePath="/root/.cache/lliurex-up"
	
		try:
			if not os.path.exists(versionFile):
				clear=True
			else:
				with open(versionFile,'r') as fd:
					fileVersion=fd.readline().strip()

				if fileVersion!=installedVersion:
					clear=True

			if clear:
				with open(versionFile,'w') as fd:
					fd.write(installedVersion)

				if os.path.exists(cachePath):
					shutil.rmtree(cachePath)
		except:
			pass

	#def clearCache

	def _getPackageVersion(self):

		packageVersionFile="/var/lib/lliurex-up/version"
		pkgVersion=""

		if os.path.exists(packageVersionFile):
			with open(packageVersionFile,'r') as fd:
				pkgVersion=fd.readline().strip()

		return pkgVersion

	#def _getPackageVersion


#class LliurexUpConnect			
