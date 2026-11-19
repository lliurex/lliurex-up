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

	KIRIGAMI_MSG_OK = 0
	KIRIGAMI_MSG_ERROR = 1 
	KIRIGAMI_MSG_WARNING = 2
	KIRIGAMI_MSG_INFO = 3


	def __init__(self):

		self.llxUpCore = LliurexUpCore.LliurexUpCore()

		self.preactionsToken = self.llxUpCore.processPath / "preactions_token"
		self.upgradeToken = self.llxUpCore.processPath / "upgrade_token"
		self.installflavourToken = self.llxUpCore.processPath / "installflavour_token"
		self.postactionsToken = self.llxUpCore.processPath / "postactions_token"
		self.errorPostactionToken = self.llxUpCore.errorPostactionToken
		self.errorUpgradeToken = self.llxUpCore.errorUpgradeToken
		self.errorFinalMetapackageToken = self.llxUpCore.errorFinalMetapackageToken
		self.finalUpgradeToken = self.llxUpCore.finalUpgradeToken
		self.packagesData = []
		self.desktopsPath = Path("/usr/share/applications")
		self.standardIconPath = Path("/usr/share/lliurex-up/rsrc")
		self.systemIconPath = Path("/usr/share/icons/hicolor/48x48/apps")
		self.systemScalableIconPath = Path("/usr/share/icons/hicolor/scalable")
		self.disableSystrayPath = Path("/etc/lliurex-up-indicator")
		self.disableSystrayToken = self.disableSystrayPath / "disableIndicator.token"
		self.isSystrayEnabled = True
		self.pendingDownloads = set()
		self.pendingUnpacked = set()
		self.pendingInstalled = set ()
		self.initialNumberPackages = set()
		self.packagesInstalled = set()
		self.progressDownload = 0
		self.progressDownloadPercentaje = 0.00
		self.progressInstallation = 0
		self.progressInstallationPercentage = 0.00
		self.progressUnpacked = 0
		self.progressUnpackedPercentage = 0.00
		self.aptCachePath = Path("/var/cache/apt/archives")
		self.currentConfig = {"systrayEnabled":self.isSystrayEnabled}
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
			freeSpace = round(usage.free / (1024**3),2)
		except Exception as e:
			self.log(f"Error checking disk space on /: {e}")
			return {"enoughSpace": False,"freeSpace": 0.0}

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
		arg = "initActions"

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

	def isLliurexUpUpdated(self):

		try:
			isLliurexupUpdated = self.llxUpCore.isLliurexUpUpdated()
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

			logLines = [
				f"Get LliurexVersion installed: {self.lliurexVersionLocal.get("installed")}",
				f"Get LliurexVersion candidate from local repository: {self.lliurexVersionLocal.get("candidate")}",
				f"Get Update source:{self.lliurexVersionLocal.get("updateSource")}"
			]

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
			self.log(f"Install initial metapackage: {flavourToInstall}. Error: {e}")
			return {"status": 1, "data":str(e)}
			
	#def installInitialFlavour

	def getPackagesToUpdate(self):
		
		try:
			packageInfo = self.llxUpCore.getPackagesToUpdate()
			packages = packageInfo.get("packagesToUpdate")
			totalSize = packageInfo.get("totalSize")

			self.log(f"Get packages to update. Number of packages: {len(packages)}") 

		except Exception as e:
			self.log(f"Get packages to update. Error: {e}")

		self.getPackagesData(packages)	

		return {"totalPackages":len(packages),"upgradeSize":totalSize}
			
	#def getPackagesToUpdate
	
	def getPackagesData(self,packages):

		self.newPackages = 0
		self.packagesData = []
		self.pendingDownloads = set()
		self.pendingUnpacked = set()
		self.pendingInstalled = set()
		self.initialNumberPackages = set()
		self.totalPackagesCount = len(packages)

		for pkgId,info in packages.items():
			pkgVersion = info.get("candidate","")
			pkgSize = info.get("size", "0 B")
			installStatus = info.get("install")
			arch = info.get("architecture","")
			
			if installStatus is None or str(installStatus) == "None":
				self.newPackages += 1

			pkgInfo = {
				"pkgId": pkgId,
				"pkgVersion": pkgVersion,
				"pkgSize": pkgSize,
				"pkgIcon": self._parseDesktop(installStatus,pkgId),
				"pkgStatus": 0,
				"showStatus": False
			}

			self.packagesData.append(pkgInfo)
			pkgFullId = f"{pkgId}_{pkgVersion}"
			self.pendingDownloads.add(f"{pkgFullId}_{arch}.deb".replace(":","%3a"))
			self.pendingUnpacked.add(pkgFullId)
			self.pendingInstalled.add(pkgFullId)
			self.initialNumberPackages.add(pkgFullId)

	#def getPackagesData

	def _parseDesktop(self,installed,name):

		defaultPkgIcon = self.standardIconPath / "package.png"

		if installed is None or str(installed) == "None":
			newPkgIcon = self.standardIconPath / "new_package.png"
			return str(newPkgIcon if newPkgIcon.exists() else defaultPkgIcon)


		desktopFile=self.desktopsPath / f"{name}.desktop"

		if not desktopFile.is_file():
			return str(defaultPkgIcon)

		try:
			config = configparser.ConfigParser()
			config.optionxform=str
			config.read(desktopFile,encoding="utf-8")

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
				candidate = pngCandidate  if pngCandidate.exists() else svgCandidate
			else:
				candidate = systemIconDir / iconPath.name

			return str(candidate if candidate.exists() else defaultPkgIcon)
				
		except Exception as e:
			return str(defaultPkgIcon)

	#def parseDesktop

	def checkIncorrectFlavours(self):

		incorrectFlavours = self.llxUpCore.checkIncorrectFlavours()

		if incorrectFlavours.get('status'):
			self.log(f"Checking incorrect metapackages. Others metapackages detected: {incorrectFlavours.get('status')}. Detected flavours: {incorrectFlavours.get('data')}")
		else:
			self.log("Checking incorrect metapackages. Others metapackages not detected")

		return incorrectFlavours	

	#def checkIncorrectFlavours	

	def getPackageChangelog(self,package):

		changelogFile = self.llxUpCore.changelogsPath / package
		changelog = "Changelog not found"

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

				changelog = "\n".join(cleanLines).replace("\n","\n")

				return changelog

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
			self.isSystrayEnabled = False
		else:
			self.isSystrayEnabled = True

		self.currentConfig["systrayEnabled"] = self.isSystrayEnabled

	#de isSystrayEnabled

	def manageSystray(self,enable):

		try:
			if enable:
				self.disableSystrayToken.unlink(missing_ok=True)
			else:
				self.disableSystrayPath.mkdir(parents=True,exist_ok=True)
				self.disableSystrayToken.touch(exist_ok=True)
	
			return True
		except OSError as e:
			return False

	#def manageSystray

	def preActionsScript(self):

		preActionsCommand = self.llxUpCore.preActionsScript()
		preActionsCommand = f'DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high {preActionsCommand} ;touch {self.preactionsToken}\n'
		self.log("Exec Pre-Actions")

		return preActionsCommand

	#def preActionsScript	

	def distUpgradeProcess(self):
		
		distupgradeCommand = self.llxUpCore.distUpgradeProcess()	
		distupgradeCommand = f'DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high {distupgradeCommand} ;touch {self.upgradeToken}\n'
		self.log("Exec Dist-uggrade")

		return distupgradeCommand

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
	
	def checkFinalFlavour(self):

		self.errorCheckFlavour = False
		flavourToInstall = None
		
		self.checkFinalN4dStatus()

		try:
			flavourToInstall = self.llxUpCore.checkFlavour(True)
			self.log(f"Final check metapackage. Metapackage to install: {flavourToInstall}")

		except Exception as e:
			self.errorCheckFlavour = True
			self.log(f"Final check metapackage. Error: {e}")

		return flavourToInstall	
	
	#def checkFinalFlavour
	
	def installFinalFlavour(self,flavourToInstall):

		installFlavourCommand = self.llxUpCore.installFinalFlavour(flavourToInstall)
		installFlavourCommand = f'DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high {installFlavourCommand} 2> >(tee {self.errorFinalMetapackageToken} );touch {self.installflavourToken}\n'
		self.log("Install final metapackage")

		return installFlavourCommand

	#def installFinalFlavour

	def postActionsScript(self):

		postActionsCommand = self.llxUpCore.postActionsScript()
		postActionsCommand = f'DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high {postActionsCommand} 2> >(tee {self.errorPostactionToken} ); touch {self.postactionsToken}\n'
		self.log("Exec Post-Actions")

		return postActionsCommand

	#def postActionsScript

	def checkFinalN4dStatus(self):

		self.llxUpCore.checkN4dStatus()

		if not self.llxUpCore.n4dStatus:
			self.log("N4d is not working")

	#def checkFinalN4dStatus

	def updatePackagesData(self,finalUpdate=False):

		if finalUpdate:
			_ = self._getDpkgState()

		for item in self.packagesData:
			if item["showStatus"] and not finalUpdate:
				continue

			tmpName = f"{item["pkgId"]}_{item["pkgVersion"]}"

			if tmpName in self.packagesInstalled:
				item["showStatus"] = True
			elif finalUpdate:
				item["pkgStatus"] = 1
				item["showStatus"] = True

	#def updatePackagesData		

	def cleanEnvironment(self):
		
		try:
			self.llxUpCore.cleanEnvironment()
			self.log("Clean environment: OK")
		except Exception as e:
			self.log(f"Clean environment. Error: {e}")

	#def cleanEnvironment

	def cleanLliurexUpLock(self):

		try:
			self.llxUpCore.cleanLliurexUpLock()
		except Exception as e:
			print(e)
	
	#def cleanLliurexUpLock		

	def searchMeta(self,meta):
		
		match = False
		try:
			match = self.llxUpCore.search_meta(meta)
			return match
		except Exception as e:
			return match

	#def searchMeta			

	def log(self,msg):
		
		logFile = Path("/var/log/lliurex-up.log")
		
		logFile.parent.mkdir(parents=True,exist_ok=True)

		with logFile.open("a",encoding="utf-8") as fd:
			fd.write(f"{msg}\n")

	#def log

	def checkUser(self):
		
		return self.llxUpCore.isUserAdmin()

	#def checkUser

	def checkProgressDownload(self):

		if self.totalPackagesCount == 0:
			self.progressDownload = 0
			self.progressDownloadPercentage = 1.0

		self.pendingDownloads = {
			pkg for pkg in self.pendingDownloads
			if not (self.aptCachePath / pkg).exists()
		}

		self.progressDownload = self.totalPackagesCount - len(self.pendingDownloads)
		self.progressDownloadPercentage = round(self.progressDownload / self.totalPackagesCount,2)

	#def checkProgressDownload

	def _getDpkgState(self):

		unpackedOrMore = set()
		self.packagesInstalled = set()

		try:
			pkgNames = [p["pkgId"] for p in self.packagesData]

			if not pkgNames:
				return unpackedOrMore

			result = subprocess.run(
				["dpkg-query", "-W", "-f=${db:Status-Abbrev}\t${Package}\t${Version}\n"] + pkgNames,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				errors="replace",
				check=False
			)

			for line in result.stdout.splitlines():
				parts = line.split("\t")
				if len(parts) != 3:
					continue

				status = parts[0].strip()
				pkgName = parts[1].split(":")[0]
				pkgVersion = parts[2].strip()
				pkgFullId = f"{pkgName}_{pkgVersion}"

				if status == "ii":
					self.packagesInstalled.add(pkgFullId)
					unpackedOrMore.add(pkgFullId)
				elif len(status) >=2 and status[1] in ("U","F","H"):
					unpackedOrMore.add(pkgFullId)

		except Exception as e:
			self.log(f"Error checkgin pkg status: {e}")

		return unpackedOrMore

	#def _getDpkgState

	def checkProgressUnpacked(self):

		if self.totalPackagesCount == 0:
			return

		unpackedOrMore = self._getDpkgState()

		self.pendingUnpacked -= unpackedOrMore
		self.pendingInstalled -= self.packagesInstalled

		self.progressUnpacked = self.totalPackagesCount - len(self.pendingUnpacked)
		self.progressUnpackedPercentage = round(self.progressUnpacked / self.totalPackagesCount,2)

		self.progressInstallation = self.totalPackagesCount - len(self.pendingInstalled)
		self.progressInstallationPercentage = round(self.progressInstallation / self.totalPackagesCount,2)

		
	#def checkProgressUnpacked

	def checkProgressInstallation(self):

		if self.totalPackagesCount == 0:
			return

		_ = self._getDpkgState()

		self.pendingInstalled -= self.packagesInstalled

		self.progressInstallation = self.totalPackagesCount - len(self.pendingInstalled)
		self.progressInstallationPercentage = round(self.progressInstallation / self.totalPackagesCount,2)

	#def checkProgressInstallation

	def applySettingsChanges(self,newConfig):
		
		'''
			-0: Systray
		'''
		CHANGES_APPLY_OK = 0
		SYSTRAY_ERROR = -1
		
		changesInSystray = False
		retSystray = True

		if newConfig.get("systrayEnabled") != self.currentConfig.get("systrayEnabled"):
			retSystray = self.manageSystray(newConfig.get("systrayEnabled"))
			if retSystray:
				changesInSystray = True

		if changesInSystray:
			self.getSystrayStatus()
				
		if retSystray:
			return {"status": True,"code":CHANGES_APPLY_OK,"type": self.KIRIGAMI_MSG_OK}

		else:
			return {"status": False,"code":SYSTRAY_ERROR,"type": self.KIRIGAMI_MSG_ERROR}		
	
	#def applySettingsChanges

	def flatpakActionsScript(self):

		self.flatpakActions = self.llxUpCore.flatpakActionsScript()
		self.flatpakActions = f'{self.flatpakActions} ;touch {self.flatpakActionsToken};exit\n'

		self.log("Exec Update-Flatpak")
		
		return self.flatpakActions

	#def flatpakActionsScript
	
	def getFlapakUpdateInfo(self):
		
		flatPakUpdateInfo = {"totalFlatpak":0,"size":"0 B"}

		flatPakUpdateInfo = self.llxUpCore.getFlatpakUpdateInfo()
		self.log(f"Flatpak update info: {flatPakUpdateInfo}")
		
		return flatPakUpdateInfo
	
	#def getFlapakUpdateInfo

	def _clearCache(self):
		
		clear = False
		installedVersion = self._getPackageVersion()

		versionFile="/root/.lliurex-up.conf"
		cachePath="/root/.cache/lliurex-up"
	
		try:
			if not os.path.exists(versionFile):
				clear = True
			else:
				with open(versionFile,'r') as fd:
					fileVersion=fd.readline().strip()

				if fileVersion!=installedVersion:
					clear = True

			if clear:
				with open(versionFile,'w') as fd:
					fd.write(installedVersion)

				if os.path.exists(cachePath):
					shutil.rmtree(cachePath)
		except:
			pass

	#def clearCache

	def _getPackageVersion(self):

		packageVersionFile = "/var/lib/lliurex-up/version"
		pkgVersion = ""

		if os.path.exists(packageVersionFile):
			with open(packageVersionFile,'r') as fd:
				pkgVersion=fd.readline().strip()

		return pkgVersion

	#def _getPackageVersion


#class LliurexUpConnect			
