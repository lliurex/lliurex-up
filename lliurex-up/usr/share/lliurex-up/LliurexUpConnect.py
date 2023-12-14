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

#from math import pi

import lliurex.lliurexup as LliurexUpCore
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


class LliurexUpConnect():

	def __init__(self):

		self.llxUpCore=LliurexUpCore.LliurexUpCore()

		self.preactionsToken=os.path.join(self.llxUpCore.processPath,'preactions_token')
		self.upgradeToken=os.path.join(self.llxUpCore.processPath,'upgrade_token')
		self.installflavourToken=os.path.join(self.llxUpCore.processPath,'installflavour_token')
		self.postactionsToken=os.path.join(self.llxUpCore.processPath,'postactions_token')
		self.errorPostactionToken=self.llxUpCore.errorpostaction_token
		self.errorUpgradeToken=self.llxUpCore.errorupgrade_token
		self.errorFinalMetapackageToken=self.llxUpCore.errorfinalmetapackage_token
		self.finalUpgradeToken=self.llxUpCore.finalupgrade_token
		self.allRepos=False
		self.packagesData=[]
		self.desktopsPath="/usr/share/applications"
		self.standardIconPath="/usr/share/lliurex-up/rsrc"
		self.systemIconPath="/usr/share/icons/hicolor/48x48/apps"
		self.systemScalableIconPath="/usr/share/icons/hicolor/scalable"
		self.disableSystrayPath="/etc/lliurex-up-indicator"
		self.disableSystrayToken=os.path.join(self.disableSystrayPath,"disableIndicator.token")
		self.enabledAutoUpgradeToken="/etc/systemd/system/multi-user.target.wants/lliurex-up-auto-upgrade.service"
		self.numberPackagesDownloaded=[]
		self.numberPackagesUnpacked=[]
		self.numberPackagesInstalled=[]
		self.initialNumberPackages=[]
		self.progressDownload=0
		self.progressDownloadPercentaje=0.00
		self.progressInstallation=0
		self.progressInstallationPercentage=0.00
		self.progressUnpacked=0
		self.progressUnpackedPercentage=0.00
		self.aptCachePath="/var/cache/apt/archives"
		self.connectionWithServer=self.llxUpCore.connectionWithServer

	#def __init__	

	def checkLocks(self):

		self.llxUpCore.checkLocks()

	#def checkLocks

	def isLliurexUpLocked(self):

		code=self.llxUpCore.isLliurexUpLocked()
		msgLog="------------------------------------------\n"+"LLIUREX-UP-GUI STARTING AT: " + datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") +"\n------------------------------------------"

		if code!=0:
			if code ==1:
				msgLog="Lliurex-Up is running"
			elif code==2:
				self.log(msgLog)
				msgLog="Lliurex-Up is locked"
			
		self.log(msgLog)

		return code		

	#def isLliurexUpLocked	

	def isAptLocked(self):
	
		code=self.llxUpCore.isAptLocked()


		if code !=0:
			if code ==1:
				msgLog="Apt is running"
			elif code==2:
				msgLog="Apt is locked"

			self.log(msgLog)

		return 	code

	#def isAptLocked 	

	def isDpkgLocked(self):


		code=self.llxUpCore.isDpkgLocked()

		if code !=0:
			if code ==1:
				msgLog="Dpkg is running"
			elif code==2:
				msgLog="Dpkg is locked"
			elif code==3:
				msgLog="Apt is running"	

			self.log(msgLog)
	
		return 	code	

	#def isDpkgLocked	

	def unlockingProcess(self):

		cmd=self.llxUpCore.unlockerCommand()
		result=subprocess.call(cmd,shell=True,stdout=subprocess.PIPE)

		if result!=0:
			msgLog="The unlocking process has failed"
		else:
			msgLog="The unlocking process finished successfully"

		self.log(msgLog)

		return result	

	#def unlockingProcess	

	def startLliurexUp(self):

		self.llxUpCore.startLliurexUp()

	#def startLliurexUp	

	def freeSpaceCheck(self):

		freeSpace=(os.statvfs("/").f_bfree * os.statvfs("/").f_bsize) / (1024*1024*1024)
		if (freeSpace) < 2: #less than 2GB available?
			msgLog="Not enough space on disk to upgrade (2 GB needed): "+str(freeSpace)+" GB available"
			self.log(msgLog)
			return False
		else:
			return True	

	#def freeSpaceCheck		

	def checkInitialN4dStatus(self):

		self.statusN4d=self.llxUpCore.n4dStatus

		if not self.statusN4d:
			msgLog="N4d is not working"
			self.log(msgLog)

		return self.statusN4d	

	#def checkInitialN4dStatus	

	def checkInitialFlavour(self):

		self.targetMetapackage=self.llxUpCore.checkInitialFlavour()
		msgLog="Initial check metapackage. Metapackage to install: " + str(self.targetMetapackage)
		self.log(msgLog)
		self.previousFlavours=self.llxUpCore.previousFlavours
		msgLog="Get initial metapackage: " + str(self.previousFlavours)
		self.log(msgLog)
		return self.targetMetapackage

	#def checkFlavoour

	def canConnectToLliurexNet(self):

		canConnect=self.llxUpCore.canConnectToLliurexNet()
		msgLog="Checking connection to lliurex.net: %s"%canConnect
		self.log(msgLog)

		if canConnect['status']:
			msgLog="Can connect to lliurex.net: True"
			self.log(msgLog)
			return True
		else:
			msgLog="Can connect to lliurex.net: False"
			self.log(msgLog)
			isClient=self.searchMeta("client")
			if not isClient:
				return False
			else:
				return True		

	#def canConnectToLliurexNet

	def initActionsScript(self):

		arg="initActions"
		command="DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high " + self.llxUpCore.initActionsScript(arg)
		
		try:
		 	os.system(command)
		 	msgLog="Exec Init-Actions"
		 	self.log(msgLog)
		 	return True
		except Exception as e:
		 	msgLog="Exec Init-Actions.Error: " +str(e)
		 	self.log(msgLog)
		 	return False		

	#def initActionsScript	

	def clientCheckingMirrorIsRunning(self):

		isMirrorRunningInServer=self.llxUpCore.clientCheckingMirrorIsRunning()
		msgLog="Checking if mirrror in server is being updated. MirrorManager response: %s"%isMirrorRunningInServer['data']
		self.log(msgLog)		
		
		if isMirrorRunningInServer['ismirrorrunning'] ==None:
			msgLog="Checking if mirror in server is being updated. Error: " + str(isMirrorRunningInServer['exception'])
			self.log(msgLog)
		else:
			if isMirrorRunningInServer['ismirrorrunning']==True:
				msgLog="Mirror is being udpated in server. Unable to update the system"
				self.log(msgLog)

		self.connectionWithServer=self.llxUpCore.connectionWithServer
		return isMirrorRunningInServer['ismirrorrunning']

	#def clientCheckingMirrorIsRunning

	def clientCheckingMirrorExists(self):

		isMirrorExistsInServer=self.llxUpCore.clientCheckingMirrorExists()
		msgLog="Checking if mirrror exists in server. MirrorManager response: %s"%isMirrorExistsInServer['data']
		self.log(msgLog)
	
		if isMirrorExistsInServer['ismirroravailable'] ==None:
			msgLog="Checking if mirror exists in server. Error: " + str(isMirrorExistsInServer['exception'])
			self.log(msgLog)

		else:
			if not isMirrorExistsInServer['ismirroravailable']:
				msgLog="Mirror not detected on the server"
				self.log(msgLog)
				
		self.connectionWithServer=self.llxUpCore.connectionWithServer
		return isMirrorExistsInServer['ismirroravailable']

	#def clientCheckingMirrorIsRunning

	def addSourcesListLliurex(self,args):

		self.llxUpCore.addSourcesListLliurex(args)
		self.allRepos=args

	#def addSourcesListLliurex	

	def isLliurexUpIsUpdated(self):

		try:
			isLliurexupUpdated=self.llxUpCore.isLliurexUpIsUpdated(self.allRepos)
			msgLog="Checking lliurex-up. Is lliurex-up updated: "+ str(isLliurexupUpdated)
			self.log(msgLog)
			return isLliurexupUpdated
		except Exception as e:
			msgLog="Checking lliurex-up. Error: " + str(e)
			self.log(msgLog)
			return True

	#def isLliurexUpIsUpdated

	def installLliurexUp(self):

		try:
			isLliurexupInstalled=self.llxUpCore.installLliurexUp()
			returncode=isLliurexupInstalled['returncode']
			error=isLliurexupInstalled['stderrs']
			msgLog="Installing lliurex-up. Returncode: " + str(returncode) + ". Error: " + str(error)
			self.log(msgLog)
			if returncode==0:
				return True 
			else:
				isLliurexupUpdated=self.llxUpCore.isLliurexUpIsUpdated(self.allRepos)
				if isLliurexupUpdated:
					return True
				else:
					return False
			
		except Exception as e:
			msgLog="Installing lliurex-up. Error: " + str(e)
			self.log(msgLog)
			return True

	#def installLliurexUp	

	def lliurexMirrorIsUpdated(self):

		try:
			isMirrorUpdated=self.llxUpCore.lliurexMirrorIsUpdated()
			msgLog="Checking mirror: %s"%isMirrorUpdated
			self.log(msgLog)
			if isMirrorUpdated !=None:
			
				if isMirrorUpdated['action']=='update':
					msgLog="Checking mirror. Is mirror update: False"
					self.log(msgLog)
					return False
				else: 
					msgLog="Checking mirror. Is mirror update: " + isMirrorUpdated['action']
					self.log(msgLog)
					return True
			else:
				msgLog="Checking mirror. Is mirror update: None"
				self.log(msgLog)
				return True
		
		except Exception as e:
			msgLog="Checking mirror. Error: " + str(e)
			self.log(msgLog)
			return True	

	#def lliurexMirrorIsUpdated		

	def lliurexMirrorIsRunning(self):

		try:
			isLliurexMirrorRunning=self.llxUpCore.lliurexMirrorIsRunning()
			return isLliurexMirrorRunning
		except Exception as e:
			msgLog="Updating mirror. Error: " + str(e)
			self.log(msgLog)
			return False

	#def lliurexMirrorIsRunning		

	def getPercentageLliurexMirror(self):

		try:
			percentageMirror=self.llxUpCore.getPercentageLliurexMirror()
			if percentageMirror != None:
				return percentageMirror
			else:
				return 0	
		
		except Exception as e:
			return 0 	

	#def getPercentageLliurexMirror

	def getLliurexVersionLocal(self):
		
		try:
			self.lliurexVersionLocal=self.llxUpCore.getLliurexVersionLocal()
			msgLog="Get LliurexVersion installed: " + str(self.lliurexVersionLocal["installed"])
			self.log(msgLog)
			msgLog="Get LliurexVersion candidate from local repository: " + str(self.lliurexVersionLocal["candidate"])
			self.log(msgLog)
			msgLog="Get Update source: "+self.lliurexVersionLocal["updateSource"]
			self.log(msgLog)

		except Exception as e:
			msgLog="Get LliurexVersion from local repository. Error: " + str(e)
			self.log(msgLog)
			self.lliurexVersionLocal={"installed":None,"candidate":None,"updateSource":None}

		return self.lliurexVersionLocal

	#def getLliurexVersionLocal(
	
	def getLliurexVersionNet(self):
		
		try:
			self.lliurexVersionNet=self.llxUpCore.getLliurexVersionLliurexNet()["candidate"]
			msgLog="Get LliurexVersion candidate from lliurex.net: " + str(self.lliurexVersionNet)
			self.log(msgLog)
			
		except Exception as e:
			msgLog="Get LliurexVersion from lliurex.net. Error: " + str(e)
			self.log(msgLog)
			self.lliurexVersionNet=None

		return self.lliurexVersionNet	

	#def getLliurexVersionNet
	
	def installInitialFlavour(self,flavourToInstall):

		try:
			isFlavourInstalled=self.llxUpCore.installInitialFlavour(flavourToInstall)
			returncode=isFlavourInstalled['returncode']
			error=isFlavourInstalled['stderrs']
			msgLog="Install initial metapackage:" + str(flavourToInstall) + ": Returncode: " + str(returncode) + " Error: " + str(error)
			self.log(msgLog)
			return returncode
		except Exception as e:
			print(str(e))
			msgLog="Install initial metapackage: " + str(flavourToInstall) + ". Error: " + str(e)
			self.log(msgLog)
			return 1
			
	#def installInitialFlavour

	def getPackagesToUpdate(self):
		
		packagesParsed=[]
		self.totalSize=0
		
		try:
			packages=self.llxUpCore.getPackagesToUpdate()
			if len(packages)>0:
				for item in packages:
					version=packages[item]['candidate']
					size=self.getSizePackagesToUpdate(item)
					install=str(packages[item]['install'])
					architecture=str(packages[item]['architecture'])
					packagesParsed.append(item+";"+version+";"+size+";"+install+";"+architecture)
					
			msgLog="Get packages to update. Number of packages: " + str(len(packages)) 
			self.log(msgLog)		

		except Exception as e:
			msgLog="Get packages to update. Error: " + str(e)
			self.log(msgLog)

		self.totalSize=self.convertSize(self.totalSize)
		self.getPackagesData(packagesParsed)	

		return packagesParsed,self.totalSize
			
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
			self.totalSize=(self.totalSize)+int(size)
			size=self.convertSize(size)
			return size

		except Exception as e:
			print(e)
			return self.convertSize(size) 

	#def getSizePackagesToUpdate

	def convertSize(self,sizeBytes):

		sizeBytes=float(sizeBytes)
		if (sizeBytes == 0):
			return '0B'

		sizeName = ("B", "KB", "MB", "GB")
		i = int(math.floor(math.log(sizeBytes, 1024)))
		p = math.pow(1024, i)
		s = round(sizeBytes/p,)
		s=int(s)
		return '%s %s' % (s, sizeName[i])

	#def convertSize

	def getPackagesData(self,packages):

		self.newPackages=0
		self.packagesData=[]
		self.numberPackagesDownloaded=[]
		self.numberPackagesUnpacked=[]
		self.numberPackagesInstalled=[]
		self.initialNumberPackages=[]

		for item in packages:
			tmp={}
			tmpItem=item.split(";")
			if len(tmpItem)>1:
				if tmpItem[3]==str(None):
					self.newPackages=int(self.newPackages)+1
				tmp["pkgId"]=tmpItem[0]
				tmp["pkgVersion"]=tmpItem[1]
				tmp["pkgSize"]=tmpItem[2]
				tmp["pkgIcon"]=self._parseDesktop(tmpItem[3],tmpItem[0])
				tmp["pkgStatus"]=0
				tmp["showStatus"]=False
				self.packagesData.append(tmp)
				self.numberPackagesDownloaded.append(tmpItem[0]+"_"+tmpItem[1]+"_"+tmpItem[4]+".deb")
				self.numberPackagesUnpacked.append(tmpItem[0]+"_"+tmpItem[1])
				self.numberPackagesInstalled.append(tmpItem[0]+"_"+tmpItem[1])
				self.initialNumberPackages.append(tmpItem[0]+"_"+tmpItem[1])

	#def getPackagesData

	def _parseDesktop(self,installed,name):

		installedIcon=False
		iconWithPath=False
		desktopFile=os.path.join(self.desktopsPath,name+".desktop")

		try:
			if str(installed)=='None':
				icon=os.path.join(self.standardIconPath,"new_package.png")
			else:	
				config = configparser.ConfigParser()
				config.optionxform=str
				config.read(desktopFile)
				
				if config.has_section("Desktop Entry") and config.has_option("Desktop Entry","Icon") and config.get("Desktop Entry","Type").lower()!="zomando":
					icon=config.get("Desktop Entry","Icon")
					installedIcon=True
					if len(icon.split("/"))>1:
						iconWithPath=True
					iconExtension=os.path.splitext(icon)[1]
					if iconExtension!="":
						if iconExtension==".xpm":
							icon=os.path.join(self.standardIconPath,"package.png")
							installedIcon=False
						elif iconExtension==".png":
							if not iconWithPath:
								icon=os.path.join(self.systemIconPath,icon)
						elif iconExtension==".svg":
							if not iconWithPath:
								icon=os.path.join(self.systemScalableIconPath,icon)
					else:
						if not iconWithPath:
							icon=os.path.join(self.systemIconPath,icon+".png")	
				else:
					icon=os.path.join(self.standardIconPath,"package.png")
				
		except Exception as e:
			icon=os.path.join(self.standardIconPath,"package.png")

		if os.path.exists(icon):
			return icon
		else:
			return os.path.join(self.standardIconPath,"package.png")

	#def parseDesktop

	def checkIncorrectFlavours(self):

		incorrectFlavours=self.llxUpCore.checkIncorrectFlavours()

		if incorrectFlavours['status']:
			msgLog="Checking incorrect metapackages. Others metapackages detected: " + str(incorrectFlavours['status']) + ". Detected flavours: "+str(incorrectFlavours['data'])
			self.log(msgLog)
		else:
			msgLog="Checking incorrect metapackages. Others metapackages not detected"
			self.log(msgLog)

		return incorrectFlavours	

	#def checkIncorrectFlavours	

	def getPackageChangelog(self,package):

		changelogFile=os.path.join(self.llxUpCore.changelogsPath,package)
		changelog="Changelog not found"

		if not os.path.exists(changelogFile):
			cmd='LANG=C LANGUAGE=en apt-get changelog %s > %s'%(package,changelogFile)
			p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			poutput,perror=p.communicate()

			if len(perror)>0:
				return changelog
			
		try:
			cmd="sed -i '/Get:1 http\|Fetched/d' " + str(changelogFile)
			os.system(cmd)
			f=open(changelogFile,"r")
			tmpChangelog=f.readlines()
			f.close()
			changelog="".join(str(x) for x in tmpChangelog)
			changelog=changelog.replace("\n ","\n")
								
		except Exception as e:
			return changelog

		return changelog	

	#def getPackageChangelog

	def manageSettingsOptions(self):

		showSettings=True
		try:
			if self.targetMetapackage !=None:
				if self.searchMeta('client') and self.connectionWithServer:
					showSettings=False
			else:
				if self.searchMeta('client') and self.connectionWithServer:	
					showSettings=False

			return showSettings

		except Exception as e:	
			return False

	#def manageSettinsgOptions

	def isSystrayEnabled(self):

		if os.path.exists(self.disableSystrayToken):
			return False
		else:
			return True

	#de isSystrayEnabled

	def manageSystray(self,enable):

		if enable:
			if os.path.exists(self.disableSystrayToken):
				os.remove(self.disableSystrayToken)
		else:
			if not os.path.exists(self.disableSystrayToken):
				if not os.path.exists(self.disableSystrayPath):
					os.mkdir(self.disableSystrayPath)
			
				f=open(self.disableSystrayToken,'w')
				f.close()

	#def manageSystray

	def isAutoUpgradeEnabled(self):

		if os.path.exists(self.enabledAutoUpgradeToken):
			return True
		else:
			return False

	#de isAutoUpgradeEnabled

	def manageAutoUpgrade(self,enable):

		if enable:
			cmd="systemctl enable lliurex-up-auto-upgrade.service"
		else:
			cmd="systemctl disable lliurex-up-auto-upgrade.service"

		os.system(cmd)

	#def manageAutoUpgrade	

	def preActionsScript(self):

		self.preActions=self.llxUpCore.preActionsScript()
		self.preActions='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high ' +self.preActions + ' ;touch ' + self.preactionsToken + '\n'
		msgLog="Exec Pre-Actions"
		self.log(msgLog)
		return self.preActions

	#def preActionsScript	

	def distUpgradeProcess(self):
		
		self.distupgrade=self.llxUpCore.distUpgradeProcess()	
		self.distupgrade='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high ' +self.distupgrade + ' ;touch ' + self.upgradeToken + '\n'
		msgLog="Exec Dist-uggrade"
		self.log(msgLog)
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
				msgLog="Dist-upgrade process ending with errors. "+errorDetails
				self.log(msgLog)
			else:			
				msgLog="Dist-upgrade process ending OK"
				self.log(msgLog)

		except Exception as e:
			print(e)
			msgLog="Error checking distupgrade. Error: " + str(e)
			self.log(msgLog)
			error=True

		return error	

	#def checkErrorDistUpgrade
	
	def getStatusPackage(self):

		command='dpkg -l |grep "^i[i]"'
		packagesStatus=[]
		try:
			p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
			for line in iter(p.stdout.readline,b""):
				if type(line) is bytes:
					line=line.decode()

				tmp=str(line.strip().split()[1].split(":")[0])+"_"+str(line.strip().split()[2])
				packagesStatus.append(tmp)

		except Exception as e:
			print(str(e))
			pass

		return packagesStatus						

	def checkFinalFlavour(self):

		self.errorCheckFlavour=False
		flavourToInstall=None
		
		self.checkFinalN4dStatus()

		try:
			flavourToInstall=self.llxUpCore.checkFlavour(True)
			msgLog="Final check metapackage. Metapackage to install: " + str(flavourToInstall)
			self.log(msgLog)

		except Exception as e:
			self.errorCheckFlavour=True
			msgLog="Final check metapackage. Error: " + str(e)
			self.log(msgLog)

		return flavourToInstall	
	
	#def checkFinalFlavour
	
	def installFinalFlavour(self,flavourToInstall):

		self.command=self.llxUpCore.installFinalFlavour(flavourToInstall)
		self.command='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high ' +self.command + ' 2> >(tee ' + self.errorFinalMetapackageToken + ');touch ' + self.installflavourToken + ' ; exit'+' \n'
		msgLog="Install final metapackage"
		self.log(msgLog)
		return self.command

	#def installFinalFlavour

	def postActionsScript(self):

		self.postActions=self.llxUpCore.postActionsScript()
		self.postActions='DEBIAN_FRONTEND=kde DEBIAN_PRIORITY=high '+self.postActions + ' 2> >(tee ' + self.errorPostactionToken + ') ;touch ' + self.postactionsToken + ' \n'
		#self.postActions=self.postActions + ' ;touch ' + self.postactionsToken + ' \n'

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

	def updatePackagesData(self):

		pkgStatus=self.getStatusPackage()

		for item in self.packagesData:
			pkgName=item["pkgId"]
			pkgVersion=item["pkgVersion"]
			tmpName=pkgName+"_"+pkgVersion
			if tmpName not in pkgStatus:
				item["pkgStatus"]=-1

			item["showStatus"]=True

	#def updatePackagesData		

	def cleanEnvironment(self):
		
		try:
			self.llxUpCore.cleanEnvironment()
			msgLog="Clean environment: OK"
			self.log(msgLog)

		except Exception as e:
			msgLog="Clean environment. Error :" + str(e)
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
		
		lockUser=False
		flavours=[]

		try:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			gid = pwd.getpwnam(user).pw_gid
			groupsGids = os.getgrouplist(user, gid)
			userGroups = [ grp.getgrgid(x).gr_name for x in groupsGids ]

			if 'teachers' in userGroups:
				if 'sudo' not in userGroups and 'admins' not in userGroups:
					cmd='lliurex-version -v'
					p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
					result=p.communicate()[0]
					if type(result) is bytes:
						result=result.decode()
						flavours = [ x.strip() for x in result.split(',') ]	
					
					for item in flavours:
						if 'server' in item or 'client' in item:
							lockUser=True
							break
		
		except Exception as e:
			pass

		return lockUser

	#def checkUser

	def checkProgressDownload(self):

		for i in range(len(self.numberPackagesDownloaded)-1,-1,-1):
			if os.path.exists(os.path.join(self.aptCachePath,self.numberPackagesDownloaded[i])):
				self.numberPackagesDownloaded.pop(i)

		self.progressDownload=len(self.initialNumberPackages)-len(self.numberPackagesDownloaded)
		self.progressDownloadPercentage=round(self.progressDownload/len(self.initialNumberPackages),2)

	#def checkProgressDownload

	def checkProgressUnpacked(self):

		checkInstalledPkg=False
		tmpPackagesUnpacked=self.checkUnpackedStatus()

		if self.progressUnpacked>=len(self.numberPackagesUnpacked):
			tmpPackagesInstalled=self.checkInstalledStatus()
			checkInstalledPkg=True
		
		for i in range(len(self.numberPackagesUnpacked)-1,-1,-1):
			if self.numberPackagesUnpacked[i] in tmpPackagesUnpacked:
				self.numberPackagesUnpacked.pop(i)
			else:
				if checkInstalledPkg:
					if self.numberPackagesUnpacked[i] in tmpPackagesInstalled:
						self.numberPackagesUnpacked.pop(i)

		self.progressUnpacked=len(self.initialNumberPackages)-len(self.numberPackagesUnpacked)
		self.progressUnpackedPercentage=round(self.progressUnpacked/len(self.initialNumberPackages),2)

	#def checkProgressUnpacked

	def checkProgressInstallation(self):

		tmpPackages=self.checkInstalledStatus()
		for i in range(len(self.numberPackagesInstalled)-1,-1,-1):
			if self.numberPackagesInstalled[i] in tmpPackages:
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

	def checkInstalledStatus(self):
		
		cmd='dpkg -l |grep "^i[i]"'
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
	
	#def checkInstalledStatus

#class LliurexUpConnect			
