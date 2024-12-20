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
		signal.signal(signal.SIGINT,self.handler_signal)
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
		self.free_space_check()
		self.checkInitialN4dStatus()


	def checkInitialN4dStatus(self):


		self.statusN4d=self.lliurexcore.n4dStatus
		
		if not self.statusN4d:
			log_msg="N4d is not working"
			print("  [Lliurex-Up]: %s"%log_msg)
			self.log(log_msg)
			'''
			self.cleanEnvironment()
			sys.exit(1)
			'''

	def checkInitialFlavour(self,extra_args=None):

		self.targetMetapackage=self.lliurexcore.checkInitialFlavour()
		log_msg="Initial check metapackage. Metapackage to install: " + str(self.targetMetapackage)
		self.log(log_msg)
		log_msg="Get initial flavours: " + str(self.lliurexcore.previousFlavours)
		self.log(log_msg)
		
	#def checkInitialFlavour	
		

	def canConnectToLliurexNet(self):

		print("  [Lliurex-Up]: Checking connection to lliurex.net...")

		can_connect=self.lliurexcore.canConnectToLliurexNet()
		log_msg="Checking connection to lliurex.net: %s"%can_connect
		self.log(log_msg)
		if can_connect['status']:
				log_msg="Can connect to lliurex.net: True"
				self.log(log_msg)
				return True
		else:
			log_msg="Can connect to lliurex.net: False"
			self.log(log_msg)

			is_client=self.lliurexcore.search_meta("client")
			if not is_client:
				if self.initActionsArg !="initActionsSai":
					return False
				
			print("  [Lliurex-Up]: Unable to connect to lliurex.net")
			return True
				
	#def canConnectToLliurexNet		

	def clientCheckingMirrorExists(self,extra_args=None):

		self.allRepos=False

		if extra_args["repositories"]:
			self.allRepos=True
		
		if not extra_args["unattendend_upgrade"]:
			if not self.allRepos:
				print("  [Lliurex-Up]: Checking if mirror exists in server...")
				is_mirror_exists=self.lliurexcore.clientCheckingMirrorExists()
				log_msg="Checking if mirrror exists in server. MirrorManager response: %s"%is_mirror_exists['data']
				self.log(log_msg)
				if is_mirror_exists["ismirroravailable"]==None:
					log_msg="Checking if mirror exists in server. Error: "+str(is_mirror_exists['exception'])
					self.log(log_msg)
					print("  [Lliurex-Up]: %s"%log_msg)

				else:
					if not is_mirror_exists["ismirroravailable"]:
						log_msg="Mirror not detected in server"
						self.log(log_msg)
						response=input('  [Lliurex-Up]: Mirror not detected on the server.Do you want to add the repositories of lliurex.net? (yes/no): ').lower()
						if response.startswith('y'):
							self.allRepos=True
							log_msg="Adding the repositories of lliurex.net on client. Response: Yes"
						else:
							log_msg="Adding the repositories of lliurex.net on client. Response : No"	
						self.log(log_msg)	
					else:
						print("  [Lliurex-Up]: Nothing to do with mirror")

		self.lliurexcore.addSourcesListLliurex(self.allRepos)						
	
	#def clientCheckingMirrorExists
				
	def clientCheckingMirrorIsRunning(self):
		
		is_mirror_running_inserver=self.lliurexcore.clientCheckingMirrorIsRunning()
		log_msg="Checking if mirrror in server is being updated. MirrorManager response: %s"%is_mirror_running_inserver['data']
		self.log(log_msg)		
		if is_mirror_running_inserver['ismirrorrunning'] ==None:
			log_msg="Checking if mirror in server is being updated. Error: " + str(is_mirror_running_inserver['exception'])
			self.log(log_msg)
		else:
			if is_mirror_running_inserver['ismirrorrunning']:
				log_msg="Mirror is being updated in server. Unable to update the system"
				self.log(log_msg)
		
		return is_mirror_running_inserver['ismirrorrunning']
		
			
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
				output_err=output[1].decode()
			else:
				output_err=output[1]	
			error=self.readErrorOutput(output_err)
			if error:
				if 'dpkg --configure -a' in output_err:
					self.configureRequired=True
				print("  [Lliurex-Up]: Executing init actions. Error: " +'\n'+str(output_err))
				log_msg="Exec Init-Actions. Error: %s"%str(output_err)
			else:
				log_msg="Exec Init-Actions. OK"
			
		except Exception as e:
			log_msg="Exec Init-Actions.Error: " +str(e)
			print("  [Lliurex-Up]: Checking system. Error: " +'\n'+str(e))

			
		self.log(log_msg)	
			
	#def initActionsScript
	
	def checkLliurexUp(self):

		print("  [Lliurex-Up]: Looking for new version of Lliurex Up...")


		is_lliurexup_updated=self.lliurexcore.isLliurexUpIsUpdated(self.allRepos)
		restart=False

		if not is_lliurexup_updated:
			print("  [Lliurex-Up]: Updating Lliurex-Up...")
			is_lliurexup_installed=self.lliurexcore.installLliurexUp()
			log_msg="Installing Lliurex-Up. Returncode: " + str(is_lliurexup_installed['returncode']) + ". Error: " + str(is_lliurexup_installed['stderrs'])
			self.log(log_msg)
			if is_lliurexup_installed['returncode']==0:
				restart=True
			else:
				is_lliurexup_updated=self.lliurexcore.isLliurexUpIsUpdated(self.allRepos)
				if not is_lliurexup_updated:
					log_msg="Unable to update Lliurex-Up"
					self.log(log_msg)
					print("  [Lliurex-Up]: Unable to update Lliurex-Up. Error: %s"%str(is_lliurexup_installed['stderrs']))
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
			log_msg="Checking Lliurex-Up. Is Lliurex-Up updated: "+ str(is_lliurexup_updated)
			self.log(log_msg)
			print("  [Lliurex-Up]: Lliurex-Up is updated.Nothing to do")
			return True	
			
	#def checkLliurexUp		

	def checkMirror(self,extra_args=None):

		print("  [Lliurex-Up]: Checking if mirror is updated...")

		try:
			is_mirror_updated=self.lliurexcore.lliurexMirrorIsUpdated()

			if is_mirror_updated !=None:
				log_msg="Checking mirror. MirrorManager response: %s"%is_mirror_updated['data']
				self.log(log_msg)
				try:
					is_mirror_running=self.lliurexcore.lliurexMirrorIsRunning()
					if is_mirror_running:
						print("  [Lliurex-Up]: Updating mirror. Wait a moment please...")
						self.updateMirrorProgress()
					else:
						if is_mirror_updated['action']=='update':
							if not is_mirror_running:
								log_msg="Checking mirror. Is mirror update: False"
								self.log(log_msg)
								if not extra_args["unattended_mirror"]:
									response=input('  [Lliurex-Up]: Do you want update mirror (yes/no): ').lower()
								else:
									response="yes"

								if response.startswith('y'):
									log_msg="Update lliurex-mirror. Response: Yes"
									self.log(log_msg)
									print("  [Lliurex-Up]: Updating mirror. Wait a moment please...")
									command='lliurex-mirror update %s'%self.defaultMirror
									subprocess.Popen(command,shell=True).communicate()

								else:
									log_msg="Update lliurex-mirror. Response: No"
									self.log(log_msg)
									print("  [Lliurex-Up]: Mirror update. Not update")	
						else:
							log_msg="Checking mirror. Is mirror update: nothing-to-do"
							self.log(log_msg)
							print("  [Lliurex-Up]: %s"%log_msg)
				
				except Exception as e:
					log_msg="Updating mirror. Error: " + str(e)
					self.log(log_msg)	
					print("  [Lliurex-Up]: Updating mirror. Error: " +str(e))
											
			else:
				log_msg="Checking mirror. Is mirror update: None"
				self.log(log_msg)
				print("  [Lliurex-Up]: Nothing to do with mirror")
		
		except Exception as e:
			log_msg="Checking mirror. Error: " + str(e)
			self.log(log_msg)	
			print("  [Lliurex-Up]: Checking mirror. Error: " +str(e)) 	
			
	#def checkMirror		

	def updateMirrorProgress(self):

		is_mirror_running=self.lliurexcore.lliurexMirrorIsRunning()
		counter = 0
		percentage = 0
		clockpercentage = 0
		clock = ['—','/','|','\\']

		while is_mirror_running:
			if  counter ==  0:
				percentage=self.lliurexcore.getPercentageLliurexMirror()
				
				if percentage!=None:
					is_mirror_running=self.lliurexcore.lliurexMirrorIsRunning()
					
				else:
					is_mirror_running=False	

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
		
		self.version_update=self.lliurexcore.getLliurexVersionLocal()
		log_msg="Get LliurexVersion installed: " + str(self.version_update["installed"])
		self.log(log_msg)
		log_msg="Get LliurexVersion candidate from local repository: " + str(self.version_update["candidate"])
		self.log(log_msg)
		log_msg="Get Update source: "+str(self.version_update["updateSource"])
		self.log(log_msg)

	#def getLliurexVersionLocal	
	

	def getLliurexVersionLliurexNet(self):
	
		print("  [Lliurex-Up]: Looking for LliurexVersion from lliurex.net...")

		self.version_available=self.lliurexcore.getLliurexVersionLliurexNet()
		log_msg="Get LliurexVersion candidate from lliurex.net: " + str(self.version_available["candidate"])
		self.log(log_msg)
	
	#def getLliurexVersionLliurexNet		

	def checkingInitialFlavourToInstall(self):

		print("  [Lliurex-Up]: Checking if installation of metapackage is required...")

		self.returncode_initflavour=0
		if len(self.targetMetapackage)==0:
			
			print("  [Lliurex-Up]: Installation of metapackage is not required")
			
		else:
			print("  [Lliurex-Up]: Installation of metapackage is required: " + str(self.targetMetapackage))
			is_flavour_installed=self.lliurexcore.installInitialFlavour(self.targetMetapackage)	
			self.returncode_initflavour=is_flavour_installed['returncode']
			error=is_flavour_installed['stderrs']
			log_msg="Install initial metapackage:" + str(self.targetMetapackage) + ": Returncode: " + str(self.returncode_initflavour) + " Error: " + str(error)
			self.log(log_msg)
			print("  [Lliurex-Up]: Metapackage is now installed: Returncode: " + str(self.returncode_initflavour) + " Error: " + str(error))
			
	#def checkingInitialFlavourToInstall		
	
	def getPackagesToUpdate(self):

		print("  [Lliurex-Up]: Looking for new updates...")
		packages=self.lliurexcore.getPackagesToUpdate()
		log_msg="Get packages to update. Number of packages: "+ str(len(packages))
		self.log(log_msg)

		self.newpackages=0
		self.listpackages=""
		if (len(packages))>0:
			for item in packages:
				if packages[item]["install"]==None:
						self.newpackages=int(self.newpackages) + 1
				self.listpackages=str(self.listpackages) + item +" "		

		return packages

	#def getPackagesToUpdate		
			
	def checkingIncorrectFlavours(self):
		
		incorrectFlavours=self.lliurexcore.checkIncorrectFlavours()
		self.aditionalFlavours=incorrectFlavours["data"]
		log_msg="Checking incorrect metapackages. Others metapackages detected: " + str(incorrectFlavours["status"])+". Detected Flavours: "+str(self.aditionalFlavours)
		self.log(log_msg)

		return incorrectFlavours['status']
	
	#def checkingIncorrectFlavours		
		
	def checkPreviousUpgrade(self):
		
		error=False
		if self.returncode_initflavour!=0:
			error=True

		else:
			if self.version_update["candidate"]!=None:
				if self.version_update["installed"]!=self.version_update["candidate"]:
					error=True
			else:
				if self.version_update["installed"]!=self.version_available["candidate"]:	
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
				log_msg="Exec Pre-Actions. Error: %s"%str(output_err)
			else:
				log_msg="Exec Pre-Actions. OK"

		except Exception as e:
			print("  [Lliurex-Up]: Preparing system to update. Error: " +'\n'+str(e))
			log_msg="Exec Pre-Actions. Error " +str(e)
			

		self.log(log_msg)	

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
				output_err=output[1].decode()
			else:
				output_err=output[1]	
			error=self.readErrorOutput(output_err)
			if error:
				print("  [Lliurex-Up]: Downloading and installing packages. Error: "+ '\n' +str(output_err))
				log_msg="Exec Dist-upgrade. Error: %s"%str(output_err)
			else:
				log_msg="Exec Dist-upgrade. OK"
		
		except Exception as e:
			print("  [Lliurex-Up]: Downloading and installing packages. Error: " + '\n' +str(e))
			log_msg="Exec Dist-uggrade.Error : " +str(e)

		self.log(log_msg)	
			
	#def distUpgrade		

	def postActionsScript(self,extra_args):

		print("  [Lliurex-Up]: Ending the update...")

		self.errorpostaction=False

		if extra_args["unattendend_upgrade"]:
			command="DEBIAN_FRONTEND=noninteractive " + self.lliurexcore.postActionsScript() 
		else:
			command=self.lliurexcore.postActionsScript()
	
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
				self.errorpostaction=True
				log_msg="Exec Post-Actions. Error: %s"%str(output_err)
			else:
				log_msg="Exec Post-Actions.OK"

			
		except Exception as e:
			self.errorpostaction=True
			print("  [Lliurex-Up]: Ending the update. Error: " +'\n'+str(e))
			log_msg="Exec Post-Actions.Error:%s"%str(e)

		self.log(log_msg)	

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
			log_msg="N4d is not working"
			self.log(log_msg)

	#def checkFinalN4dStatus		

	def checkingFinalFlavourToInstall(self):
		
		print("  [Lliurex-Up]: Checking final metapackage...")
		self.errorfinalmetapackage=False
		self.checkFinalN4dStatus()

		try:
			self.flavourToInstall=self.lliurexcore.checkFlavour(True)

			log_msg="Final check metapackage. Metapackage to install:%s"%str(self.flavourToInstall)
			self.log(log_msg)
							
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
						output_err=output[1].decode()
					else:
						output_err=output[1]	
					error=self.readErrorOutput(output_err)
					if error:
						self.errorfinalmetapackage=True
						print("  [Lliurex-Up]: Install of metapackage. Error: " +'\n'+str(output_err))
						log_msg="Final install metapackage. Error %s"%str(output_err)
					else:
						log_msg="Final install metapackage.OK"


				except Exception as e:
					self.errorfinalmetapackage=True
					print("  [Lliurex-Up]: Install of metapackage. Error: " +'\n'+str(e))
					log_msg="Install of metapackage. Error:%s"%str(e)

				self.log(log_msg)	
					
							
			else:
				print("  [Lliurex-Up]: Metapackage is correct. Nothing to do")

		except Exception as e:	
			self.errorfinalmetapackage=True
			print("  [Lliurex-Up]: Checking Metapackage. Error:" +'\n'+str(e))
			log_msg="Final check metapackage. Error:%s"%str(e)	
			self.log(log_msg)	
			
	#def checkingFinalFlavourToInstall		
					
	def checkFinalUpgrade(self):


		print("  [Lliurex-Up]: Checking Dist-upgrade...")
		error=self.lliurexcore.checkErrorDistUpgrade()
		errorDetails=str(error[1])

		if error[0] or self.errorfinalmetapackage or self.errorpostaction :
			print("  [Lliurex-Up]: The updated process is endend with errors")
			log_msg="Dist-upgrade process ending with errors. "+errorDetails
			self.distUpgrade_OK=False
		
		else:					
			print("  [Lliurex-Up]: The system is now update")	
			log_msg="Dist-upgrade process ending OK"
			self.distUpgrade_OK=True

		
		self.log(log_msg)
		
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

	def handler_signal(self,signal,frame):
		
		print("\n  [Lliurex-Up]: Cancel process with Ctrl+C signal")
		log_msg="Cancel process with Ctrl+C signal"
		self.log(log_msg)
		if not self.checkingBlock:
			self.cleanEnvironment()
		
		sys.exit(0)
	
	#def handler_signal

	def log(self,msg):
		
		log_file="/var/log/lliurex-up.log"
		f=open(log_file,"a+")
		f.write(msg + '\n')
		f.close()	
	
	#def log


	def free_space_check(self):
		
		free_space=(os.statvfs("/").f_bfree * os.statvfs("/").f_bsize) / (1024*1024*1024)

		if (free_space) < 2: #less than 2GB available?
			print("  [Lliurex-Up]: There's not enough space on disk to upgrade (2 GB needed)")
			log_msg="There's not enough space on disk to upgrade: "+str(free_space)+ " GB available"
			self.log(log_msg)
			self.cleanEnvironment()
			sys.exit(1)

	#def free_space_check		

	def isLliurexUpLocked(self,extra_args):

		print("  [Lliurex-Up]: Checking if LliureX-Up is running...")

		code=self.lliurexcore.isLliurexUpLocked()
		log_msg="------------------------------------------\n"+"LLIUREX-UP-CLI STARTING AT: " + datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") +"\n------------------------------------------"

		
		if code !=0:
			if code!=1:
				self.log(log_msg)
			self.manageLocker(code,"Lliurex-Up")	
		else:
			self.log(log_msg)
							
		
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
				log_msg=action+" is running"
				self.log(log_msg)
			print("  [Lliurex-Up]: "+action+" is now running. Wait a moment and try again")
		
		elif code==3:
			log_msg="Apt is running"
			self.log(log_msg)
			print("  [Lliurex-Up]: Apt is now running. Wait a moment and try again")
		
		elif code==2:
			log_msg=action+" is locked"
			self.log(log_msg)
			if not extra_args["unattendend_upgrade"]:
				response=input( '  [Lliurex-Up]: '+action+' seems blocked by a failed previous execution. Lliurex-Up can not continue if this block is maintained.You want to try to unlock it (yes/no)?')
				if response.startswith('y'):
					self.pulsate_unlocking_process()
				else:
					unlocker=False
			else:
				unlocker=False

		if not unlocker:
			print("  [Lliurex-Up]: "+action+ " seems blocked by a failed previous execution. Unabled to update de sytem")
		
		sys.exit(1)			


	def pulsate_unlocking_process(self):

		self.endProcess=False
		
		result_queue=multiprocessing.Queue()
		self.unlocking_t=multiprocessing.Process(target=self.unlocking_process,args=(result_queue,))
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
			log_msg="The unlocking process finished successfully"
			self.log(log_msg)
			os.execv("/usr/sbin/lliurex-upgrade",sys.argv)
		else:
			if result==1:
				print("  [Lliurex-Up]: The unlocking process has failed")
				log_msg="The unlocking process has failed"
			else:
				print("  [Lliurex-Up]: Some process are running. Wait a moment and try again")
				log_msg="Some process are running. Wait a moment and try again"
	
			self.log(log_msg)
			sys.exit(1)


	#def pulsate_unlocking_process

	def unlocking_process(self,result_queue):

		cmd=self.lliurexcore.unlockerCommand()
		p=subprocess.call(cmd,shell=True,stdout=subprocess.PIPE)
		result_queue.put(p)

	#def unlocking_process	
		
	
	def main(self,mode,extra_args=None):

		self.isLliurexUpLocked(extra_args)
		self.isAptLocked(extra_args)
		self.isDpkgLocked(extra_args)
		self.startLliurexUp(mode)
		self.checkInitialFlavour()

		log_msg="Mode of execution: " + str(self.mode)
		self.log(log_msg)
		log_msg="Extra args: " + str(extra_args)
		self.log(log_msg)
			
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
				print("  [Lliurex-Up]: List of packages to update:\n"+str(self.listpackages))
				print("  [Lliurex-Up]: Number of packages to update:    " +str(len(self.packages)) + " (" + str(self.newpackages) + " news)" )
				print("  [Lliurex-Up]: Current version:                 " +str(self.version_update["installed"]))
				print("  [Lliurex-Up]: Available version (lliurex.net): " +str(self.version_available["candidate"]))
				print("  [Lliurex-Up]: Candidate version (to install):  " +str(self.version_update["candidate"]))
				print("  [Lliurex-Up]: Update source:                   " +str(self.version_update["updateSource"]))
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
					log_msg="Cancel the update"
					self.log(log_msg)
					print("  [Lliurex-Up]: Cancel the update")
					self.cleanEnvironment()

					return 0
			else:
				print("[Lliurex-Up]: Updated abort for incorrect flavours detected in new update. Detected flavours: "+str(self.aditionalFlavours))
				log_msg="Updated abort for incorrect flavours detected in new update"
				self.log(log_msg)
				self.cleanEnvironment()

				return 1			
		else:
			if not self.checkPreviousUpgrade():
				print("  [Lliurex-Up]: Current version:                 " +str(self.version_update["installed"]))
				print("  [Lliurex-Up]: Available version (lliurex.net): " +str(self.version_available["candidate"]))
				print("  [Lliurex-Up]: Candidate version (to install):  " +str(self.version_update["candidate"]))
				print("  [Lliurex-Up]: Update source:                   " +str(self.version_update["updateSource"]))
				print("  [Lliurex-Up]: Your system is updated. Nothing to do")
				log_msg="System updated. Nothing to do"
				self.log(log_msg)
				self.cleanEnvironment()

				return 0
			else:
				print("  [Lliurex-Up]: Updated abort. An error occurred checking new updates")
				log_msg=" Updated abort. An error occurred checking new updates"
				self.log(log_msg)
				self.cleanEnvironment()

				return 1
	#def main			
#class LliurexUpCli
