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
#from math import pi

import lliurex.lliurexup as LliurexUpCore
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


class LliurexUpConnect():

	def __init__(self):

		self.llxUpCore=LliurexUpCore.LliurexUpCore()

		self.preactions_token=os.path.join(self.llxUpCore.processPath,'preactions_token')
		self.upgrade_token=os.path.join(self.llxUpCore.processPath,'upgrade_token')
		self.installflavour_token=os.path.join(self.llxUpCore.processPath,'installflavour_token')
		self.postactions_token=os.path.join(self.llxUpCore.processPath,'postactions_token')
		self.errorpostaction_token=self.llxUpCore.errorpostaction_token
		self.errorupgrade_token=self.llxUpCore.errorupgrade_token
		self.errorfinalmetapackage_token=self.llxUpCore.errorfinalmetapackage_token
		self.finalupgrade_token=self.llxUpCore.finalupgrade_token

	#def __init__	

	def checkLocks(self):

		self.llxUpCore.checkLocks()

	def isLliurexUpLocked(self):

		code=self.llxUpCore.isLliurexUpLocked()
		log_msg="------------------------------------------\n"+"LLIUREX-UP-GUI STARTING AT: " + datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") +"\n------------------------------------------"

		if code!=0:
			if code ==1:
				log_msg="Lliurex-Up is running"
			elif code==2:
				self.log(log_msg)
				log_msg="Lliurex-Up is locked"
			
		self.log(log_msg)

		return code		

	#def isLliurexUpLocked	

	def isAptLocked(self):
	
		code=self.llxUpCore.isAptLocked()


		if code !=0:
			if code ==1:
				log_msg="Apt is running"
			elif code==2:
				log_msg="Apt is locked"

			self.log(log_msg)

		return 	code

	#def isLliurexUpLocked 	

	def isDpkgLocked(self):


		code=self.llxUpCore.isDpkgLocked()

		if code !=0:
			if code ==1:
				log_msg="Dpkg is running"
			elif code==2:
				log_msg="Dpkg is locked"
			elif code==3:
				log_msg="Apt is running"	

			self.log(log_msg)
	
		return 	code	

	#def isDpkgLocked	


	def unlockingProcess(self):

		cmd=self.llxUpCore.unlockerCommand()
		result=subprocess.call(cmd,shell=True,stdout=subprocess.PIPE)

		if result!=0:
			log_msg="The unlocking process has failed"
		else:
			log_msg="The unlocking process finished successfully"

		self.log(log_msg)
		return result	

	#def unlockingProcess	

	def startLliurexUp(self):

		
		self.llxUpCore.startLliurexUp()

	#def startLliurexUp	

	def free_space_check(self):

		if ((os.statvfs("/").f_bfree * os.statvfs("/").f_bsize) / (1024*1024*1024)) < 2: #less than 2GB available?
			log_msg="Not enough space on disk to upgrade (2 GB needed)"
			self.log(log_msg)
			return False
			
		else:
			return True	

	#def free_space_check		

	def checkInitialN4dStatus(self):

		self.statusN4d=self.llxUpCore.n4dStatus

		if not self.statusN4d:
			log_msg="N4d is not working"
			self.log(log_msg)

		return self.statusN4d	

	#def checkInitialN4dStatus	


	def checkInitialFlavour(self):

		self.targetMetapackage=self.llxUpCore.checkInitialFlavour()
		log_msg="Initial check metapackage. Metapackage to install: " + str(self.targetMetapackage)
		self.log(log_msg)
		self.previousFlavours=self.llxUpCore.previousFlavours
		log_msg="Get initial metapackage: " + str(self.previousFlavours)
		self.log(log_msg)
		return self.targetMetapackage

	#def checkFlavoour


	def canConnectToLliurexNet(self):

		can_connect=self.llxUpCore.canConnectToLliurexNet()

		if can_connect:
			log_msg="Can connect to lliurex.net: True"
			self.log(log_msg)
			return True

		else:
			log_msg="Can connect to lliurex.net: False"
			self.log(log_msg)
			#if "lliurex-meta-server" == self.targetMetapackage or "server" in self.llxUpCore.previousFlavours:
			is_client=self.search_meta("client")
			if not is_client:
				return False
			else:
				return True		

	#def canConnectToLliurexNet


	def initActionsScript(self):

		#self.checkInitialFlavour()
		arg="initActions"
		command="DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high " + self.llxUpCore.initActionsScript(arg)
		
		try:
		 	os.system(command)
		 	log_msg="Exec Init-Actions"
		 	self.log(log_msg)
		 	return True

		except Exception as e:
		 	log_msg="Exec Init-Actions.Error: " +str(e)
		 	self.log(log_msg)
		 	return False		

	#def initActionsScript	

	def clientCheckingMirrorIsRunning(self):

		is_mirror_running_inserver=self.llxUpCore.clientCheckingMirrorIsRunning()
		
		if is_mirror_running_inserver['ismirrorrunning'] ==None:
			log_msg="Checking if mirror in server is being updated. Error: " + str(is_mirror_running_inserver['exception'])
			self.log(log_msg)

		else:
			if is_mirror_running_inserver['ismirrorrunning']==True:
				log_msg="Mirror is being udpated in server. Unable to update the system"
				self.log(log_msg)
				
		
		return is_mirror_running_inserver['ismirrorrunning']

	#def clientCheckingMirrorIsRunning


	def clientCheckingMirrorExists(self):

		is_mirror_exists_inserver=self.llxUpCore.clientCheckingMirrorExists()
		
		if is_mirror_exists_inserver['ismirroravailable'] ==None:
			log_msg="Checking if mirror exists in server. Error: " + str(is_mirror_exists_inserver['exception'])
			self.log(log_msg)

		else:
			if not is_mirror_exists_inserver['ismirroravailable']:
				log_msg="Mirror not detected on the server"
				self.log(log_msg)
				
		
		return is_mirror_exists_inserver['ismirroravailable']

	#def clientCheckingMirrorIsRunning

	def addSourcesListLliurex(self,args):

		self.llxUpCore.addSourcesListLliurex(args)

	#def addSourcesListLliurex	

	def isLliurexUpIsUpdated(self):

		try:
			is_lliurexup_updated=self.llxUpCore.isLliurexUpIsUpdated()
			log_msg="Checking lliurex-up. Is lliurex-up updated: "+ str(is_lliurexup_updated)
			self.log(log_msg)
			return is_lliurexup_updated
		
		except Exception as e:
			log_msg="Checking lliurex-up. Error: " + str(e)
			self.log(log_msg)
			return True

	#def isLliurexUpIsUpdated

	def installLliurexUp(self):

		try:
			is_lliurexup_installed=self.llxUpCore.installLliurexUp()
			returncode=is_lliurexup_installed['returncode']
			error=is_lliurexup_installed['stderrs']
			log_msg="Installing lliurex-up. Returncode: " + str(returncode) + ". Error: " + str(error)
			self.log(log_msg)
			return returncode
			
		except Exception as e:
			log_msg="Installing lliurex-up. Error: " + str(e)
			self.log(log_msg)
			return True

	#def installLliurexUp	

	
	def lliurexMirrorIsUpdated(self):

		try:
			is_mirror_updated=self.llxUpCore.lliurexMirrorIsUpdated()

			if is_mirror_updated !=None:
			
				if is_mirror_updated['action']=='update':
					log_msg="Checking mirror. Is mirror update: False"
					self.log(log_msg)
					return False
				else: 
					log_msg="Checking mirror. Is mirror update: " + is_mirror_updated['action']
					self.log(log_msg)
					return True
			else:
				log_msg="Checking mirror. Is mirror update: None"
				self.log(log_msg)
				return True
		
		
		except Exception as e:
			log_msg="Checking mirror. Error: " + str(e)
			self.log(log_msg)
			return True	

	#def lliurexMirrorIsUpdated		

	def lliurexMirrorIsRunning(self):

		try:
			is_lliurexmirror_running=self.llxUpCore.lliurexMirrorIsRunning()
			return is_lliurexmirror_running

		except Exception as e:
			log_msg="Updating mirror. Error: " + str(e)
			self.log(log_msg)
			return False

	#def lliurexMirrorIsRunning		

	def getPercentageLliurexMirror(self):

		try:
			percentage_mirror=self.llxUpCore.getPercentageLliurexMirror()
			if percentage_mirror != None:
				return percentage_mirror
			else:
				return 0	
		
		except Exception as e:
			return 0 	


	#def getPercentageLliurexMirror

	def getLliurexVersionLocal(self):
		
		try:
			
			self.lliurexVersionLocal=self.llxUpCore.getLliurexVersionLocal()
			log_msg="Get LliurexVersion installed: " + str(self.lliurexVersionLocal["installed"])
			self.log(log_msg)
			log_msg="Get LliurexVersion candidate from Local repository: " + str(self.lliurexVersionLocal["candidate"])
			self.log(log_msg)

		except Exception as e:
			log_msg="Get LliurexVersion from Local repository. Error: " + str(e)
			self.log(log_msg)
			self.lliurexVersionLocal={"installed":None,"candidate":None}

		return self.lliurexVersionLocal

	#def getLliurexVersionLocal(
	
	def getLliurexVersionNet(self):
		
		try:
			self.lliurexVersionNet=self.llxUpCore.getLliurexVersionLliurexNet()["candidate"]
			log_msg="Get LliurexVersion candidate from Lliurex Net: " + str(self.lliurexVersionNet)
			self.log(log_msg)
			

		except Exception as e:
			log_msg="Get LliurexVersion from Lliurex Net. Error: " + str(e)
			self.log(log_msg)
			self.lliurexVersionNet=None

		return self.lliurexVersionNet	

	#def getLliurexVersionNet
	
	def installInitialFlavour(self,flavourToInstall):

		try:
			is_flavour_installed=self.llxUpCore.installInitialFlavour(flavourToInstall)
			returncode=is_flavour_installed['returncode']
			error=is_flavour_installed['stderrs']
			log_msg="Install initial metapackage:" + str(flavourToInstall) + ": Returncode: " + str(returncode) + " Error: " + str(error)
			self.log(log_msg)
			return returncode

		except Exception as e:
			print(str(e))
			log_msg="Install initial metapackage: " + str(flavourToInstall) + ". Error: " + str(e)
			self.log(log_msg)
			return 1
			
	#def installInitialFlavour

	def getPackagesToUpdate(self):
		
		packages_parse=[]
		self.total_size=0
		
		try:
			packages=self.llxUpCore.getPackagesToUpdate()
			if len(packages)>0:
				for item in packages:
					version=packages[item]['candidate']
					size=self.getSizePackagesToUpdate(item)
					install=str(packages[item]['install'])
					packages_parse.append(item+";"+version+";"+size+";"+install)
					
			log_msg="Get packages to update. Number of packages: " + str(len(packages)) 
			self.log(log_msg)		

		except Exception as e:
			log_msg="Get packages to update. Error: " + str(e)
			self.log(log_msg)

		self.total_size=self.convert_size(self.total_size)	
		return packages_parse,self.total_size
			
	#def getPackagesToUpdate
	
	def getSizePackagesToUpdate(self,pkg):
		size=0
		try:
			command='apt-cache show ' + pkg + ' |grep "^Size:" |cut -d " " -f2 |head -1'
			p=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
			size=p.stdout.readline()
			if type(size) is bytes:
				size=size.decode()
			size=size.strip()
			self.total_size=(self.total_size)+int(size)
			size=self.convert_size(size)
			return size

		except Exception as e:
			print(e)
			return self.convert_size(size) 
	

	def convert_size(self,size_bytes):

		size_bytes=float(size_bytes)
		if (size_bytes == 0):
			return '0B'

		size_name = ("B", "KB", "MB", "GB")
		i = int(math.floor(math.log(size_bytes, 1024)))
		p = math.pow(1024, i)
		s = round(size_bytes/p,)
		s=int(s)
		return '%s %s' % (s, size_name[i])

	
	def checkIncorrectFlavours(self):

		incorrectFlavours=self.llxUpCore.checkIncorrectFlavours()

		if incorrectFlavours['status']:
			log_msg="Checking incorrect metapackages. Others metapackages detected: " + str(incorrectFlavours['status']) + ". Detected flavours: "+str(incorrectFlavours['data'])
			self.log(log_msg)
		else:
			log_msg="Checking incorrect metapackages. Others metapackages not detected"
			self.log(log_msg)

		return incorrectFlavours	

	#def checkIncorrectFlavours	

	def getPackageChangelog(self,package):

		changelog_file=os.path.join(self.llxUpCore.changelogsPath,package)
		changelog="Changelog not found"

		if not os.path.exists(changelog_file):
			cmd='LANG=C LANGUAGE=en apt-get changelog %s > %s'%(package,changelog_file)
			p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			poutput,perror=p.communicate()

			if len(perror)>0:
				return changelog
			
		try:
			cmd="sed -i '/Get:1 http\|Fetched/d' " + str(changelog_file)
			os.system(cmd)
			f=open(changelog_file,"r")
			changelog=f.readlines()
			f.close()
								
		except Exception as e:
			changelog="Changelog not found"	

		return changelog	

	#def getPackageChangelog		

	def preActionsScript(self):

		self.preActions=self.llxUpCore.preActionsScript()
		self.preActions='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high ' +self.preActions + ' ;touch ' + self.preactions_token + '\n'
		log_msg="Exec Pre-Actions"
		self.log(log_msg)
		return self.preActions

	#def preActionsScript	

	def distUpgradeProcess(self):
		
		self.distupgrade=self.llxUpCore.distUpgradeProcess()	
		self.distupgrade='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high ' +self.distupgrade + ' ;touch ' + self.upgrade_token + '\n'
		log_msg="Exec Dist-uggrade"
		self.log(log_msg)
		return self.distupgrade

	#def distUpgradeProcess
	
	def checkErrorDistUpgrade(self):

		error=False
		errorDetails=""
		try:
			errorDistUpgrade=self.llxUpCore.checkErrorDistUpgrade()
			errorDetails=str(errorDistUpgrade[1])
			
			if errorDistUpgrade[0] or self.errorCheckFlavour:
				error=True
				log_msg="Dist-upgrade process ending with errors. "+errorDetails
				self.log(log_msg)
			else:			
				log_msg="Dist-upgrade process ending OK"
				self.log(log_msg)

		except Exception as e:
			print(e)
			log_msg="Error checking distupgrade. Error: " + str(e)
			self.log(log_msg)
			error=True

		return error	
				

	#def checkErrorDistUpgrade
	
	def getStatusPackage(self):

		command='dpkg -l |grep "^i[i]"'
		packages_status=[]
		try:
			p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
			for line in iter(p.stdout.readline,b""):
				if type(line) is bytes:
					line=line.decode()

				tmp=str(line.strip().split()[1].split(":")[0])+"_"+str(line.strip().split()[2])
				packages_status.append(tmp)

		except Exception as e:
			print(str(e))

		return packages_status						

	def checkFinalFlavour(self):

		self.errorCheckFlavour=False
		flavourToInstall=None
		
		self.checkFinalN4dStatus()

		try:
			#flavourToInstall=self.llxUpCore.checkFinalFlavour()
			flavourToInstall=self.llxUpCore.checkFlavour(True)
			log_msg="Final check metapackage. Metapackage to install: " + str(flavourToInstall)
			self.log(log_msg)

		except Exception as e:
			self.errorCheckFlavour=True
			log_msg="Final check metapackage. Error: " + str(e)
			self.log(log_msg)

		
		return flavourToInstall	

	
	#def checkFinalFlavour
	
	def installFinalFlavour(self,flavourToInstall):

		self.command=self.llxUpCore.installFinalFlavour(flavourToInstall)
		self.command='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high ' +self.command + ' 2> >(tee ' + self.errorfinalmetapackage_token + ');touch ' + self.installflavour_token + ' ; exit'+' \n'
		log_msg="Install final metapackage"
		self.log(log_msg)
		return self.command

	#def installFinalFlavour

	def postActionsScript(self):

		self.postActions=self.llxUpCore.postActionsScript()
		self.postActions='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high '+self.postActions + ' 2> >(tee ' + self.errorpostaction_token + ') ;touch ' + self.postactions_token + ' \n'
		#self.postActions=self.postActions + ' ;touch ' + self.postactions_token + ' \n'

		log_msg="Exec Post-Actions"
		self.log(log_msg)
		return self.postActions

	#def postActionsScript

	def checkFinalN4dStatus(self):

		self.llxUpCore.checkN4dStatus()

		if not self.llxUpCore.n4dStatus:
			log_msg="N4d is not working"

			self.log(log_msg)

	#def checkFinalN4dStatus		


	def cleanEnvironment(self):
		
		try:
			self.llxUpCore.cleanEnvironment()
			log_msg="Clean environment: OK"
			self.log(log_msg)

		except Exception as e:
			log_msg="Clean environment. Error :" + str(e)
			self.log(log_msg)				

	#def cleanEnvironment

	def cleanLliurexUpLock(self):

		try:
			self.llxUpCore.cleanLliurexUpLock()
		
		except Exception as e:
			print(e)
	
	#def cleanLliurexUpLock		

	def search_meta(self,meta):
		
		match=False
		try:
			match=self.llxUpCore.search_meta(meta)
			return match
		except Exception as e:
			return match

	#def searchMeta			

	def log(self,msg):
		
		log_file="/var/log/lliurex-up.log"
		f=open(log_file,"a+")
		f.write(msg + '\n')
		f.close()

	#def log			
