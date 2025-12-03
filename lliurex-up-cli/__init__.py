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
		self.defaultMirror = self.lliurexUpCore.defaultMirror
		signal.signal(signal.SIGINT,self.handlerSignal)
		self.lliurexUpCore.checkLocks()
		self.checkingBlock=True
		self.configureRequired=False
		self.currentDay=datetime.date.today().isoformat()
		self.isUserAdmin=self.lliurexUpCore.isUserAdmin()
		self.isDesktopInADI=False
		self.isMirrorInADI=self.lliurexUpCore.isMirrorInADI
	
	#def __init__
	
	def startLliurexUp(self,mode):

		self.checkingBlock=False
		self.lliurexUpCore.startLliurexUp()

		if mode=="sai":
			self.mode=mode
			self.initActionsArg="initActionsSai"
		else:
			self.mode="normal"
			self.initActionsArg="initActions"	

		print("  [Lliurex-Up]: Checking n4d service status...")
		
		self.freeSpaceCheck()
		self.checkInitialN4dStatus()

	#def startLliurexUp

	def checkInitialN4dStatus(self):

		self.statusN4d=self.lliurexUpCore.n4dStatus
		
		if not self.statusN4d:
			msgLog="N4d is not working"
			print("  [Lliurex-Up]: %s"%msgLog)
			self.log(msgLog)

	#def checkInitialN4dStatus
	
	def checkInitialFlavour(self):

		self.targetMetapackage=self.lliurexUpCore.checkInitialFlavour()
		msgLog="Initial check metapackage. Metapackage to install: %s"%str(self.targetMetapackage)
		self.log(msgLog)
		msgLog="Get initial flavours: %s"%str(self.lliurexUpCore.previousFlavours)
		self.log(msgLog)
		
		self.isMirrorInADI=self.lliurexUpCore.isMirrorInADI
		self.canConnectToADI=self.lliurexUpCore.canConnectToADI

	#def checkInitialFlavour	
		
	def canConnectToLliurexNet(self):

		print("  [Lliurex-Up]: Checking connection to lliurex.net...")

		canConnect=self.lliurexUpCore.canConnectToLliurexNet()
		msgLog="Checking connection to lliurex.net: %s"%canConnect
		self.log(msgLog)
		if canConnect['status']:
			msgLog="Can connect to lliurex.net: True"
			self.log(msgLog)
			return True
		else:
			msgLog="Can connect to lliurex.net: False"
			self.log(msgLog)

			if self.canConnectToADI:
				if self.isMirrorInADI:
					return True
			else:
				if self.initActionsArg =="initActionsSai":
					return True

			return False
				
			print("  [Lliurex-Up]: Unable to connect to lliurex.net")
			return True
				
	#def canConnectToLliurexNet		

	def desktopCheckingMirrorExists(self):

		print("  [Lliurex-Up]: Checking if mirror exists in ADI...")
		isMirrorExists=self.lliurexUpCore.desktopCheckingMirrorExists()
		msgLog="Checking if mirrror exists in ADI. MirrorManager response: %s"%isMirrorExists['data']
		self.log(msgLog)
		if not isMirrorExists["ismirroravailable"]:
			msgLog="Mirror not detected in ADI"
			print("  [Lliurex-Up]: Mirror not detected in ADI")
			self.log(msgLog)
		else:
			print("  [Lliurex-Up]: Nothing to do with mirror")

		self.lliurexUpCore.addSourcesListLliurex()						
	
	#def desktopCheckingMirrorExists
				
	def desktopCheckingMirrorIsRunning(self):
		
		isMirrorRunningInADI=self.lliurexUpCore.desktopCheckingMirrorIsRunning()
		msgLog="Checking if mirrror in ADI is being updated. MirrorManager response: %s"%isMirrorRunningInADI['data']
		self.log(msgLog)		
		
		if isMirrorRunningInADI['ismirrorrunning']:
			msgLog="Mirror is being updated in ADI. Unable to update the system"
			self.log(msgLog)
		
		return isMirrorRunningInADI['ismirrorrunning']
		
			
	#def desktopCheckingMirrorIsRunning		
	
	def initActionsScript(self):

		print("  [Lliurex-Up]: Executing init actions...")
		self.configureRequired=False

		if self.extraArgs["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive %s"%self.lliurexUpCore.initActionsScript(self.initActionsArg)
		
		else:
			command=self.lliurexUpCore.initActionsScript(self.initActionsArg)
		
		try:
			
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				outputErr=output[1].decode()
			else:
				outputErr=output[1]	
			error=self.readErrorOutput(outputErr)
			if error:
				if 'dpkg --configure -a' in outputErr:
					self.configureRequired=True
				print("  [Lliurex-Up]: Executing init actions. Error:\n%s"%str(outputErr))
				msgLog="Exec Init-Actions. Error: %s"%str(outputErr)
			else:
				msgLog="Exec Init-Actions. OK"
			
		except Exception as e:
			msgLog="Exec Init-Actions.Error: %s"%str(e)
			print("  [Lliurex-Up]: Checking system. Error:\n%s"%str(e))

			
		self.log(msgLog)	
			
	#def initActionsScript
	
	def checkLliurexUp(self):

		print("  [Lliurex-Up]: Looking for new version of Lliurex Up...")

		isLliurexUpUpdated=self.lliurexUpCore.isLliurexUpIsUpdated()
		restart=False

		if not isLliurexUpUpdated:
			print("  [Lliurex-Up]: Updating Lliurex-Up...")
			isLliurexUpInstalled=self.lliurexUpCore.installLliurexUp()
			msgLog="Installing Lliurex-Up. Returncode: %s. Error: %s"%(str(isLliurexUpInstalled['returncode']),str(isLliurexUpInstalled['stderrs']))
			self.log(msgLog)
			if isLliurexUpInstalled['returncode']==0:
				restart=True
			else:
				isLliurexUpUpdated=self.lliurexUpCore.isLliurexUpIsUpdated()
				if not isLliurexUpUpdated:
					msgLog="Unable to update Lliurex-Up"
					self.log(msgLog)
					print("  [Lliurex-Up]: Unable to update Lliurex-Up. Error: %s"%str(isLliurexUpInstalled['stderrs']))
					restart=False
				else:
					restart=True

			if restart:
				print("  [Lliurex-Up]: Lliurex-Up is now update and will be reboot now..." )
				time.sleep(3)
				self.lliurexUpCore.cleanLliurexUpLock()
				os.execv("/usr/sbin/lliurex-upgrade",sys.argv)
			else:
				return False

		else:
			msgLog="Checking Lliurex-Up. Is Lliurex-Up updated: %s"%str(isLliurexUpUpdated)
			self.log(msgLog)
			print("  [Lliurex-Up]: Lliurex-Up is updated.Nothing to do")
			return True	
			
	#def checkLliurexUp		

	def checkMirror(self):

		print("  [Lliurex-Up]: Checking if mirror is updated...")

		try:
			isMirrorUpdated=self.lliurexUpCore.lliurexMirrorIsUpdated()

			if isMirrorUpdated !=None:
				msgLog="Checking mirror. MirrorManager response: %s"%isMirrorUpdated['data']
				self.log(msgLog)
				try:
					isMirrorRunning=self.lliurexUpCore.lliurexMirrorIsRunning()
					if isMirrorRunning:
						print("  [Lliurex-Up]: Updating mirror. Wait a moment please...")
						self.updateMirrorProgress()
					else:
						if isMirrorUpdated['action']=='update':
							if not isMirrorRunning:
								msgLog="Checking mirror. Is mirror update: False"
								self.log(msgLog)
								if not self.extraArgs["unattended_mirror"]:
									response=input('  [Lliurex-Up]: Do you want update mirror (yes/no): ').lower()
								else:
									response="yes"

								if response.startswith('y'):
									msgLog="Update lliurex-mirror. Response: Yes"
									self.log(msgLog)
									print("  [Lliurex-Up]: Updating mirror. Wait a moment please...")
									command='lliurex-mirror update %s'%self.defaultMirror
									subprocess.Popen(command,shell=True).communicate()

								else:
									msgLog="Update lliurex-mirror. Response: No"
									self.log(msgLog)
									print("  [Lliurex-Up]: Mirror update. Not update")	
						else:
							msgLog="Checking mirror. Is mirror update: nothing-to-do"
							self.log(msgLog)
							print("  [Lliurex-Up]: %s"%msgLog)
				
				except Exception as e:
					msgLog="Updating mirror. Error: %s"%str(e)
					self.log(msgLog)	
					print("  [Lliurex-Up]: Updating mirror. Error: %s"%str(e))
											
			else:
				msgLog="Checking mirror. Is mirror update: None"
				self.log(msgLog)
				print("  [Lliurex-Up]: Nothing to do with mirror")
		
		except Exception as e:
			msgLog="Checking mirror. Error: %s"%str(e)
			self.log(msgLog)	
			print("  [Lliurex-Up]: Checking mirror. Error: %s"%str(e)) 	
			
	#def checkMirror		

	def updateMirrorProgress(self):

		isMirrorRunning=self.lliurexUpCore.lliurexMirrorIsRunning()
		counter = 0
		percentage = 0
		clockpercentage = 0
		clock = ['—','/','|','\\']

		while isMirrorRunning:
			if  counter ==  0:
				percentage=self.lliurexUpCore.getPercentageLliurexMirror()
				
				if percentage!=None:
					isMirrorRunning=self.lliurexUpCore.lliurexMirrorIsRunning()
					
				else:
					isMirrorRunning=False	

			progress = clock[clockpercentage%4]
			print("{} % {}".format(percentage,progress),end='\r')
			time.sleep(0.1)
			counter += 1
			if counter == 40:
				counter = 0
			clockpercentage +=1
			if clockpercentage == 30:
				clockpercentage = 0	
	
	#def updateMirrorProgress			
		
	def getLliurexVersionLocal(self):

		print("  [Lliurex-Up]: Looking for LliurexVersion from local repository...")
		
		self.versionToUpdate=self.lliurexUpCore.getLliurexVersionLocal()
		msgLog="Get LliurexVersion installed: %s"%str(self.versionToUpdate["installed"])
		self.log(msgLog)
		msgLog="Get LliurexVersion candidate from local repository: %s"%str(self.versionToUpdate["candidate"])
		self.log(msgLog)
		msgLog="Get Update source: %s"%str(self.versionToUpdate["updateSource"])
		self.log(msgLog)

	#def getLliurexVersionLocal	
	

	def getLliurexVersionLliurexNet(self):
	
		print("  [Lliurex-Up]: Looking for LliurexVersion from lliurex.net...")

		self.versionAvailable=self.lliurexUpCore.getLliurexVersionLliurexNet()
		msgLog="Get LliurexVersion candidate from lliurex.net: %s"%str(self.versionAvailable["candidate"])
		self.log(msgLog)
	
	#def getLliurexVersionLliurexNet		

	def checkingInitialFlavourToInstall(self):

		print("  [Lliurex-Up]: Checking if installation of metapackage is required...")

		self.returnCodeInitFlavour=0
		if len(self.targetMetapackage)==0:
			
			print("  [Lliurex-Up]: Installation of metapackage is not required")
			
		else:
			print("  [Lliurex-Up]: Installation of metapackage is required: %s"%str(self.targetMetapackage))
			isFlavourInstalled=self.lliurexUpCore.installInitialFlavour(self.targetMetapackage)	
			self.returnCodeInitFlavour=isFlavourInstalled['returncode']
			error=isFlavourInstalled['stderrs']
			msgLog="Install initial metapackage: %s: Returncode: %s Error: %s"%(str(self.targetMetapackage),str(self.returnCodeInitFlavour),str(error))
			self.log(msgLog)
			print("  [Lliurex-Up]: Metapackage is now installed: Returncode: %s"%str(self.returnCodeInitFlavour) + " Error: " + str(error))
			
	#def checkingInitialFlavourToInstall		
	
	def getPackagesToUpdate(self):

		print("  [Lliurex-Up]: Looking for new updates...")
		packages=self.lliurexUpCore.getPackagesToUpdate()
		msgLog="Get packages to update. Number of packages: %s"%str(len(packages))
		self.log(msgLog)

		self.newPackages=0
		self.packagesList=""
		if (len(packages))>0:
			for item in packages:
				if packages[item]["install"]==None:
						self.newPackages=int(self.newPackages) + 1
				self.packagesList="%s %s "%(str(self.packagesList),item)		

		return packages

	#def getPackagesToUpdate		
			
	def checkingIncorrectFlavours(self):
		
		incorrectFlavours=self.lliurexUpCore.checkIncorrectFlavours()
		self.aditionalFlavours=incorrectFlavours["data"]
		msgLog="Checking incorrect metapackages. Others metapackages detected: %s. Detected Flavours: %s"%(str(incorrectFlavours["status"]),str(self.aditionalFlavours))
		self.log(msgLog)

		return incorrectFlavours['status']
	
	#def checkingIncorrectFlavours		
		
	def checkPreviousUpgrade(self):
		
		error=False
		if self.returnCodeInitFlavour!=0:
			error=True

		else:
			if self.versionToUpdate["candidate"]!=None:
				if self.versionToUpdate["installed"]!=self.versionToUpdate["candidate"]:
					error=True
			else:
				if self.versionToUpdate["installed"]!=self.versionAvailable["candidate"]:	
					error=True

		return error

	#def checkPreviousUpgrade		

	def preActionsScript(self):

		print("  [Lliurex-Up]: Preparing system to update...")

		if self.extraArgs["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive %s"%self.lliurexUpCore.preActionsScript()
		else:
			command=self.lliurexUpCore.preActionsScript()		
		
		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				outputErr=output[1].decode()
			else:
				outputErr=output[1]	
			error=self.readErrorOutput(outputErr)
			if error:
				print("  [Lliurex-Up]: Preparing system to update. Error:\n%s"%str(outputErr))
				msgLog="Exec Pre-Actions. Error: %s"%str(outputErr)
			else:
				msgLog="Exec Pre-Actions. OK"

		except Exception as e:
			print("  [Lliurex-Up]: Preparing system to update. Error:\n%s"%str(e))
			msgLog="Exec Pre-Actions. Error %s"%str(e)
			

		self.log(msgLog)	

	#def preActionsScript			

	def distUpgrade(self):

		print("  [Lliurex-Up]: Downloading and installing packages...")

		if self.extraArgs["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive %s"%self.lliurexUpCore.distUpgradeProcess()
		else:
			command=self.lliurexUpCore.distUpgradeProcess()

		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				outputErr=output[1].decode()
			else:
				outputErr=output[1]	
			error=self.readErrorOutput(outputErr)
			if error:
				print("  [Lliurex-Up]: Downloading and installing packages. Error:\n%s"%str(outputErr))
				msgLog="Exec Dist-upgrade. Error: %s"%str(outputErr)
			else:
				msgLog="Exec Dist-upgrade. OK"
		
		except Exception as e:
			print("  [Lliurex-Up]: Downloading and installing packages. Error:\n%s"%str(e))
			msgLog="Exec Dist-uggrade.Error: %s"%str(e)

		self.log(msgLog)	
			
	#def distUpgrade		

	def postActionsScript(self):

		print("  [Lliurex-Up]: Ending the update...")

		self.postActionError=False

		if self.extraArgs["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive %s"%self.lliurexUpCore.postActionsScript() 
		else:
			command=self.lliurexUpCore.postActionsScript()
	
		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				outputErr=output[1].decode()
			else:
				outputErr=output[1]	
			error=self.readErrorOutput(outputErr)
			if error:
				print("  [Lliurex-Up]: Ending the update. Error:\n%s"%str(outputErr))
				self.postActionError=True
				msgLog="Exec Post-Actions. Error: %s"%str(outputErr)
			else:
				msgLog="Exec Post-Actions.OK"
			
		except Exception as e:
			self.postActionError=True
			print("  [Lliurex-Up]: Ending the update. Error:\n%s"%str(e))
			msgLog="Exec Post-Actions.Error: %s"%str(e)

		self.log(msgLog)	

	#def postActionsScript			

	def readErrorOutput(self,output):

		cont=0
		lines=output.split("\n")
		for line in lines:
			if "E: " in line:
				cont=cont+1

		if cont>0:
			return True
		else:
			return False			

	#def readErrorOutput

	def checkFinalN4dStatus(self):

		print("  [Lliurex-Up]: Checking N4d status...")

		self.lliurexUpCore.checkN4dStatus()
		
		if not self.lliurexUpCore.n4dStatus:
			msgLog="N4d is not working"
			self.log(msgLog)

	#def checkFinalN4dStatus		

	def checkingFinalFlavourToInstall(self):
		
		print("  [Lliurex-Up]: Checking final metapackage...")
		self.finalMetaPackageError=False
		self.checkFinalN4dStatus()

		try:
			self.flavourToInstall=self.lliurexUpCore.checkFlavour(True)

			msgLog="Final check metapackage. Metapackage to install:%s"%str(self.flavourToInstall)
			self.log(msgLog)
							
			if len(self.flavourToInstall)>0:
				print("  [Lliurex-Up]: Install of metapackage is required:%s"%str(self.flavourToInstall))
			
				if self.extraArgs["unattendend_upgrade"]:
					command="DEBIAN_FRONTEND=noninteractive %s"%self.lliurexUpCore.installFinalFlavour(self.flavourToInstall)
				else:
					command=self.lliurexUpCore.installFinalFlavour(self.flavourToInstall)

				try:

					p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
					output=p.communicate()
					if type(output[1]) is bytes:
						outputErr=output[1].decode()
					else:
						outputErr=output[1]	
					error=self.readErrorOutput(outputErr)
					if error:
						self.finalMetaPackageError=True
						print("  [Lliurex-Up]: Install of metapackage. Error:\n%s"%str(outputErr))
						msgLog="Final install metapackage. Error %s"%str(outputErr)
					else:
						msgLog="Final install metapackage.OK"
				
				except Exception as e:
					self.finalMetaPackageError=True
					print("  [Lliurex-Up]: Install of metapackage. Error:\n%s"%str(e))
					msgLog="Install of metapackage. Error: %s"%str(e)

				self.log(msgLog)	
			else:
				print("  [Lliurex-Up]: Metapackage is correct. Nothing to do")

		except Exception as e:	
			self.finalMetaPackageError=True
			print("  [Lliurex-Up]: Checking Metapackage. Error:\n%s"%str(e))
			msgLog="Final check metapackage. Error: %s"%str(e)	
			self.log(msgLog)	
			
	#def checkingFinalFlavourToInstall

	def getFlatpakUpdateInfo(self):

		flatpakInfo=[0,"0"]
		
		flatpakInfo=self.lliurexUpCore.getFlatpakUpdateInfo()
		msgLog="Flatpak update info: %s"%str(flatpakInfo)
		self.log(msgLog)

		return flatpakInfo

	#def getFlatpakUpdateInfo

	def flatpakActionsScript(self):

		print("  [Lliurex-Up]: Updating Flatpak applications...")

		self.errorFlatpakActions=False

		command=self.lliurexUpCore.flatpakActionsScript()
	
		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				outputErr=output[1].decode()
			else:
				outputErr=output[1]	
			error=self.readErrorOutput(outputErr)
			if error:
				print("  [Lliurex-Up]: Updating flatpak. Error:\n%s"%str(outputErr))
				self.errorFlatpakActions=True
				msgLog="Exec UpdateFlatpak. Error: %s"%str(outputErr)
			else:
				msgLog="Exec UpdateFlatpak.OK"
			
		except Exception as e:
			self.errorFlatpakActions=True
			print("  [Lliurex-Up]: Updating flatpak. Error:\n%s"%str(e))
			msgLog="Exec UpdateFlatpak.OK: %s"%str(e)

		self.log(msgLog)	

	#def flatpakActionsScript			
		
	def checkFinalUpgrade(self):

		print("  [Lliurex-Up]: Checking Dist-upgrade...")
		error=self.lliurexUpCore.checkErrorDistUpgrade()
		errorDetails=str(error[1])

		if error[0] or self.finalMetaPackageError or self.postActionError :
			print("  [Lliurex-Up]: The updated process is endend with errors")
			msgLog="Dist-upgrade process ending with errors. %s"%errorDetails
			self.distUpgradeOK=False
		
		else:					
			print("  [Lliurex-Up]: The system is now update")	
			msgLog="Dist-upgrade process ending OK"
			self.distUpgradeOK=True

		self.log(msgLog)
		
	#def checkFinalUpgrade	

	def cleanEnvironment(self):

		self.lliurexUpCore.cleanEnvironment()
		self.lliurexUpCore.cleanLliurexUpLock()

		if self.initActionsArg =="initActionsSai":
			origPinningPath="/usr/share/lliurex-up/templates/lliurex-pinning.cfg"
			destPinningPath="/etc/apt/preferences.d/lliurex-pinning"
			shutil.copy(origPinningPath,destPinningPath)

		return

	#def cleanEnvironment		

	def handlerSignal(self,signal,frame):
		
		print("\n  [Lliurex-Up]: Cancel process with Ctrl+C signal")
		msgLog="Cancel process with Ctrl+C signal"
		self.log(msgLog)
		if not self.checkingBlock:
			self.cleanEnvironment()
		
		sys.exit(0)
	
	#def handlerSignal

	def log(self,msg):
		
		logFile="/var/log/lliurex-up.log"
		f=open(logFile,"a+")
		f.write(msg + '\n')
		f.close()	
	
	#def log

	def freeSpaceCheck(self):
		
		#freeSpace=(os.statvfs("/").f_bfree * os.statvfs("/").f_bsize) / (1024*1024*1024)

		freeSpace=psutil.disk_usage("/").free/(1024**3)
		if (freeSpace) < 2: #less than 2GB available?
			print("  [Lliurex-Up]: There's not enough space on disk to upgrade: 2 GB needed - %s GB available"%str(round(freeSpace,2)))
			msgLog="There's not enough space on disk to upgrade: %s GB available"%str(round(freeSpace,2))
			self.log(msgLog)
			self.cleanEnvironment()
			sys.exit(1)

	#def freeSpaceCheck		

	def isLliurexUpLocked(self):

		print("  [Lliurex-Up]: Checking if LliureX-Up is running...")

		code=self.lliurexUpCore.isLliurexUpLocked()
		msgLog="------------------------------------------\n"+"LLIUREX-UP-CLI STARTING AT: " + datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") +"\n------------------------------------------"

		if code !=0:
			if code!=1:
				self.log(msgLog)
			self.manageLocker(code,"Lliurex-Up")	
		else:
			self.log(msgLog)
							
		
	#def islliurexup_running	

	def isAptLocked(self):

		print("  [Lliurex-Up]: Checking if Apt is running...")

		code=self.lliurexUpCore.isAptLocked()
		
		if code !=0:
			self.manageLocker(code,"Apt")	

	#def isAptLocked		

	def isDpkgLocked(self):

		print("  [Lliurex-Up]: Checking if Dpkg is running...")

		code=self.lliurexUpCore.isDpkgLocked()

		if code !=0:
			self.manageLocker(code,"Dpkg")	
	
	#def isDpkgLocked

	def manageLocker(self,code,action):

		unlocker=True
		if code==1:
			if action!="Lliurex-Up":
				msgLog=action+" is running"
				self.log(msgLog)
			print("  [Lliurex-Up]: %s is now running. Wait a moment and try again"%action)
		
		elif code==3:
			msgLog="Apt is running"
			self.log(msgLog)
			print("  [Lliurex-Up]: Apt is now running. Wait a moment and try again")
		
		elif code==2:
			msgLog=action+" is locked"
			self.log(msgLog)
			if not self.extraArgs["unattendend_upgrade"]:
				response=input( '  [Lliurex-Up]: %s seems blocked by a failed previous execution. Lliurex-Up can not continue if this block is maintained.You want to try to unlock it (yes/no)?'%action)
				if response.startswith('y'):
					self.pulsate_unlockingProcess()
				else:
					unlocker=False
			else:
				unlocker=False

		if not unlocker:
			print("  [Lliurex-Up]: %s seems blocked by a failed previous execution. Unabled to update de sytem"%action)
		
		sys.exit(1)			

	#def manageLocker

	def pulsate_unlockingProcess(self):

		self.endProcess=False
		
		resultQueue=multiprocessing.Queue()
		self.unlocking_t=multiprocessing.Process(target=self.unlockingProcess,args=(resultQueue,))
		self.unlocking_t.start()
		

		progressbar= ["[    ]","[=   ]","[==  ]","[=== ]","[====]","[ ===]","[  ==]","[   =]","[    ]","[   =]","[  ==]","[ ===]","[====]","[=== ]","[==  ]","[=   ]"]
		i=1
		while self.unlocking_t.is_alive():
			time.sleep(0.5)
			per=i%16
			print("  [Lliurex-Up]: The unlocking process is running. Wait a moment " + progressbar[per],end='\r')

			i+=1

		result=resultQueue.get()
		
		if result ==0:
			sys.stdout.flush()
			msgLog="The unlocking process finished successfully"
			self.log(msgLog)
			os.execv("/usr/sbin/lliurex-upgrade",sys.argv)
		else:
			if result==1:
				print("  [Lliurex-Up]: The unlocking process has failed")
				msgLog="The unlocking process has failed"
			else:
				print("  [Lliurex-Up]: Some process are running. Wait a moment and try again")
				msgLog="Some process are running. Wait a moment and try again"
	
			self.log(msgLog)
			sys.exit(1)


	#def pulsate_unlockingProcess

	def unlockingProcess(self,resultQueue):

		cmd=self.lliurexUpCore.unlockerCommand()
		p=subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,check=False)
		resultQueue.put(p.returncode)

	#def unlockingProcess

	def getAutoUpgradeSettings(self):

		if self.lliurexUpCore.isAutoUpgradeAvailable():
			self.lliurexUpCore.getAutoUpgradeConfig()

	#def getAutoUpgradeSettings

	def disableUpdatePause(self):

		if self.currentDay>=self.lliurexUpCore.dateToUpdate:
			ret=self.lliurexUpCore.manageUpdatePause(False,0)
 
 	#def disableAutoUpdate
	
	def updateAction(self,mode,extraArgs=None):

		self.extraArgs=extraArgs
		self.isLliurexUpLocked()
		self.isAptLocked()
		self.isDpkgLocked()
		self.startLliurexUp(mode)
		self.checkInitialFlavour()

		msgLog="Mode of execution: %s"%str(self.mode)
		self.log(msgLog)
		msgLog="Extra args: %s"%str(self.extraArgs)
		self.log(msgLog)
			
		if not self.canConnectToLliurexNet():
			print("  [Lliurex-Up]: Unable to connect to lliurex.net")
			self.cleanEnvironment()
			return 1
			
		desktopCheckingMirror=self.desktopCheckingMirrorIsRunning()
		
		if desktopCheckingMirror!=False:
			if desktopCheckingMirror:
				print("  [Lliurex-Up]: Mirror is being updated in ADI. Unable to update the system")
	
			self.cleanEnvironment()
			return 1
		else:
			self.desktopCheckingMirrorExists()
				
		self.initActionsScript()
		if not self.checkLliurexUp():
			self.cleanEnvironment()
			return 1

		if self.extraArgs["mirror"]:
			self.checkMirror()

		self.getLliurexVersionLocal()
		self.getLliurexVersionLliurexNet()
		self.checkingInitialFlavourToInstall()
		self.packages=self.getPackagesToUpdate()
		self.getAutoUpgradeSettings()
		self.flatPakUpdateInfo=self.getFlatpakUpdateInfo()

		if len(self.packages)>0:
			if not self.checkingIncorrectFlavours():
				print("  [Lliurex-Up]: List of packages to update:\n%s"%str(self.packagesList))
				print("  [Lliurex-Up]: Number of packages to update:    %s"%str(len(self.packages)) + " (" + str(self.newPackages) + " news)" )
				print("  [Lliurex-Up]: Current version:                 %s"%str(self.versionToUpdate["installed"]))
				print("  [Lliurex-Up]: Available version (lliurex.net): %s"%str(self.versionAvailable["candidate"]))
				print("  [Lliurex-Up]: Candidate version (to install):  %s"%str(self.versionToUpdate["candidate"]))
				print("  [Lliurex-Up]: Update source:                   %s"%str(self.versionToUpdate["updateSource"]))
				if self.flatPakUpdateInfo[0]>0:
					print("  [Lliurex-Up]: Flatpak update info:             Number of Flatpak: %s - Size: < %s"%(str(self.flatPakUpdateInfo[0]),self.flatPakUpdateInfo[1]))

				
				if self.configureRequired:
					print("  [Lliurex-Up]: dpkg --configure -a must be executed. You can use dpkg-unlocker for this")
				if not self.extraArgs["unattendend_upgrade"]:
					response=input('  [Lliurex-Up]: Do you want to update the system (yes/no)): ').lower()
				else:
					response="yes"

				if response.startswith('y'):
					self.lliurexUpCore.stopAutoUpgrade()
					self.preActionsScript()
					self.distUpgrade()
					self.postActionsScript()
					time.sleep(5)
					self.checkingFinalFlavourToInstall()
					if self.flatPakUpdateInfo[0]>0:
						self.flatpakActionsScript()	
					self.checkFinalUpgrade()
					self.cleanEnvironment()
					if self.distUpgradeOK:
						return 0
					else:
						return 1
				else:
					msgLog="Cancel the update"
					self.log(msgLog)
					print("  [Lliurex-Up]: Cancel the update")
					self.cleanEnvironment()

					return 0
			else:
				print("[Lliurex-Up]: Updated abort for incorrect flavours detected in new update. Detected flavours: %s"%str(self.aditionalFlavours))
				msgLog="Updated abort for incorrect flavours detected in new update"
				self.log(msgLog)
				self.cleanEnvironment()

				return 1			
		else:
			if not self.checkPreviousUpgrade():
				print("  [Lliurex-Up]: Current version:                 %s"%str(self.versionToUpdate["installed"]))
				print("  [Lliurex-Up]: Available version (lliurex.net): %s"%str(self.versionAvailable["candidate"]))
				print("  [Lliurex-Up]: Candidate version (to install):  %s"%str(self.versionToUpdate["candidate"]))
				print("  [Lliurex-Up]: Update source:                   %s"%str(self.versionToUpdate["updateSource"]))
				print("  [Lliurex-Up]: Your system is updated. Nothing to do")
				msgLog="System updated. Nothing to do"
				self.log(msgLog)
				self.disableUpdatePause()
				self.cleanEnvironment()

				return 0
			else:
				print("  [Lliurex-Up]: Updated abort. An error occurred checking new updates")
				msgLog=" Updated abort. An error occurred checking new updates"
				self.log(msgLog)
				self.cleanEnvironment()

				return 1
	#def updateAction

	def manageUpdates(self,action,unattendend,weeks_of_pause):

		execute=False
		if self.lliurexUpCore.isLliurexUpLocked()==0:
			if self.lliurexUpCore.isAutoUpgradeAvailable():
				execute=True
				if action in ["enable","disable"]:
					if not self.isUserAdmin:
						print("  [Lliurex-Up]: You not have privlleges to execute this action")
						return 0
			if not execute:
				print("  [Lliurex-Up]: Manage options not available in this computer")
				return 0
			else:
				self.lliurexUpCore.getAutoUpgradeConfig()

				if action=="settings":
					self.showAutoUpdateSettings()
				elif action=="enable":
					self.enableAutoUpdate(unattendend)
				elif action=="disable":
					self.disableAutoUpdate(unattendend)
				elif action=="cancel":
					self.cancelAutoUpdate(unattendend)
				elif action=="pause":
					self.pauseAutoUpdate(unattendend,weeks_of_pause)
				elif action=="extended":
					self.extendedAutoUpdatePause(unattendend,weeks_of_pause)
		else:
			print("  [Lliurex-Up]: LliureX-Up is now running. Wait a moment and try again")
			return 0		

	# manageUpdates

	def showAutoUpdateSettings(self):

		print("  [Lliurex-Up]: Current automatic updates settings:")
		automaticEnabled=self.lliurexUpCore.isAutoUpgradeEnabled()
		print("		- Automatic updates enabled: %s"%str(automaticEnabled))

		if automaticEnabled:
			print("		- Attemps to cancel automatic update: %s"%str(self.lliurexUpCore.cancellationsAvailables))
			weeksOfPause=self.lliurexUpCore.weeksOfPause
			if weeksOfPause>0:
				print("		- Automatic updates paused for: %s weeks"%str(weeksOfPause))
				print("		- The pause of automatic updates can be extended up to: %s weeks"%str(self.lliurexUpCore.extensionPause))
				dateToUpdate=datetime.date.fromisoformat(self.lliurexUpCore.dateToUpdate).strftime("%d/%m/%y")
				print("		- Automatic updates will resume from: %s"%str(dateToUpdate))
	
		return 0

	#def showAutoUpdateSettings

	def enableAutoUpdate(self,unattendend):

		if self.lliurexUpCore.isAutoUpgradeEnabled():
			print("  [Lliurex-Up]: Automatic updates are already enabled. Nothing to do")
		else:
			if not unattendend:
				response=input( '  [Lliurex-Up]: Do you want to enable automatic updates in this compueter (yes/no)?')
			else:
				response="yes"

			if response.startswith('y'):
				ret=self.lliurexUpCore.manageAutoUpgrade(True)
				if ret:
					print("  [Lliurex-Up]: Automatic updates have been successfully activated")
					return 0
				else:
					print("  [Lliurex-Up]: Unable to enable automatic updates")
					return 1
		return 0
	
	#def enableAutoUpdate	

	def disableAutoUpdate(self,unattendend):

		if not self.lliurexUpCore.isAutoUpgradeEnabled():
			print("  [Lliurex-Up]: Automatic updates are already disabled. Nothing to do")
		else:
			if not unattendend:
				response=input( '  [Lliurex-Up]: Do you want to disable automatic updates in this compueter (yes/no)?')
			else:
				response="yes"

			if response.startswith('y'):
				ret=self.lliurexUpCore.manageAutoUpgrade(False)
				if ret:
					print("  [Lliurex-Up]: Automatic updates have been successfully disabled")
					return 0
				else:
					print("  [Lliurex-Up]: Unable to disable automatic updates")
					return 1
		return 0
	
	#def disableAutoUpdate

	def cancelAutoUpdate(self,unattendend):

		if self.lliurexUpCore.isAutoUpgradeEnabled():
			if self.lliurexUpCore.isAutoUpgradeActive():
				if self.lliurexUpCore.canCancelAutoUpdate():
					if not unattendend:
						response=input( '  [Lliurex-Up]: Do you want to cancel automatic update until tomorrow (yes/no)?')
					else:
						response="yes"

					if response.startswith('y'):
						ret=self.lliurexUpCore.stopAutoUpgrade(False)
						if ret:
							print("  [Lliurex-Up]: Automatic updates have been successfully cancelled until tomorrow")
						else:
							print("  [Lliurex-Up]: Unable to cancel automatic updates")
							return 1
				else:
					print("  [Lliurex-Up]: Unable to cancel automatic updates. The attemps to cancel have benn exceed")
			else:
				print("  [Lliurex-Up]: Automatic updates has already cancelled")
		else:
			print("  [Lliurex-Up]: Automatic updates are disabled in this computer")
			
		return 0

	#def cancelAutoUpdate

	def pauseAutoUpdate(self,unattendend,weeksOfPause):

		if self.lliurexUpCore.isAutoUpgradeEnabled():

			if self.lliurexUpCore.weeksOfPause>0:
				print("  [Lliurex-Up]: Paussing of automatic updates is already set. Use the extended-update-pause option instead")
			else:
				if weeksOfPause>5:
					print("  [Lliurex-Up]: Unable to pause automatic updates. The indicate pause weeks exceed the limit")
					return 0
				else:
					if not unattendend:
						response=input( '  [Lliurex-Up]: Do you want to pause automatic update in this computer (yes/no)?')
					else:
						response="yes"

					if response.startswith('y'):
						ret=self.lliurexUpCore.manageUpdatePause(True,weeksOfPause)
						if ret:
							print("  [Lliurex-Up]: Automatic updates have been successfully paused for %s weeks"%str(weeksOfPause))
						else:
							print("  [Lliurex-Up]: Unable to pause automatic updates")
							return 1
						
		else:
			print("  [Lliurex-Up]: Automatic updates are already disabled. Nothing to do")

		return 0
	
	#def pauseAutoUpdate

	def extendedAutoUpdatePause(self,unattendend,extensionWeeksOfPause):

		if self.lliurexUpCore.isAutoUpgradeEnabled():

			if self.lliurexUpCore.weeksOfPause==0:
				print("  [Lliurex-Up]: Paussing of automatic updates is not configured. Use the pause-automatic-updates option instead")
			else:
				if self.lliurexUpCore.extensionPause==0:
					print("  [Lliurex-Up]: Unable to extend the pause of automatic updates. The configured pause has already reached the limit")
				else:
					if extensionWeeksOfPause > self.lliurexUpCore.extensionPause:
						print("  [Lliurex-Up]: Unable to extend the pause of automatic updates. The indicate extended weeks exceed the limit")
						return 0
					else:
						if not unattendend:
							response=input( '  [Lliurex-Up]: Do you want to extended the pause automatic update in this computer (yes/no)?')
						else:
							response="yes"

						if response.startswith('y'):
							ret=self.lliurexUpCore.manageUpdatePause(True,extensionWeeksOfPause)
							if ret:
								print("  [Lliurex-Up]: Automatic updates have been successfully extended for %s more weeks"%str(extensionWeeksOfPause))
							else:
								print("  [Lliurex-Up]: Unable to pause automatic updates")
								return 1
						
		else:
			print("  [Lliurex-Up]: Automatic updates are already disabled. Nothing to do")

		return 0
	
	#def pauseAutoUpdate

#class LliurexUpCli
