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

		self.lliurexUpCore = lliurex.lliurexup.LliurexUpCore()
		self.defaultMirror = self.lliurexUpCore.defaultMirror
		signal.signal(signal.SIGINT,self.handlerSignal)
		self.lliurexUpCore.checkLocks()
		self.checkingBlock=True
		self.configureRequired=False
	
	
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


	def checkInitialN4dStatus(self):


		self.statusN4d=self.lliurexUpCore.n4dStatus
		
		if not self.statusN4d:
			msgLog="N4d is not working"
			print("  [Lliurex-Up]: %s"%msgLog)
			self.log(msgLog)
	
	def checkInitialFlavour(self):

		self.targetMetapackage=self.lliurexUpCore.checkInitialFlavour()
		msgLog="Initial check metapackage. Metapackage to install: " + str(self.targetMetapackage)
		self.log(msgLog)
		msgLog="Get initial flavours: " + str(self.lliurexUpCore.previousFlavours)
		self.log(msgLog)
		
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

			isClient=self.lliurexUpCore.search_meta("client")
			if not isClient:
				if self.initActionsArg !="initActionsSai":
					return False
				
			print("  [Lliurex-Up]: Unable to connect to lliurex.net")
			return True
				
	#def canConnectToLliurexNet		

	def clientCheckingMirrorExists(self):

		self.allRepos=False

		if self.extraArgs["repositories"]:
			self.allRepos=True
		
		if not self.extraArgs["unattendend_upgrade"]:
			if not self.allRepos:
				print("  [Lliurex-Up]: Checking if mirror exists in server...")
				isMirrorExists=self.lliurexUpCore.clientCheckingMirrorExists()
				msgLog="Checking if mirrror exists in server. MirrorManager response: %s"%isMirrorExists['data']
				self.log(msgLog)
				if isMirrorExists["ismirroravailable"]==None:
					msgLog="Checking if mirror exists in server. Error: "+str(isMirrorExists['exception'])
					self.log(msgLog)
					print("  [Lliurex-Up]: %s"%msgLog)

				else:
					if not isMirrorExists["ismirroravailable"]:
						msgLog="Mirror not detected in server"
						self.log(msgLog)
						response=input('  [Lliurex-Up]: Mirror not detected on the server.Do you want to add the repositories of lliurex.net? (yes/no): ').lower()
						if response.startswith('y'):
							self.allRepos=True
							msgLog="Adding the repositories of lliurex.net on client. Response: Yes"
						else:
							msgLog="Adding the repositories of lliurex.net on client. Response : No"	
						self.log(msgLog)	
					else:
						print("  [Lliurex-Up]: Nothing to do with mirror")

		self.lliurexUpCore.addSourcesListLliurex(self.allRepos)						
	
	#def clientCheckingMirrorExists
				
	def clientCheckingMirrorIsRunning(self):
		
		isMirrorRunningInServer=self.lliurexUpCore.clientCheckingMirrorIsRunning()
		msgLog="Checking if mirrror in server is being updated. MirrorManager response: %s"%isMirrorRunningInServer['data']
		self.log(msgLog)		
		if isMirrorRunningInServer['ismirrorrunning'] ==None:
			msgLog="Checking if mirror in server is being updated. Error: " + str(isMirrorRunningInServer['exception'])
			self.log(msgLog)
		else:
			if isMirrorRunningInServer['ismirrorrunning']:
				msgLog="Mirror is being updated in server. Unable to update the system"
				self.log(msgLog)
		
		return isMirrorRunningInServer['ismirrorrunning']
		
			
	#def clientCheckingMirrorIsRunning		
	
	def initActionsScript(self):

		print("  [Lliurex-Up]: Executing init actions...")
		self.configureRequired=False

		if self.extraArgs["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexUpCore.initActionsScript(self.initActionsArg)
		
		else:
			command=self.lliurexUpCore.initActionsScript(self.initActionsArg)
		
		try:
			
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				output_err=output[1].decode()
			else:
				output_err=output[1]	
			error=self.readErrorOutput(output_err)
			if error:
				if 'dpkg --configure -a' in output_err:
					self.configureRequired=True
				print("  [Lliurex-Up]: Executing init actions. Error: " +'\n'+str(output_err))
				msgLog="Exec Init-Actions. Error: %s"%str(output_err)
			else:
				msgLog="Exec Init-Actions. OK"
			
		except Exception as e:
			msgLog="Exec Init-Actions.Error: " +str(e)
			print("  [Lliurex-Up]: Checking system. Error: " +'\n'+str(e))

			
		self.log(msgLog)	
			
	#def initActionsScript
	
	def checkLliurexUp(self):

		print("  [Lliurex-Up]: Looking for new version of Lliurex Up...")


		isLliurexUpUpdated=self.lliurexUpCore.isLliurexUpIsUpdated(self.allRepos)
		restart=False

		if not isLliurexUpUpdated:
			print("  [Lliurex-Up]: Updating Lliurex-Up...")
			isLliurexUpInstalled=self.lliurexUpCore.installLliurexUp()
			msgLog="Installing Lliurex-Up. Returncode: " + str(isLliurexUpInstalled['returncode']) + ". Error: " + str(isLliurexUpInstalled['stderrs'])
			self.log(msgLog)
			if isLliurexUpInstalled['returncode']==0:
				restart=True
			else:
				isLliurexUpUpdated=self.lliurexUpCore.isLliurexUpIsUpdated(self.allRepos)
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
			msgLog="Checking Lliurex-Up. Is Lliurex-Up updated: "+ str(isLliurexUpUpdated)
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
					msgLog="Updating mirror. Error: " + str(e)
					self.log(msgLog)	
					print("  [Lliurex-Up]: Updating mirror. Error: " +str(e))
											
			else:
				msgLog="Checking mirror. Is mirror update: None"
				self.log(msgLog)
				print("  [Lliurex-Up]: Nothing to do with mirror")
		
		except Exception as e:
			msgLog="Checking mirror. Error: " + str(e)
			self.log(msgLog)	
			print("  [Lliurex-Up]: Checking mirror. Error: " +str(e)) 	
			
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
		msgLog="Get LliurexVersion installed: " + str(self.versionToUpdate["installed"])
		self.log(msgLog)
		msgLog="Get LliurexVersion candidate from local repository: " + str(self.versionToUpdate["candidate"])
		self.log(msgLog)
		msgLog="Get Update source: "+str(self.versionToUpdate["updateSource"])
		self.log(msgLog)

	#def getLliurexVersionLocal	
	

	def getLliurexVersionLliurexNet(self):
	
		print("  [Lliurex-Up]: Looking for LliurexVersion from lliurex.net...")

		self.versionAvailable=self.lliurexUpCore.getLliurexVersionLliurexNet()
		msgLog="Get LliurexVersion candidate from lliurex.net: " + str(self.versionAvailable["candidate"])
		self.log(msgLog)
	
	#def getLliurexVersionLliurexNet		

	def checkingInitialFlavourToInstall(self):

		print("  [Lliurex-Up]: Checking if installation of metapackage is required...")

		self.returnCodeInitFlavour=0
		if len(self.targetMetapackage)==0:
			
			print("  [Lliurex-Up]: Installation of metapackage is not required")
			
		else:
			print("  [Lliurex-Up]: Installation of metapackage is required: " + str(self.targetMetapackage))
			isFlavourInstalled=self.lliurexUpCore.installInitialFlavour(self.targetMetapackage)	
			self.returnCodeInitFlavour=isFlavourInstalled['returncode']
			error=isFlavourInstalled['stderrs']
			msgLog="Install initial metapackage:" + str(self.targetMetapackage) + ": Returncode: " + str(self.returnCodeInitFlavour) + " Error: " + str(error)
			self.log(msgLog)
			print("  [Lliurex-Up]: Metapackage is now installed: Returncode: " + str(self.returnCodeInitFlavour) + " Error: " + str(error))
			
	#def checkingInitialFlavourToInstall		
	
	def getPackagesToUpdate(self):

		print("  [Lliurex-Up]: Looking for new updates...")
		packages=self.lliurexUpCore.getPackagesToUpdate()
		msgLog="Get packages to update. Number of packages: "+ str(len(packages))
		self.log(msgLog)

		self.newPackages=0
		self.packagesList=""
		if (len(packages))>0:
			for item in packages:
				if packages[item]["install"]==None:
						self.newPackages=int(self.newPackages) + 1
				self.packagesList=str(self.packagesList) + item +" "		

		return packages

	#def getPackagesToUpdate		
			
	def checkingIncorrectFlavours(self):
		
		incorrectFlavours=self.lliurexUpCore.checkIncorrectFlavours()
		self.aditionalFlavours=incorrectFlavours["data"]
		msgLog="Checking incorrect metapackages. Others metapackages detected: " + str(incorrectFlavours["status"])+". Detected Flavours: "+str(self.aditionalFlavours)
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
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexUpCore.preActionsScript()
		else:
			command=self.lliurexUpCore.preActionsScript()		
		
		try:
			#os.system(command)
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				output_err=output[1].decode()
			else:
				output_err=output[1]	
			error=self.readErrorOutput(output_err)
			if error:
				print("  [Lliurex-Up]: Preparing system to update. Error: " +'\n'+str(output_err))
				msgLog="Exec Pre-Actions. Error: %s"%str(output_err)
			else:
				msgLog="Exec Pre-Actions. OK"

		except Exception as e:
			print("  [Lliurex-Up]: Preparing system to update. Error: " +'\n'+str(e))
			msgLog="Exec Pre-Actions. Error " +str(e)
			

		self.log(msgLog)	

	#def preActionsScript			

	def distUpgrade(self):

		print("  [Lliurex-Up]: Downloading and installing packages...")

		if self.extraArgs["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexUpCore.distUpgradeProcess()
		else:
			command=self.lliurexUpCore.distUpgradeProcess()

		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				output_err=output[1].decode()
			else:
				output_err=output[1]	
			error=self.readErrorOutput(output_err)
			if error:
				print("  [Lliurex-Up]: Downloading and installing packages. Error: "+ '\n' +str(output_err))
				msgLog="Exec Dist-upgrade. Error: %s"%str(output_err)
			else:
				msgLog="Exec Dist-upgrade. OK"
		
		except Exception as e:
			print("  [Lliurex-Up]: Downloading and installing packages. Error: " + '\n' +str(e))
			msgLog="Exec Dist-uggrade.Error : " +str(e)

		self.log(msgLog)	
			
	#def distUpgrade		

	def postActionsScript(self):

		print("  [Lliurex-Up]: Ending the update...")

		self.postActionError=False

		if self.extraArgs["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexUpCore.postActionsScript() 
		else:
			command=self.lliurexUpCore.postActionsScript()
	
		try:
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			if type(output[1]) is bytes:
				output_err=output[1].decode()
			else:
				output_err=output[1]	
			error=self.readErrorOutput(output_err)
			if error:
				print("  [Lliurex-Up]: Ending the update. Error: " +'\n'+str(output_err))
				self.postActionError=True
				msgLog="Exec Post-Actions. Error: %s"%str(output_err)
			else:
				msgLog="Exec Post-Actions.OK"

			
		except Exception as e:
			self.postActionError=True
			print("  [Lliurex-Up]: Ending the update. Error: " +'\n'+str(e))
			msgLog="Exec Post-Actions.Error:%s"%str(e)

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
					command="DEBIAN_FRONTEND=noninteractive " + self.lliurexUpCore.installFinalFlavour(self.flavourToInstall)
				else:
					command=self.lliurexUpCore.installFinalFlavour(self.flavourToInstall)

				try:

					p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
					output=p.communicate()
					if type(output[1]) is bytes:
						output_err=output[1].decode()
					else:
						output_err=output[1]	
					error=self.readErrorOutput(output_err)
					if error:
						self.finalMetaPackageError=True
						print("  [Lliurex-Up]: Install of metapackage. Error: " +'\n'+str(output_err))
						msgLog="Final install metapackage. Error %s"%str(output_err)
					else:
						msgLog="Final install metapackage.OK"


				except Exception as e:
					self.finalMetaPackageError=True
					print("  [Lliurex-Up]: Install of metapackage. Error: " +'\n'+str(e))
					msgLog="Install of metapackage. Error:%s"%str(e)

				self.log(msgLog)	
					
							
			else:
				print("  [Lliurex-Up]: Metapackage is correct. Nothing to do")

		except Exception as e:	
			self.finalMetaPackageError=True
			print("  [Lliurex-Up]: Checking Metapackage. Error:" +'\n'+str(e))
			msgLog="Final check metapackage. Error:%s"%str(e)	
			self.log(msgLog)	
			
	#def checkingFinalFlavourToInstall		
					
	def checkFinalUpgrade(self):


		print("  [Lliurex-Up]: Checking Dist-upgrade...")
		error=self.lliurexUpCore.checkErrorDistUpgrade()
		errorDetails=str(error[1])

		if error[0] or self.finalMetaPackageError or self.postActionError :
			print("  [Lliurex-Up]: The updated process is endend with errors")
			msgLog="Dist-upgrade process ending with errors. "+errorDetails
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
			origPinningPath="/usr/share/lliurex-up/lliurex-pinning.cfg"
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
		
		freeSpace=(os.statvfs("/").f_bfree * os.statvfs("/").f_bsize) / (1024*1024*1024)

		if (freeSpace) < 2: #less than 2GB available?
			print("  [Lliurex-Up]: There's not enough space on disk to upgrade (2 GB needed)")
			msgLog="There's not enough space on disk to upgrade: "+str(freeSpace)+ " GB available"
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
			print("  [Lliurex-Up]: "+action+" is now running. Wait a moment and try again")
		
		elif code==3:
			msgLog="Apt is running"
			self.log(msgLog)
			print("  [Lliurex-Up]: Apt is now running. Wait a moment and try again")
		
		elif code==2:
			msgLog=action+" is locked"
			self.log(msgLog)
			if not self.extraArgs["unattendend_upgrade"]:
				response=input( '  [Lliurex-Up]: '+action+' seems blocked by a failed previous execution. Lliurex-Up can not continue if this block is maintained.You want to try to unlock it (yes/no)?')
				if response.startswith('y'):
					self.pulsate_unlockingProcess()
				else:
					unlocker=False
			else:
				unlocker=False

		if not unlocker:
			print("  [Lliurex-Up]: "+action+ " seems blocked by a failed previous execution. Unabled to update de sytem")
		
		sys.exit(1)			


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
		p=subprocess.call(cmd,shell=True,stdout=subprocess.PIPE)
		resultQueue.put(p)

	#def unlockingProcess	
		
	
	def main(self,mode,extraArgs=None):

		self.extraArgs=extraArgs
		self.isLliurexUpLocked()
		self.isAptLocked()
		self.isDpkgLocked()
		self.startLliurexUp(mode)
		self.checkInitialFlavour()

		msgLog="Mode of execution: " + str(self.mode)
		self.log(msgLog)
		msgLog="Extra args: " + str(self.extraArgs)
		self.log(msgLog)
			
		if not self.canConnectToLliurexNet():
			print("  [Lliurex-Up]: Unable to connect to lliurex.net")
			self.cleanEnvironment()
			return 1
			
			

		clientCheckingMirror=self.clientCheckingMirrorIsRunning()
		
		if clientCheckingMirror!=False:
			if clientCheckingMirror:
				print("  [Lliurex-Up]: Mirror is being updated in server. Unable to update the system")
			else:
				print("  [Lliurex-Up]: Unable to connect with server")

			self.cleanEnvironment()
			return 1
		else:
			self.clientCheckingMirrorExists()
				
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

		if len(self.packages)>0:
			if not self.checkingIncorrectFlavours():
				print("  [Lliurex-Up]: List of packages to update:\n"+str(self.packagesList))
				print("  [Lliurex-Up]: Number of packages to update:    " +str(len(self.packages)) + " (" + str(self.newPackages) + " news)" )
				print("  [Lliurex-Up]: Current version:                 " +str(self.versionToUpdate["installed"]))
				print("  [Lliurex-Up]: Available version (lliurex.net): " +str(self.versionAvailable["candidate"]))
				print("  [Lliurex-Up]: Candidate version (to install):  " +str(self.versionToUpdate["candidate"]))
				print("  [Lliurex-Up]: Update source:                   " +str(self.versionToUpdate["updateSource"]))
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
				print("[Lliurex-Up]: Updated abort for incorrect flavours detected in new update. Detected flavours: "+str(self.aditionalFlavours))
				msgLog="Updated abort for incorrect flavours detected in new update"
				self.log(msgLog)
				self.cleanEnvironment()

				return 1			
		else:
			if not self.checkPreviousUpgrade():
				print("  [Lliurex-Up]: Current version:                 " +str(self.versionToUpdate["installed"]))
				print("  [Lliurex-Up]: Available version (lliurex.net): " +str(self.versionAvailable["candidate"]))
				print("  [Lliurex-Up]: Candidate version (to install):  " +str(self.versionToUpdate["candidate"]))
				print("  [Lliurex-Up]: Update source:                   " +str(self.versionToUpdate["updateSource"]))
				print("  [Lliurex-Up]: Your system is updated. Nothing to do")
				msgLog="System updated. Nothing to do"
				self.log(msgLog)
				self.cleanEnvironment()

				return 0
			else:
				print("  [Lliurex-Up]: Updated abort. An error occurred checking new updates")
				msgLog=" Updated abort. An error occurred checking new updates"
				self.log(msgLog)
				self.cleanEnvironment()

				return 1
	#def main			
#class LliurexUpCli
