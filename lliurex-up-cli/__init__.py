#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lliurex.lliurexup
import os
import subprocess
import multiprocessing
import sys
import shutil
import datetime
import time
import signal
import psutil
signal.signal(signal.SIGINT,signal.SIG_IGN)

class LliurexUpCli(object):
	def __init__(self):

		self.lliurexUpCore = lliurex.lliurexup.LliurexUpCore()
		signal.signal(signal.SIGINT,self._handlerSignal)
		self.lliurexUpCore.checkLocks()
		self.checkingBlock = True
		self.configureRequired = False
		self.isUserAdmin = self.lliurexUpCore.isUserAdmin()
	
	#def __init__
	
	def _startLliurexUp(self,mode):

		self.checkingBlock = False
		self.lliurexUpCore.startLliurexUp()

		if mode == "sai":
			self.mode = mode
			self.initActionsArg = "initActionsSai"
		else:
			self.mode = "normal"
			self.initActionsArg = "initActions"	

		print("  [Lliurex-Up]: Checking n4d service status...")
		
		self._freeSpaceCheck()
		self._checkInitialN4dStatus()

	#def _startLliurexUp

	def _checkInitialN4dStatus(self):

		self.statusN4d = self.lliurexUpCore.n4dStatus
		
		if not self.statusN4d:
			msgLog="N4d is not working"
			print(f"  [Lliurex-Up]: {msgLog}")
			self._log(msgLog)

	#def _checkInitialN4dStatus
	
	def _checkInitialFlavour(self):

		self.targetMetapackage = self.lliurexUpCore.checkInitialFlavour()
		msgLog = f"Initial check metapackage. Metapackage to install: {self.targetMetapackage}"
		self._log(msgLog)
		msgLog = f"Get initial flavours: {self.lliurexUpCore.previousFlavours}"
		self._log(msgLog)

	#def _checkInitialFlavour	
		
	def _canConnectToLliurexNet(self):

		print("  [Lliurex-Up]: Checking connection to lliurex.gva.es...")

		canConnect = self.lliurexUpCore.canConnectToLliurexNet()
		msgLog = f"Checking connection to lliurex.gva.es: {canConnect}"
		self._log(msgLog)
		if canConnect.get("status"):
			msgLog = "Can connect to lliurex.gva.es: True"
			self._log(msgLog)
			return True
	
		msgLog = "Can connect to lliurex.gva.es: False"
		self._log(msgLog)
		if self.initActionsArg =="initActionsSai":
			return True
		
		print("  [Lliurex-Up]: Unable to connect to lliurex.gva.es")
		return False
				
	#def _canConnectToLliurexNet		

	def _addSourcesList(self):

		self.lliurexUpCore.addSourcesListLliurex()						
	
	#def _addSourcesList
				
	def _initActionsScript(self):

		print("  [Lliurex-Up]: Executing init actions...")
		self.configureRequired = False

		command = self.lliurexUpCore.initActionsScript(self.initActionsArg)
		envVars = None

		if self.extraArgs.get("unattendend_upgrade"):
			envVars = os.environ.copy()
			envVars["DEBIAN_FRONTEND"] = "noninteractive"

		try:
			result = subprocess.run(
				command,
				env=envVars,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True
			)

			outputErr = result.stderr or ""

			if self.readErrorOutput(outputErr):
				if 'dpkg --configure -a' in outputErr:
					self.configureRequired=True

				print(f"  [Lliurex-Up]: Executing init actions. Error:\n{outputErr}")
				msgLog = f"Exec Init-Actions. Error: {outputErr}"
			else:
				msgLog = "Exec Init-Actions. OK"
			
		except Exception as e:
			msgLog = f"Exec Init-Actions.Error:{e}"
			print(f"  [Lliurex-Up]: Checking system. Error:\n{e}")

			
		self._log(msgLog)	
			
	#def _initActionsScript
	
	def _checkLliurexUp(self):

		print("  [Lliurex-Up]: Looking for new version of Lliurex Up...")

		isLliurexUpUpdated = self.lliurexUpCore.isLliurexUpIsUpdated()
		restart = False

		msgLog = f"Checking Lliurex-Up. Is Lliurex-Up updated: {isLliurexUpUpdated}"
		self._log(msgLog)

		if isLliurexUpUpdated:
			print("  [Lliurex-Up]: Lliurex-Up is updated.Nothing to do")
			return True	
		
		print("  [Lliurex-Up]: Updating Lliurex-Up...")

		isLliurexUpInstalled = self.lliurexUpCore.installLliurexUp()
		code = isLliurexUpInstalled.get("returncode")
		data = isLliurexUpInstalled.get('stderrs')
		msgLog = f"Installing Lliurex-Up. Returncode: {code}. Error: {data}"
		self._log(msgLog)

		if code == 0:
			restart = True

		else:
			isLliurexUpUpdated = self.lliurexUpCore.isLliurexUpIsUpdated()
			if not isLliurexUpUpdated:
				msgLog = "Unable to update Lliurex-Up"
				self._log(msgLog)
				print(f"  [Lliurex-Up]: Unable to update Lliurex-Up. Error: {data}")
				restart = False
			else:
				restart = True

		if restart:
			print("  [Lliurex-Up]: Lliurex-Up is now update and will be reboot now..." )
			time.sleep(3)
			self.lliurexUpCore.cleanLliurexUpLock()
			os.execv("/usr/sbin/lliurex-upgrade",sys.argv)
		else:
			return False
			
	#def _checkLliurexUp		

	def _getLliurexVersionLocal(self):

		print("  [Lliurex-Up]: Looking for LliurexVersion from local repository...")
		
		self.versionToUpdate = self.lliurexUpCore.getLliurexVersionLocal()
		msgLog = f"Get LliurexVersion installed: {self.versionToUpdate.get('installed')}"
		self._log(msgLog)
		msgLog = f"Get LliurexVersion candidate from local repository: {self.versionToUpdate['candidate']}"
		self._log(msgLog)
		msgLog = f"Get Update source: {self.versionToUpdate.get('updateSource')}"
		self._log(msgLog)

	#def _getLliurexVersionLocal	

	def _getLliurexVersionLliurexNet(self):
	
		print("  [Lliurex-Up]: Looking for LliurexVersion from lliurex.gva.es...")

		self.versionAvailable = self.lliurexUpCore.getLliurexVersionLliurexNet()
		msgLog = f"Get LliurexVersion candidate from lliurex.gva.es: {self.versionAvailable.get('candidate')}"
		self._log(msgLog)
	
	#def _getLliurexVersionLliurexNet		

	def _checkingInitialFlavourToInstall(self):

		print("  [Lliurex-Up]: Checking if installation of metapackage is required...")

		self.returnCodeInitFlavour = 0
		if len(self.targetMetapackage)==0:
			print("  [Lliurex-Up]: Installation of metapackage is not required")
			return
			
		print(f"  [Lliurex-Up]: Installation of metapackage is required: {self.targetMetapackage}")
		isFlavourInstalled = self.lliurexUpCore.installInitialFlavour(self.targetMetapackage)	
		self.returnCodeInitFlavour = isFlavourInstalled.get('returncode')
		error = isFlavourInstalled.get('stderrs')
		msgLog = f"Install initial metapackage: {self.targetMetapackage}: Returncode: {self.returnCodeInitFlavour} Error: {error}"
		self._log(msgLog)
		print(f"  [Lliurex-Up]: Metapackage is now installed: Returncode: {self.returnCodeInitFlavour} Error: {error}")
			
	#def _checkingInitialFlavourToInstall		
	
	def _getPackagesToUpdate(self):

		print("  [Lliurex-Up]: Looking for new updates...")
		packages = self.lliurexUpCore.getPackagesToUpdate()
		msgLog = f"Get packages to update. Number of packages: {len(packages)}"
		self._log(msgLog)

		self.newPackages = 0
		collectedPackages = []

		for item in packages:
			if packages[item].get("install") is None:
				self.newPackages+=1

			collectedPackages.append(item)

		self.packagesList = f"{' '.join(collectedPackages)}" if collectedPackages else ""

		return packages

	#def _getPackagesToUpdate		
			
	def _checkingIncorrectFlavours(self):
		
		incorrectFlavours = self.lliurexUpCore.checkIncorrectFlavours()
		self.aditionalFlavours = incorrectFlavours.get("data")
		msgLog = f"Checking incorrect metapackages. Others metapackages detected: {incorrectFlavours.get('status')}. Detected Flavours: {self.aditionalFlavours}"
		self._log(msgLog)

		return incorrectFlavours.get('status')
	
	#def _checkingIncorrectFlavours		
		
	def checkPreviousUpgrade(self):
		
		if self.returnCodeInitFlavour != 0:
			return True

		if self.versionToUpdate.get("candidate") is not None:
			if self.versionToUpdate.get("installed") != self.versionToUpdate.get("candidate"):
				return True

		if self.versionToUpdate.get("installed") != self.versionAvailable.get("candidate"):	
			return True 

		return False

	#def checkPreviousUpgrade		

	def _preActionsScript(self):

		print("  [Lliurex-Up]: Preparing system to update...")

		command = self.lliurexUpCore.preActionsScript()
		envVars = None

		if self.extraArgs.get("unattendend_upgrade"):
			envVars = os.environ.copy()
			envVars["DEBIAN_FRONTEND"] = "noninteractive"

		try:
			result = subprocess.run(
				command,
				env=envVars,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True
			)

			outputErr = result.stderr
			error = self.readErrorOutput(outputErr)

			if error:
				print(f"  [Lliurex-Up]: Preparing system to update. Error:\n{outputErr}")
				msgLog = f"Exec Pre-Actions. Error: {outputErr}"
			else:
				msgLog="Exec Pre-Actions. OK"

		except Exception as e:
			print(f"  [Lliurex-Up]: Preparing system to update. Error:\n{e}")
			msgLog = f"Exec Pre-Actions. Error {e}"
			
		self._log(msgLog)	

	#def _preActionsScript			

	def _distUpgrade(self):

		print("  [Lliurex-Up]: Downloading and installing packages...")

		command = self.lliurexUpCore.distUpgradeProcess()
		envVars = None

		if self.extraArgs.get("unattendend_upgrade"):
			envVars = os.environ.copy()
			envVars["DEBIAN_FRONTEND"] = "noninteractive"

		try:
			result = subprocess.run(
				command,
				env=envVars,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True
			)

			outputErr = result.stderr
			error = self.readErrorOutput(outputErr)

			if error:
				print(f"  [Lliurex-Up]: Downloading and installing packages. Error:\n{outputErr}")
				msgLog = f"Exec Dist-upgrade. Error: {outputErr}"
			else:
				msgLog = "Exec Dist-upgrade. OK"
		
		except Exception as e:
			print(f"  [Lliurex-Up]: Downloading and installing packages. Error:\n{e}")
			msgLog = f"Exec Dist-uggrade.Error: {e}"

		self._log(msgLog)	
			
	#def _distUpgrade		

	def _postActionsScript(self):

		print("  [Lliurex-Up]: Ending the update...")

		self.postActionError = False

		command = self.lliurexUpCore.postActionsScript()
		envVars = None

		if self.extraArgs.get("unattendend_upgrade"):
			envVars = os.environ.copy()
			envVars["DEBIAN_FRONTEND"] = "noninteractive"

		try:
			result = subprocess.run(
				command,
				env=envVars,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True
			)

			outputErr = result.stderr
			error = self.readErrorOutput(outputErr)

			if error:
				print(f"  [Lliurex-Up]: Ending the update. Error:\n{outputErr}")
				self.postActionError = True
				msgLog = f"Exec Post-Actions. Error: {outputErr}"
			else:
				msgLog = "Exec Post-Actions.OK"
			
		except Exception as e:
			self.postActionError = True
			print(f"  [Lliurex-Up]: Ending the update. Error:{e}")
			msgLog = f"Exec Post-Actions.Error: {e}"

		self._log(msgLog)	

	#def _postActionsScript			

	def readErrorOutput(self,output):

		if "E: " in output:
			return True

		return False

	#def readErrorOutput

	def _checkFinalN4dStatus(self):

		print("  [Lliurex-Up]: Checking N4d status...")

		self.lliurexUpCore.checkN4dStatus()
		
		if not self.lliurexUpCore.n4dStatus:
			msgLog = "N4d is not working"
			self._log(msgLog)

	#def _checkFinalN4dStatus		

	def _checkingFinalFlavourToInstall(self):
		
		print("  [Lliurex-Up]: Checking final metapackage...")
		self.finalMetaPackageError = False
		self._checkFinalN4dStatus()

		try:
			self.flavourToInstall = self.lliurexUpCore.checkFlavour(True)

			msgLog = f"Final check metapackage. Metapackage to install:{self.flavourToInstall}"
			self._log(msgLog)
							
			if len(self.flavourToInstall) == 0:
				print("  [Lliurex-Up]: Metapackage is correct. Nothing to do")
				return


			print("  [Lliurex-Up]: Install of metapackage is required:%s"%str(self.flavourToInstall))
			
			command = self.lliurexUpCore.installFinalFlavour(self.flavourToInstall)
			envVars = None

			if self.extraArgs.get("unattendend_upgrade"):
				envVars = os.environ.copy()
				envVars["DEBIAN_FRONTEND"] = "noninteractive"

			try:
				result = subprocess.run(
					command,
					env=envVars,
					shell=True,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True
				)

				outputErr = result.stderr
				error = self.readErrorOutput(outputErr)

				if error:
					self.finalMetaPackageError=True
					print(f"  [Lliurex-Up]: Install of metapackage. Error:\n{outputErr}")
					msgLog = f"Final install metapackage. Error {outputErr}"
				else:
					msgLog = "Final install metapackage.OK"
				
			except Exception as e:
				self.finalMetaPackageError = True
				print(f"  [Lliurex-Up]: Install of metapackage. Error:\n{e}")
				msgLog = "Install of metapackage. Error: %s"%str(e)

				self._log(msgLog)	

		except Exception as e:	
			self.finalMetaPackageError = True
			print(f"  [Lliurex-Up]: Checking Metapackage. Error:\n{e}")
			msgLog = f"Final check metapackage. Error: {e}"	
			self._log(msgLog)	
			
	#def _checkingFinalFlavourToInstall

	def _getFlatpakUpdateInfo(self):

		flatpakInfo = {"totalFlatpak":0,"size":0}
		
		flatpakInfo = self.lliurexUpCore.getFlatpakUpdateInfo()
		msgLog = f"Flatpak update info:{flatpakInfo}"
		self._log(msgLog)

		return flatpakInfo

	#def _getFlatpakUpdateInfo

	def _flatpakActionsScript(self):

		print("  [Lliurex-Up]: Updating Flatpak applications...")

		self.errorFlatpakActions = False

		command = self.lliurexUpCore.flatpakActionsScript()
	
		try:
			result = subprocess.run(
				command,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True
			)

			outputErr = result.stderr
			error = self.readErrorOutput(outputErr)

			if error:
				print(f"  [Lliurex-Up]: Updating flatpak. Error:\n{outputErr}")
				self.errorFlatpakActions = True
				msgLog = f"Exec UpdateFlatpak. Error: {outputErr}"
			else:
				msgLog = "Exec UpdateFlatpak.OK"
			
		except Exception as e:
			self.errorFlatpakActions=True
			print(f"  [Lliurex-Up]: Updating flatpak. Error:\n{e}")
			msgLog = f"Exec UpdateFlatpak.OK: {e}"

		self._log(msgLog)	

	#def _flatpakActionsScript			
		
	def _checkFinalUpgrade(self):

		print("  [Lliurex-Up]: Checking Dist-upgrade...")
		errorInfo= self.lliurexUpCore.checkErrorDistUpgrade()
		isError = errorInfo.get("status")
		errorDetails = errorInfo.get("errorDetails")

		if isError or self.finalMetaPackageError or self.postActionError :
			print("  [Lliurex-Up]: The updated process is endend with errors")
			msgLog = f"Dist-upgrade process ending with errors. {errorDetails}"
			self.distUpgradeOK = False
		
		else:					
			print("  [Lliurex-Up]: The system is now update")	
			msgLog = "Dist-upgrade process ending OK"
			self.distUpgradeOK = True

		self._log(msgLog)
		
	#def _checkFinalUpgrade	

	def _cleanEnvironment(self):

		self.lliurexUpCore.cleanEnvironment()
		self.lliurexUpCore.cleanLliurexUpLock()

		if self.initActionsArg == "initActionsSai":
			origPinningPath = "/usr/share/lliurex-up/templates/lliurex-pinning.cfg"
			destPinningPath = "/etc/apt/preferences.d/lliurex-pinning"
			shutil.copy(origPinningPath,destPinningPath)

		return

	#def _cleanEnvironment		

	def _handlerSignal(self,signal,frame):
		
		print("\n  [Lliurex-Up]: Cancel process with Ctrl+C signal")
		msgLog = "Cancel process with Ctrl+C signal"
		self._log(msgLog)
		if not self.checkingBlock:
			self._cleanEnvironment()
		
		sys.exit(0)
	
	#def _handlerSignal

	def _log(self,msg):
		
		logFile = "/var/log/lliurex-up.log"
		try:
			with open(logFile,"a",encoding="utf-8") as f:
				f.write(f"{msg}\n")
		except IOError:
			pass
	
	#def _log

	def _freeSpaceCheck(self):
		
		#freeSpace=(os.statvfs("/").f_bfree * os.statvfs("/").f_bsize) / (1024*1024*1024)

		try:
			freeSpaceBytes = psutil.disk_usage("/").free
			freeSpaceFormatedGB = freeSpaceBytes/(1024**3)

			if (freeSpaceFormatedGB) >= 2:
				return True

			availableSpace = f"{round(freeSpaceFormatedGB,2)} GB"
			msgLog = f"There's not enough space on disk to upgrade: 2 GB needed - {availableSpace} available"
			
			print(f"  [Lliurex-Up]: {msgLog}")
			self._log(msgLog)
			self._cleanEnvironment()
			sys.exit(1)
		except Exception as e:
			msgLog = f"Error checking disk space: {e}"
			print(f"  [Lliurex-Up]: {msgLog}")
			self._log(msgLog)
			self._cleanEnvironment()
			sys.exit(1)
	
	#def _freeSpaceCheck		

	def _isLliurexUpLocked(self):

		print("  [Lliurex-Up]: Checking if LliureX-Up is running...")

		code = self.lliurexUpCore.isLliurexUpLocked()
		msgLog="------------------------------------------\n"+"LLIUREX-UP-CLI STARTING AT: " + datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") +"\n------------------------------------------"

		if code == 0:
			self._log(msgLog)
			return

		if code!=1:
			self._log(msgLog)
		
		self._manageLocker(code,"Lliurex-Up")	
	
	#def isLliurexUpLocked	

	def _isAptLocked(self):

		print("  [Lliurex-Up]: Checking if Apt is running...")

		code = self.lliurexUpCore.isAptLocked()
		
		if code !=0:
			self._manageLocker(code,"Apt")	

	#def isAptLocked		

	def _isDpkgLocked(self):

		print("  [Lliurex-Up]: Checking if Dpkg is running...")

		code=self.lliurexUpCore.isDpkgLocked()

		if code !=0:
			self._manageLocker(code,"Dpkg")	
	
	#def _isDpkgLocked

	def _manageLocker(self,code,action):

		unlocker = False

		if code == 1:
			if action != "Lliurex-Up":
				msgLog = f"{action} is running"
				self._log(msgLog)
			print(f"  [Lliurex-Up]: {action} is now running. Wait a moment and try again")
			sys.exit(1)
		
		elif code == 3:
			msgLog = "Apt is running"
			self._log(msgLog)
			print("  [Lliurex-Up]: Apt is now running. Wait a moment and try again")
			sys.exit(1)
		
		elif code == 2:
			msgLog = f"{action} is locked"
			self._log(msgLog)

			if not self.extraArgs.get("unattendend_upgrade"):
				response = input( f'  [Lliurex-Up]:{action} seems blocked by a failed previous execution. Lliurex-Up can not continue if this block is maintained.You want to try to unlock it (yes/no)?')
				if response.startswith('y'):
					self._pulsate_unlockingProcess()
					unlocker = True
		
			if not unlocker:
				print(f"  [Lliurex-Up]: {action} seems blocked by a failed previous execution. Unabled to update de sytem")
				sys.exit(1)

		return True		

	#def _manageLocker

	def _pulsate_unlockingProcess(self):

		self.endProcess = False
		
		resultQueue = multiprocessing.Queue()
		self.unlocking_t = multiprocessing.Process(target=self._unlockingProcess,args=(resultQueue,))
		self.unlocking_t.start()
		
		progressbar = ["[    ]","[=   ]","[==  ]","[=== ]","[====]","[ ===]","[  ==]","[   =]","[    ]","[   =]","[  ==]","[ ===]","[====]","[=== ]","[==  ]","[=   ]"]
		i = 1

		while self.unlocking_t.is_alive():
			time.sleep(0.5)
			per = i % 16
			print(f"  [Lliurex-Up]: The unlocking process is running. Wait a moment {progressbar[per]}",end='\r')

			i += 1

		print(" " * 80, end='\r')
		sys.stdout.flush()

		result = resultQueue.get()
		
		if result == 0:
			msgLog="The unlocking process finished successfully"
			self._log(msgLog)
			args = ["/usr/sbin/lliurex-upgrade"] + sys.argv[1:]
			os.execv("/usr/sbin/lliurex-upgrade",args)
		else:
			if result == 1:
				print("  [Lliurex-Up]: The unlocking process has failed")
				msgLog="The unlocking process has failed"
			else:
				print("  [Lliurex-Up]: Some process are running. Wait a moment and try again")
				msgLog="Some process are running. Wait a moment and try again"
	
			self._log(msgLog)
			sys.exit(1)

	#def _pulsate_unlockingProcess

	def _unlockingProcess(self,resultQueue):

		try:
			cmd = self.lliurexUpCore.unlockerCommand()
			p = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,check=False)
			resultQueue.put(p.returncode)
		except Exception:
			resultQueue.put(1)

	#def _unlockingProcess

	def updateAction(self,mode,extraArgs=None):

		self.extraArgs = extraArgs
		self._isLliurexUpLocked()
		self._isAptLocked()
		self._isDpkgLocked()
		self._startLliurexUp(mode)
		self._checkInitialFlavour()

		msgLog = f"Mode of execution: {self.mode}"
		self._log(msgLog)
		msgLog = f"Extra args: {self.extraArgs}"
		self._log(msgLog)
			
		if not self._canConnectToLliurexNet():
			self._cleanEnvironment()
			return 1
			
		self._addSourcesList()
		self._initActionsScript()

		if not self._checkLliurexUp():
			self._cleanEnvironment()
			return 1

		self._getLliurexVersionLocal()
		self._getLliurexVersionLliurexNet()
		self._checkingInitialFlavourToInstall()
		self.packages = self._getPackagesToUpdate()
		self.flatPakUpdateInfo = self._getFlatpakUpdateInfo()

		if len(self.packages) > 0:
			if not self._checkingIncorrectFlavours():
				print(f"  [Lliurex-Up]: List of packages to update:\n{self.packagesList}")
				print(f"  [Lliurex-Up]: Number of packages to update:       {len(self.packages)} ({self.newPackages} news)")
				print(f"  [Lliurex-Up]: Current version:                    {self.versionToUpdate.get('installed')}")
				print(f"  [Lliurex-Up]: Available version (lliurex.gva.es): {self.versionAvailable.get('candidate')}")
				print(f"  [Lliurex-Up]: Candidate version (to install):     {self.versionToUpdate.get('candidate')}")
				print(f"  [Lliurex-Up]: Update source:                      {self.versionToUpdate.get('updateSource')}")
				if self.flatPakUpdateInfo.get("totalFlatpak") >0:
					print(f"  [Lliurex-Up]: Flatpak update info:                Number of Flatpak: {self.flatPakUpdateInfo.get('totalFlatpak')} - Size: < {self.flatPakUpdateInfo.get('size')}")

				
				if self.configureRequired:
					print(f"  [Lliurex-Up]: dpkg --configure -a must be executed. You can use dpkg-unlocker for this")
				if not self.extraArgs["unattendend_upgrade"]:
					response=input('  [Lliurex-Up]: Do you want to update the system (yes/no)): ').lower()
				else:
					response="yes"

				if not response.startswith('y'):
					msgLog = "Cancel the update"
					self._log(msgLog)
					print("  [Lliurex-Up]: Cancel the update")
					self._cleanEnvironment()
					return 0

				self._preActionsScript()
				self._distUpgrade()
				self._postActionsScript()
				time.sleep(5)
				self._checkingFinalFlavourToInstall()
				
				if self.flatPakUpdateInfo.get("totalFlatpak") > 0:
					self._flatpakActionsScript()	
				
				self._checkFinalUpgrade()
				self._cleanEnvironment()
				
				if self.distUpgradeOK:
					return 0
				else:
					return 1
			else:
				print(f"[Lliurex-Up]: Updated abort for incorrect flavours detected in new update. Detected flavours: {self.aditionalFlavours}")
				msgLog = "Updated abort for incorrect flavours detected in new update"
				self._log(msgLog)
				self._cleanEnvironment()
				return 1			
		else:
			if not self.checkPreviousUpgrade():
				print(f"  [Lliurex-Up]: Current version:                 {self.versionToUpdate.get('installed')}")
				print(f"  [Lliurex-Up]: Available version (lliurex.gva.es): {self.versionAvailable.get('candidate')}")
				print(f"  [Lliurex-Up]: Candidate version (to install):  {self.versionToUpdate.get('candidate')}")
				print(f"  [Lliurex-Up]: Update source:                   {self.versionToUpdate.get('updateSource')}")
				print("  [Lliurex-Up]: Your system is updated. Nothing to do")
				msgLog = "System updated. Nothing to do"
				self._log(msgLog)
				self._cleanEnvironment()
				return 0
			else:
				print("  [Lliurex-Up]: Updated abort. An error occurred checking new updates")
				msgLog=" Updated abort. An error occurred checking new updates"
				self._log(msgLog)
				self._cleanEnvironment()
				return 1

	#def updateAction
	
#class LliurexUpCli
