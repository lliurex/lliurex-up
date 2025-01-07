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
from gi.repository import GLib
signal.signal(signal.SIGINT,signal.SIG_IGN)

class LliurexUpCli(object):
	def __init__(self):

		self.lliurexcore = lliurex.lliurexup.LliurexUpCore()
		self.defaultMirror = self.lliurexcore.defaultMirror
		signal.signal(signal.SIGINT,self.handlerSignal)
		self.lliurexcore.checkLocks()
		self.checkingBlock=True
		self.configureRequired=False
	
	#def __init__
	
	def startLliurexUp(self,mode):

		self.checkingBlock=False
		self.lliurexcore.startLliurexUp()

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

		self.statusN4d=self.lliurexcore.n4dStatus
		
		if not self.statusN4d:
			logMsg="N4d is not working"
			print("  [Lliurex-Up]: %s"%logMsg)
			self.log(logMsg)

	#def checkInitialN4dStatus

	def checkInitialFlavour(self,extra_args=None):

		self.targetMetapackage=self.lliurexcore.checkInitialFlavour()
		logMsg="Initial check metapackage. Metapackage to install: " + str(self.targetMetapackage)
		self.log(logMsg)
		logMsg="Get initial flavours: " + str(self.lliurexcore.previousFlavours)
		self.log(logMsg)
		
	#def checkInitialFlavour	
		
	def canConnectToLliurexNet(self):

		print("  [Lliurex-Up]: Checking connection to lliurex.net...")

		canConnect=self.lliurexcore.canConnectToLliurexNet()
		logMsg="Checking connection to lliurex.net: %s"%canConnect
		self.log(logMsg)
		if canConnect['status']:
			logMsg="Can connect to lliurex.net: True"
			self.log(logMsg)
			return True
		else:
			logMsg="Can connect to lliurex.net: False"
			self.log(logMsg)
			print("  [Lliurex-Up]: Unable to connect to lliurex.net")
			return False
				
	#def canConnectToLliurexNet		

	def clientCheckingMirrorExists(self,extra_args=None):

		self.allRepos=False

		if extra_args["repositories"]:
			self.allRepos=True
		
		if not extra_args["unattendend_upgrade"]:
			if not self.allRepos:
				print("  [Lliurex-Up]: Checking if mirror exists in ADI...")
				isMirrorExists=self.lliurexcore.clientCheckingMirrorExists()
				logMsg="Checking if mirrror exists in ADI. MirrorManager response: %s"%isMirrorExists['data']
				self.log(logMsg)
				if isMirrorExists["ismirroravailable"]==None:
					logMsg="Checking if mirror exists in ADI. Error: "+str(isMirrorExists['exception'])
					self.log(logMsg)
					print("  [Lliurex-Up]: %s"%logMsg)

				else:
					if not isMirrorExists["ismirroravailable"]:
						logMsg="Mirror not detected in ADI"
						self.log(logMsg)
					else:
						print("  [Lliurex-Up]: Nothing to do with mirror")

		self.lliurexcore.addSourcesListLliurex(self.allRepos)						
	
	#def clientCheckingMirrorExists
				
	def clientCheckingMirrorIsRunning(self):
		
		isMirrorRunningInADI=self.lliurexcore.clientCheckingMirrorIsRunning()
		logMsg="Checking if mirrror in ADI is being updated. MirrorManager response: %s"%isMirrorRunningInServer['data']
		self.log(logMsg)		
		if isMirrorRunningInADI['ismirrorrunning'] ==None:
			logMsg="Checking if mirror in ADI is being updated. Error: " + str(isMirrorRunningInServer['exception'])
			self.log(logMsg)
		else:
			if isMirrorRunningInADI['ismirrorrunning']:
				logMsg="Mirror is being updated in ADI. Unable to update the system"
				self.log(logMsg)
		
		return isMirrorRunningInADI['ismirrorrunning']
		
	#def clientCheckingMirrorIsRunning		
	
	def initActionsScript(self,extra_args=None):

		print("  [Lliurex-Up]: Executing init actions...")
		self.configureRequired=False

		if extra_args["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexcore.initActionsScript(self.initActionsArg)
		
		else:
			command=self.lliurexcore.initActionsScript(self.initActionsArg)
		
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
				print("  [Lliurex-Up]: Executing init actions. Error: " +'\n'+str(outputErr))
				logMsg="Exec Init-Actions. Error: %s"%str(outputErr)
			else:
				logMsg="Exec Init-Actions. OK"
			
		except Exception as e:
			logMsg="Exec Init-Actions.Error: " +str(e)
			print("  [Lliurex-Up]: Checking system. Error: " +'\n'+str(e))

		self.log(logMsg)	
			
	#def initActionsScript
	
	def checkLliurexUp(self):

		print("  [Lliurex-Up]: Looking for new version of Lliurex Up...")

		isLliureXUpUpdated=self.lliurexcore.isLliurexUpIsUpdated(self.allRepos)
		restart=False

		if not isLliureXUpUpdated:
			print("  [Lliurex-Up]: Updating Lliurex-Up...")
			isLliureXUpInstalled=self.lliurexcore.installLliurexUp()
			logMsg="Installing Lliurex-Up. Returncode: " + str(isLliureXUpInstalled['returncode']) + ". Error: " + str(isLliureXUpInstalled['stderrs'])
			self.log(logMsg)
			if isLliureXUpInstalled['returncode']==0:
				restart=True
			else:
				isLliureXUpUpdated=self.lliurexcore.isLliurexUpIsUpdated(self.allRepos)
				if not isLliureXUpUpdated:
					logMsg="Unable to update Lliurex-Up"
					self.log(logMsg)
					print("  [Lliurex-Up]: Unable to update Lliurex-Up. Error: %s"%str(isLliureXUpInstalled['stderrs']))
					restart=False
				else:
					restart=True

			if restart:
				print("  [Lliurex-Up]: Lliurex-Up is now update and will be reboot now..." )
				time.sleep(3)
				self.lliurexcore.cleanLliurexUpLock()
				os.execv("/usr/sbin/lliurex-upgrade",sys.argv)
			else:
				return False

		else:
			logMsg="Checking Lliurex-Up. Is Lliurex-Up updated: "+ str(isLliureXUpUpdated)
			self.log(logMsg)
			print("  [Lliurex-Up]: Lliurex-Up is updated.Nothing to do")
			return True	
			
	#def checkLliurexUp		

	def checkMirror(self,extra_args=None):

		print("  [Lliurex-Up]: Checking if mirror is updated...")

		try:
			isMirrorUpdated=self.lliurexcore.lliurexMirrorIsUpdated()

			if isMirrorUpdated !=None:
				logMsg="Checking mirror. MirrorManager response: %s"%isMirrorUpdated['data']
				self.log(logMsg)
				try:
					isMirrorRunning=self.lliurexcore.lliurexMirrorIsRunning()
					if isMirrorRunning:
						print("  [Lliurex-Up]: Updating mirror. Wait a moment please...")
						self.updateMirrorProgress()
					else:
						if isMirrorUpdated['action']=='update':
							if not isMirrorRunning:
								logMsg="Checking mirror. Is mirror update: False"
								self.log(logMsg)
								if not extra_args["unattended_mirror"]:
									response=input('  [Lliurex-Up]: Do you want update mirror (yes/no): ').lower()
								else:
									response="yes"

								if response.startswith('y'):
									logMsg="Update lliurex-mirror. Response: Yes"
									self.log(logMsg)
									print("  [Lliurex-Up]: Updating mirror. Wait a moment please...")
									command='lliurex-mirror update %s'%self.defaultMirror
									subprocess.Popen(command,shell=True).communicate()

								else:
									logMsg="Update lliurex-mirror. Response: No"
									self.log(logMsg)
									print("  [Lliurex-Up]: Mirror update. Not update")	
						else:
							logMsg="Checking mirror. Is mirror update: nothing-to-do"
							self.log(logMsg)
							print("  [Lliurex-Up]: %s"%logMsg)
				
				except Exception as e:
					logMsg="Updating mirror. Error: " + str(e)
					self.log(logMsg)	
					print("  [Lliurex-Up]: Updating mirror. Error: " +str(e))
											
			else:
				logMsg="Checking mirror. Is mirror update: None"
				self.log(logMsg)
				print("  [Lliurex-Up]: Nothing to do with mirror")
		
		except Exception as e:
			logMsg="Checking mirror. Error: " + str(e)
			self.log(logMsg)	
			print("  [Lliurex-Up]: Checking mirror. Error: " +str(e)) 	
			
	#def checkMirror		

	def updateMirrorProgress(self):

		isMirrorRunning=self.lliurexcore.lliurexMirrorIsRunning()
		counter = 0
		percentage = 0
		clockpercentage = 0
		clock = ['—','/','|','\\']

		while isMirrorRunning:
			if  counter ==  0:
				percentage=self.lliurexcore.getPercentageLliurexMirror()
				
				if percentage!=None:
					isMirrorRunning=self.lliurexcore.lliurexMirrorIsRunning()
					
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
		
		self.versionUpdate=self.lliurexcore.getLliurexVersionLocal()
		logMsg="Get LliurexVersion installed: " + str(self.versionUpdate["installed"])
		self.log(logMsg)
		logMsg="Get LliurexVersion candidate from local repository: " + str(self.versionUpdate["candidate"])
		self.log(logMsg)
		logMsg="Get Update source: "+str(self.versionUpdate["updateSource"])
		self.log(logMsg)

	#def getLliurexVersionLocal	
	
	def getLliurexVersionLliurexNet(self):
	
		print("  [Lliurex-Up]: Looking for LliurexVersion from lliurex.net...")

		self.versionAvailable=self.lliurexcore.getLliurexVersionLliurexNet()
		logMsg="Get LliurexVersion candidate from lliurex.net: " + str(self.versionAvailable["candidate"])
		self.log(logMsg)
	
	#def getLliurexVersionLliurexNet		

	def checkingInitialFlavourToInstall(self):

		print("  [Lliurex-Up]: Checking if installation of metapackage is required...")

		self.returnCodeInitFlavour=0
		if len(self.targetMetapackage)==0:
			
			print("  [Lliurex-Up]: Installation of metapackage is not required")
			
		else:
			print("  [Lliurex-Up]: Installation of metapackage is required: " + str(self.targetMetapackage))
			isFlavourInstalled=self.lliurexcore.installInitialFlavour(self.targetMetapackage)	
			self.returnCodeInitFlavour=isFlavourInstalled['returncode']
			error=isFlavourInstalled['stderrs']
			logMsg="Install initial metapackage:" + str(self.targetMetapackage) + ": Returncode: " + str(self.returnCodeInitFlavour) + " Error: " + str(error)
			self.log(logMsg)
			print("  [Lliurex-Up]: Metapackage is now installed: Returncode: " + str(self.returnCodeInitFlavour) + " Error: " + str(error))
			
	#def checkingInitialFlavourToInstall		
	
	def getPackagesToUpdate(self):

		print("  [Lliurex-Up]: Looking for new updates...")
		packages=self.lliurexcore.getPackagesToUpdate()
		logMsg="Get packages to update. Number of packages: "+ str(len(packages))
		self.log(logMsg)

		self.newPackages=0
		self.listPackages=""
		if (len(packages))>0:
			for item in packages:
				if packages[item]["install"]==None:
						self.newPackages=int(self.newPackages) + 1
				self.listPackages=str(self.listPackages) + item +" "		

		return packages

	#def getPackagesToUpdate		
			
	def checkingIncorrectFlavours(self):
		
		incorrectFlavours=self.lliurexcore.checkIncorrectFlavours()
		self.aditionalFlavours=incorrectFlavours["data"]
		logMsg="Checking incorrect metapackages. Others metapackages detected: " + str(incorrectFlavours["status"])+". Detected Flavours: "+str(self.aditionalFlavours)
		self.log(logMsg)

		return incorrectFlavours['status']
	
	#def checkingIncorrectFlavours		
		
	def checkPreviousUpgrade(self):
		
		error=False
		if self.returnCodeInitFlavour!=0:
			error=True

		else:
			if self.versionUpdate["candidate"]!=None:
				if self.versionUpdate["installed"]!=self.versionUpdate["candidate"]:
					error=True
			else:
				if self.versionUpdate["installed"]!=self.versionAvailable["candidate"]:	
					error=True

		return error

	#def checkPreviousUpgrade		

	def preActionsScript(self,extra_args):

		print("  [Lliurex-Up]: Preparing system to update...")

		if extra_args["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexcore.preActionsScript()
		else:
			command=self.lliurexcore.preActionsScript()		
		
		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				outputErr=output[1].decode()
			else:
				outputErr=output[1]	
			error=self.readErrorOutput(outputErr)
			if error:
				print("  [Lliurex-Up]: Preparing system to update. Error: " +'\n'+str(outputErr))
				logMsg="Exec Pre-Actions. Error: %s"%str(outputErr)
			else:
				logMsg="Exec Pre-Actions. OK"

		except Exception as e:
			print("  [Lliurex-Up]: Preparing system to update. Error: " +'\n'+str(e))
			logMsg="Exec Pre-Actions. Error " +str(e)
			
		self.log(logMsg)	

	#def preActionsScript			

	def distUpgrade(self,extra_args):

		print("  [Lliurex-Up]: Downloading and installing packages...")

		if extra_args["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexcore.distUpgradeProcess()
		else:
			command=self.lliurexcore.distUpgradeProcess()

		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				outputErr=output[1].decode()
			else:
				outputErr=output[1]	
			error=self.readErrorOutput(outputErr)
			if error:
				print("  [Lliurex-Up]: Downloading and installing packages. Error: "+ '\n' +str(outputErr))
				logMsg="Exec Dist-upgrade. Error: %s"%str(outputErr)
			else:
				logMsg="Exec Dist-upgrade. OK"
		
		except Exception as e:
			print("  [Lliurex-Up]: Downloading and installing packages. Error: " + '\n' +str(e))
			logMsg="Exec Dist-uggrade.Error : " +str(e)

		self.log(logMsg)	
			
	#def distUpgrade		

	def postActionsScript(self,extra_args):

		print("  [Lliurex-Up]: Ending the update...")

		self.errorPostAction=False

		if extra_args["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexcore.postActionsScript() 
		else:
			command=self.lliurexcore.postActionsScript()
	
		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				outputErr=output[1].decode()
			else:
				outputErr=output[1]	
			error=self.readErrorOutput(outputErr)
			if error:
				print("  [Lliurex-Up]: Ending the update. Error: " +'\n'+str(outputErr))
				self.errorPostAction=True
				logMsg="Exec Post-Actions. Error: %s"%str(outputErr)
			else:
				logMsg="Exec Post-Actions.OK"

			
		except Exception as e:
			self.errorPostAction=True
			print("  [Lliurex-Up]: Ending the update. Error: " +'\n'+str(e))
			logMsg="Exec Post-Actions.Error:%s"%str(e)

		self.log(logMsg)	

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

		self.lliurexcore.checkN4dStatus()
		
		if not self.lliurexcore.n4dStatus:
			logMsg="N4d is not working"
			self.log(logMsg)

	#def checkFinalN4dStatus		

	def checkingFinalFlavourToInstall(self):
		
		print("  [Lliurex-Up]: Checking final metapackage...")
		self.errorFinalMetaPackage=False
		self.checkFinalN4dStatus()

		try:
			self.flavourToInstall=self.lliurexcore.checkFlavour(True)

			logMsg="Final check metapackage. Metapackage to install:%s"%str(self.flavourToInstall)
			self.log(logMsg)
							
			if len(self.flavourToInstall)>0:
				print("  [Lliurex-Up]: Install of metapackage is required:%s"%str(self.flavourToInstall))
			
				if extra_args["unattendend_upgrade"]:
					command="DEBIAN_FRONTEND=noninteractive " + self.lliurexcore.installFinalFlavour(self.flavourToInstall)
				else:
					command=self.lliurexcore.installFinalFlavour(self.flavourToInstall)

				try:

					p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
					output=p.communicate()
					if type(output[1]) is bytes:
						outputErr=output[1].decode()
					else:
						outputErr=output[1]	
					error=self.readErrorOutput(outputErr)
					if error:
						self.errorFinalMetaPackage=True
						print("  [Lliurex-Up]: Install of metapackage. Error: " +'\n'+str(outputErr))
						logMsg="Final install metapackage. Error %s"%str(outputErr)
					else:
						logMsg="Final install metapackage.OK"

				except Exception as e:
					self.errorFinalMetaPackage=True
					print("  [Lliurex-Up]: Install of metapackage. Error: " +'\n'+str(e))
					logMsg="Install of metapackage. Error:%s"%str(e)

				self.log(logMsg)	
					
			else:
				print("  [Lliurex-Up]: Metapackage is correct. Nothing to do")

		except Exception as e:	
			self.errorFinalMetaPackage=True
			print("  [Lliurex-Up]: Checking Metapackage. Error:" +'\n'+str(e))
			logMsg="Final check metapackage. Error:%s"%str(e)	
			self.log(logMsg)	
			
	#def checkingFinalFlavourToInstall		
					
	def checkFinalUpgrade(self):

		print("  [Lliurex-Up]: Checking Dist-upgrade...")
		error=self.lliurexcore.checkErrorDistUpgrade()
		errorDetails=str(error[1])

		if error[0] or self.errorFinalMetaPackage or self.errorPostAction :
			print("  [Lliurex-Up]: The updated process is endend with errors")
			logMsg="Dist-upgrade process ending with errors. "+errorDetails
			self.distUpgrade_OK=False
		
		else:					
			print("  [Lliurex-Up]: The system is now update")	
			logMsg="Dist-upgrade process ending OK"
			self.distUpgrade_OK=True

		self.log(logMsg)
		
	#def checkFinalUpgrade	

	def cleanEnvironment(self):

		self.lliurexcore.cleanEnvironment()
		self.lliurexcore.cleanLliurexUpLock()

		if self.initActionsArg =="initActionsSai":
			origPinningPath="/usr/share/lliurex-up/lliurex-pinning.cfg"
			destPinningPath="/etc/apt/preferences.d/lliurex-pinning"
			shutil.copy(origPinningPath,destPinningPath)

		return

	#def cleanEnvironment		

	def handlerSignal(self,signal,frame):
		
		print("\n  [Lliurex-Up]: Cancel process with Ctrl+C signal")
		logMsg="Cancel process with Ctrl+C signal"
		self.log(logMsg)
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
		
		freeSpace=(os.statvfs("/").f_bfree * os.statvfs("/").f_bsize) / (1024*1024*1024)

		if (freeSpace) < 2: #less than 2GB available?
			print("  [Lliurex-Up]: There's not enough space on disk to upgrade (2 GB needed)")
			logMsg="There's not enough space on disk to upgrade: "+str(freeSpace)+ " GB available"
			self.log(logMsg)
			self.cleanEnvironment()
			sys.exit(1)

	#def freeSpaceCheck		

	def isLliurexUpLocked(self,extra_args):

		print("  [Lliurex-Up]: Checking if LliureX-Up is running...")

		code=self.lliurexcore.isLliurexUpLocked()
		logMsg="------------------------------------------\n"+"LLIUREX-UP-CLI STARTING AT: " + datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") +"\n------------------------------------------"

		
		if code !=0:
			if code!=1:
				self.log(logMsg)
			self.manageLocker(code,"Lliurex-Up")	
		else:
			self.log(logMsg)
							
		
	#def islliurexup_running	

	def isAptLocked(self,extra_args):

		print("  [Lliurex-Up]: Checking if Apt is running...")

		code=self.lliurexcore.isAptLocked()
		
		if code !=0:
			self.manageLocker(code,"Apt")	

	#def isAptLocked		

	def isDpkgLocked(self,extra_args):

		print("  [Lliurex-Up]: Checking if Dpkg is running...")

		code=self.lliurexcore.isDpkgLocked()

		if code !=0:
			self.manageLocker(code,"Dpkg")	
	
	#def isDpkgLocked

	def manageLocker(self,code,action):

		unlocker=True
		if code==1:
			if action!="Lliurex-Up":
				logMsg=action+" is running"
				self.log(logMsg)
			print("  [Lliurex-Up]: "+action+" is now running. Wait a moment and try again")
		
		elif code==3:
			logMsg="Apt is running"
			self.log(logMsg)
			print("  [Lliurex-Up]: Apt is now running. Wait a moment and try again")
		
		elif code==2:
			logMsg=action+" is locked"
			self.log(logMsg)
			if not extra_args["unattendend_upgrade"]:
				response=input( '  [Lliurex-Up]: '+action+' seems blocked by a failed previous execution. Lliurex-Up can not continue if this block is maintained.You want to try to unlock it (yes/no)?')
				if response.startswith('y'):
					self.pulsateUnlockingProcess()
				else:
					unlocker=False
			else:
				unlocker=False

		if not unlocker:
			print("  [Lliurex-Up]: "+action+ " seems blocked by a failed previous execution. Unabled to update de sytem")
		
		sys.exit(1)			

	def pulsateUnlockingProcess(self):

		self.endProcess=False
		
		result_queue=multiprocessing.Queue()
		self.unlocking_t=multiprocessing.Process(target=self.unlockingProcess,args=(result_queue,))
		self.unlocking_t.start()
		
		progressbar= ["[    ]","[=   ]","[==  ]","[=== ]","[====]","[ ===]","[  ==]","[   =]","[    ]","[   =]","[  ==]","[ ===]","[====]","[=== ]","[==  ]","[=   ]"]
		i=1
		while self.unlocking_t.is_alive():
			time.sleep(0.5)
			per=i%16
			print("  [Lliurex-Up]: The unlocking process is running. Wait a moment " + progressbar[per],end='\r')

			i+=1

		result=result_queue.get()
		
		if result ==0:
			sys.stdout.flush()
			logMsg="The unlocking process finished successfully"
			self.log(logMsg)
			os.execv("/usr/sbin/lliurex-upgrade",sys.argv)
		else:
			if result==1:
				print("  [Lliurex-Up]: The unlocking process has failed")
				logMsg="The unlocking process has failed"
			else:
				print("  [Lliurex-Up]: Some process are running. Wait a moment and try again")
				logMsg="Some process are running. Wait a moment and try again"
	
			self.log(logMsg)
			sys.exit(1)

	#def pulsateUnlockingProcess

	def unlockingProcess(self,result_queue):

		cmd=self.lliurexcore.unlockerCommand()
		p=subprocess.call(cmd,shell=True,stdout=subprocess.PIPE)
		result_queue.put(p)

	#def unlockingProcess	
		
	def main(self,mode,extra_args=None):

		self.isLliurexUpLocked(extra_args)
		self.isAptLocked(extra_args)
		self.isDpkgLocked(extra_args)
		self.startLliurexUp(mode)
		self.checkInitialFlavour()

		logMsg="Mode of execution: " + str(self.mode)
		self.log(logMsg)
		logMsg="Extra args: " + str(extra_args)
		self.log(logMsg)
			
		if not self.canConnectToLliurexNet():
			print("  [Lliurex-Up]: Unable to connect to lliurex.net")
			self.cleanEnvironment()
			return 1
			
		clientCheckingMirror=self.clientCheckingMirrorIsRunning()
		
		if clientCheckingMirror!=False:
			if clientCheckingMirror:
				print("  [Lliurex-Up]: Mirror is being updated in ADI. Unable to update the system")
			else:
				print("  [Lliurex-Up]: Unable to connect with ADI")

			self.cleanEnvironment()
			return 1
		else:
			self.clientCheckingMirrorExists(extra_args)
				
		self.initActionsScript(extra_args)
		if not self.checkLliurexUp():
			self.cleanEnvironment()
			return 1

		if extra_args["mirror"]:
			self.checkMirror(extra_args)

		self.getLliurexVersionLocal()
		self.getLliurexVersionLliurexNet()
		self.checkingInitialFlavourToInstall()
		self.packages=self.getPackagesToUpdate()

		if len(self.packages)>0:
			if not self.checkingIncorrectFlavours():
				print("  [Lliurex-Up]: List of packages to update:\n"+str(self.listPackages))
				print("  [Lliurex-Up]: Number of packages to update:    " +str(len(self.packages)) + " (" + str(self.newPackages) + " news)" )
				print("  [Lliurex-Up]: Current version:                 " +str(self.versionUpdate["installed"]))
				print("  [Lliurex-Up]: Available version (lliurex.net): " +str(self.versionAvailable["candidate"]))
				print("  [Lliurex-Up]: Candidate version (to install):  " +str(self.versionUpdate["candidate"]))
				print("  [Lliurex-Up]: Update source:                   " +str(self.versionUpdate["updateSource"]))
				if self.configureRequired:
					print("  [Lliurex-Up]: dpkg --configure -a must be executed. You can use dpkg-unlocker for this")
				if not extra_args["unattendend_upgrade"]:
					response=input('  [Lliurex-Up]: Do you want to update the system (yes/no)): ').lower()
				else:
					response="yes"

				if response.startswith('y'):
					self.lliurexcore.stopAutoUpgrade()
					self.preActionsScript(extra_args)
					self.distUpgrade(extra_args)
					self.postActionsScript(extra_args)
					time.sleep(5)
					self.checkingFinalFlavourToInstall()	
					self.checkFinalUpgrade()
					self.cleanEnvironment()
					if self.distUpgrade_OK:
						return 0
					else:
						return 1
				else:
					logMsg="Cancel the update"
					self.log(logMsg)
					print("  [Lliurex-Up]: Cancel the update")
					self.cleanEnvironment()

					return 0
			else:
				print("[Lliurex-Up]: Updated abort for incorrect flavours detected in new update. Detected flavours: "+str(self.aditionalFlavours))
				logMsg="Updated abort for incorrect flavours detected in new update"
				self.log(logMsg)
				self.cleanEnvironment()

				return 1			
		else:
			if not self.checkPreviousUpgrade():
				print("  [Lliurex-Up]: Current version:                 " +str(self.versionUpdate["installed"]))
				print("  [Lliurex-Up]: Available version (lliurex.net): " +str(self.versionAvailable["candidate"]))
				print("  [Lliurex-Up]: Candidate version (to install):  " +str(self.versionUpdate["candidate"]))
				print("  [Lliurex-Up]: Update source:                   " +str(self.versionUpdate["updateSource"]))
				print("  [Lliurex-Up]: Your system is updated. Nothing to do")
				logMsg="System updated. Nothing to do"
				self.log(logMsg)
				self.cleanEnvironment()

				return 0
			else:
				print("  [Lliurex-Up]: Updated abort. An error occurred checking new updates")
				logMsg=" Updated abort. An error occurred checking new updates"
				self.log(logMsg)
				self.cleanEnvironment()

				return 1

	#def main

#class LliurexUpCli