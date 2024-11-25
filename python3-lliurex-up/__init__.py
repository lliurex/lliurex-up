#!/usr/bin/python3
# -*- coding: utf-8 -*

import xmlrpc.client as n4dclient 
import os
import shutil
import subprocess
import socket
import distutils.dir_util
import urllib.request
import time
import psutil
import struct, fcntl
import ssl
import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager



class LliurexUpCore(object):
	"""docstring for LliurexUpCore"""
	def __init__(self):
		super(LliurexUpCore, self).__init__()
		self.flavourReference=["lliurex-meta-home-adi","lliurex-meta-home-desktop"] 
		self.defaultMirror = 'llx25'
		self.defaultVersion = 'noble'
		self.defaultUrltoCheck="http://lliurex.net/jammy"
		self.lockTokenPath="/var/run/lliurexUp.lock"
		self.processPath = '/var/run/lliurex-up'
		self.sourcesListPath='/etc/apt/'
		self.changelogsPath = os.path.join(self.processPath,'changelogs')
		self.processSourceslist = os.path.join(self.processPath,'sourceslist')
		self.origsourcesfile=os.path.join(self.sourcesListPath,"sources.list")
		self.origsourcesfileback=os.path.join(self.sourcesListPath,"lliurexup_sources.list")
		self.targetMetapackagePath=os.path.join(self.processPath,"targetMetapackage")
		self.previousFlavoursPath = os.path.join(self.processPath,'previousflavours')
		self.errorPostActionToken=os.path.join(self.processPath,'errorpostaction_token')
		self.errorFinalMetapackageToken=os.path.join(self.processPath,'errorfinalmetapackage_token')
		self.errorUpgradeToken=os.path.join(self.processPath,'errorupgrade_token')
		self.finalUpgradeToken=os.path.join(self.processPath,'finalupgrade_token')

		self.initActionsPath='/usr/share/lliurex-up/initActions'
		self.preActionsPath = '/usr/share/lliurex-up/preActions'
		self.postActionsPath = '/usr/share/lliurex-up/postActions'
		self.optionsLlxUp=""
		self.desktopClientized=False
		self.connectionWithADI=True
		self.dpkgUnlocker=DpkgUnlockerManager.DpkgUnlockerManager()
		self.autoUpgradeService="/usr/lib/systemd/system/lliurex-up-auto-upgrade.service"

	#def __init__	

	def startLliurexUp(self):

		self.createLockToken()
		self.retryN4d=True
		self.n4dStatus=True
		context=ssl._create_unverified_context()
		self.n4d = n4dclient.ServerProxy('https://localhost:9779',context=context,allow_none=True)

		self.checkN4dStatus()
		
		self.haveLliurexMirror = False
		self.metapackageRef=[]
		self.previousFlavours = []

		self.getTargetMetapackage()
		self.flavours = []
		self.lastFlavours=[]
		self.getPreviousFlavours()

		if self.n4dStatus:
			if len(self.n4d.get_methods('MirrorManager')) > 0:
				self.haveLliurexMirror = True
			
		self.retryN4d=True
		self.prepareEnvironment()

	#def startLliurexUp	

	def checkLocks(self):

		self.locks_info=self.dpkgUnlocker.checkingLocks()

	#def checkLocks
	
	def isLliurexUpLocked(self):

		'''
		 0: Lliurex-Up is not running
		 1: Lliurex-Up is running
		 2: Lliurex-Up is locked for previous failed process
		 ''' 

		return self.locks_info["Lliurex-Up"]

	#def isLliurexUpLocked		

	def isAptLocked(self):

		'''
		 0: Apt is not running
		 1: Apt is running
		 2: Apt is locked for previous failed process
		'''
		return self.locks_info["Apt"]	

	#def isAptLocked
		
	def isDpkgLocked(self):

		'''
		 0: Dpkgis not running
		 1: Dpkg is running
		 2: Dpkg is locked for previous failed process
		 3: Apt is running

		 ''' 
		return self.locks_info["Dpkg"]		

	#def isAptLocked			

	def unlockerCommand(self):

		return "/usr/sbin/dpkg-unlocker-cli unlock -u"

	#def unlockeCommand				

	def createLockToken(self):

		if not os.path.exists(self.lockTokenPath):
			f=open(self.lockTokenPath,'w')
			up_pid=os.getpid()
			f.write(str(up_pid))
			f.close()

	#def createLockToken		

	def getPreviousFlavours(self):
		
		if os.path.exists(self.previousFlavoursPath):
			aux = open(self.previousFlavoursPath,'r')
			lines = aux.readlines()
			for x in lines:
				self.previousFlavours.append(x.strip())
			aux.close()
		
	#def getPreviousFlavours		

	def checkN4dStatus(self):
	
		try:
			test=self.n4d.get_methods()
			self.n4dStatus=True
		except:
			if self.retryN4d:
				self.retryN4d=False
				try: 
					cmd='systemctl restart n4d.service 1>/dev/null'
					restart=os.system(cmd)
					time.sleep(5)
					if restart==0:
						self.checkN4dStatus()
					else:
						self.n4dStatus=False
				except Exception as e:
					self.n4dStatus=False
			else:
				self.n4dStatus=False
		
	#def checkN4dStatus		
			
	def getTargetMetapackage(self):

		if os.path.exists(self.targetMetapackagePath):
			aux = open(self.targetMetapackagePath,'r')
			lines = aux.readlines()
			for x in lines:
				self.metapackageRef.append(x.strip())
			aux.close()		
		
	#def getTargetMetapackage
			
	def saveTargetMetapackage(self,targetMetapackage):

		aux=open(self.targetMetapackagePath,'w')
		for x in targetMetapackage:
			x=x.split("-")[2]	
			aux.write(x+"\n")

		x="edu"
		aux.write(x+"\n")
		aux.close()

	#def saveTargetMetapackage	

	def checkInitialFlavour(self,args=None):

		self.targetMetapackage=self.checkFlavour()
		
		if len(self.metapackageRef)==0:
			self.getTargetMetapackage()
			
		self.metapackageRef=sorted(self.metapackageRef)	
		 	 
		if len(self.previousFlavours)==0:
			self.getPreviousFlavours()
		

		self.writeDefaultSourceslist()
		self.writeDefaultSourceslistMirror()
		self.writeDefaultSourceslistAll()

		return self.targetMetapackage

	#def checkInitialFlavour	
		
	def updateFlavoursList(self,args=None):
		
		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]
		if type(result) is bytes:
			result=result.decode()
		
		if args==None:
			for x in result.split(','):
				if x.strip() in ["edu","live"]:
					pass
				else:
					if x.strip() not in self.flavours:
						self.flavours.append(x.strip())

			if len(self.flavours) > 0:
				aux = open(self.previousFlavoursPath,'w')
				for x in self.flavours:
					aux.write(x+"\n")
				aux.close()
		else:
			for x in result.split(','):
				if x.strip() in ["edu","live"]:
					pass
				else:
					self.lastFlavours.append(x.strip())

	#def updateFlavoursList		

	def writeDefaultSourceslist(self):

		f = open(os.path.join(self.processSourceslist,'default'),'w')
		f.write('deb http://lliurex.net/{version} {version} main restricted universe multiverse\n'.format(version=self.defaultVersion))
		f.write('deb http://lliurex.net/{version} {version}-updates main restricted universe multiverse\n'.format(version=self.defaultVersion))
		f.write('deb http://lliurex.net/{version} {version}-security main restricted universe multiverse\n'.format(version=self.defaultVersion))
		f.close()

	#def writeDefaultSourceslist	

	def writeDefaultSourceslistMirror(self):
		
		f = open(os.path.join(self.processSourceslist,'default_mirror'),'w')
		f.write('deb http://mirror/{version_mirror} {version} main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
		f.write('deb http://mirror/{version_mirror} {version}-updates main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
		f.write('deb http://mirror/{version_mirror} {version}-security main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
		f.close()	

	#def writeDefaultSourceslistMirror	

	def writeDefaultSourceslistAll(self):
		
		f = open(os.path.join(self.processSourceslist,'default_all'),'w')
		f.write('deb http://mirror/{version_mirror} {version} main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
		f.write('deb http://mirror/{version_mirror} {version}-updates main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
		f.write('deb http://mirror/{version_mirror} {version}-security main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
		f.write('deb http://lliurex.net/{version} {version} main restricted universe multiverse\n'.format(version=self.defaultVersion))
		f.write('deb http://lliurex.net/{version} {version}-updates main restricted universe multiverse\n'.format(version=self.defaultVersion))
		f.write('deb http://lliurex.net/{version} {version}-security main restricted universe multiverse\n'.format(version=self.defaultVersion))
		f.close()	

	#def writeDefaultSourceslistAll		

	def prepareEnvironment(self):
		'''
			This funcion delete all environment and rebuild environment

		'''
		self.cleanEnvironment()
		if not os.path.exists(self.processPath):
			os.mkdir(self.processPath)
		if not os.path.exists(self.processSourceslist):
			os.mkdir(self.processSourceslist)
		if not os.path.exists(self.changelogsPath):
			os.mkdir(self.changelogsPath)

	#def prepareEnvironment	

	def addSourcesListLliurex(self,args=None):
		
		newsourcesfile=os.path.join(self.sourcesListPath,'sources.list')
		extrasources=[]
		client=False
		textSearchMirror="/mirror/"+str(self.defaultMirror)
		textSearchLliureX="/lliurex.net/"+str(self.defaultVersion)
		
		isADI=self.searchMeta("adi")		

		if not isADI:
			if self.connectionWithADI:
				client=True
				if args:
					sourcesref=os.path.join(self.processSourceslist, 'default_all')
				else:
					sourcesref=os.path.join(self.processSourceslist, 'default_mirror')
			else:
				sourcesref=os.path.join(self.processSourceslist, 'default')	
	
		else:
			sourcesref=os.path.join(self.processSourceslist, 'default')	

		if os.path.exists(self.origsourcesfile):
			os.rename(self.origsourcesfile,self.origsourcesfileback)
			origsources=open(self.origsourcesfileback,'r')
			if not client:
				for line in origsources:
					if not textSearchLliureX in line:
						extrasources.append(line.strip())
			else:
				for line in origsources:
					if args:
						if (not textSearchLliureX in line) and (not textSearchMirror in line):
							extrasources.append(line.strip())
					else:
						if not textSearchMirror in line:
							extrasources.append(line.strip())		

			origsources.close()
				
			if os.path.exists(sourcesref):
				shutil.copy(sourcesref,self.origsourcesfile)
				if len(extrasources)>0:	
					newsourcesedit=open(newsourcesfile,'a')
					for line in extrasources:
						newsourcesedit.write(line+'\n')
					newsourcesedit.close()
			else:
				os.rename(self.origsourcesfileback,self.origsourcesfile)					
	
	#def addSourcesListLliurex 		

	def restoreOrigSourcesList(self):
		
		if os.path.exists(self.origsourcesfileback):
			os.rename(self.origsourcesfileback,self.origsourcesfile)

	#def restoreOrigSourcesList		

	def readSourcesList(self):
		
		count=0
		if os.path.exists(self.origsourcesfile):
			sources=open(self.origsourcesfile,'r')
			ref="/lliurex.net/"+str(self.defaultVersion)
			for line in sources:
				if ref in line:
					if not "#" in line:
						count=count+1
		return count	

	#def readSourcesList		

	def cleanEnvironment(self):
		
		if os.path.exists(self.processPath):
			shutil.rmtree(os.path.join(self.processPath))

		self.restoreOrigSourcesList()	

	#def cleanEnvironment	

	def cleanLliurexUpLock(self):

		if os.path.exists(self.lockTokenPath):
			os.remove(self.lockTokenPath)

	#def cleanLliurexUpLock		

	def updateCacheApt(self,options=""):
		
		command = "LANG=C LANGUAGE=en apt-get update {options}".format(options=options)
		subprocess.Popen(command,shell=True).communicate()

	#def updateCacheApt	

	def getPackageVersionAvailable(self,package,options="",checkRepo=False):
		'''
			Args :
				package String
				options String

			return dictionary => result
			result : {'installed':String,'candidate':String}

			Options are Apt options 
		'''
		command = "LANG=C LANGUAGE=en apt-cache policy {package} {options}".format(package=package,options=options)
		p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
		installed = None
		candidate = None
		getRepo=False
		updateSource=None

		for line in iter(p.stdout.readline,b""):
			if type(line) is bytes:
				line=line.decode()

			stripedline = line.strip()
			if stripedline.startswith("Installed"):
				installed = stripedline.replace("Installed: ","")
			if stripedline.startswith("Candidate"):
				candidate = stripedline.replace("Candidate: ","")
			if checkRepo:
				if candidate !=None:
					if candidate in stripedline:
						getRepo=True 
			if getRepo:
				if stripedline.startswith("666"):
					try:
						updateSource=stripedline.split(" ")[1]
						getRepo=False
					except:
						getRepo=False

		return {"installed":installed,"candidate":candidate,"updateSource":updateSource}

	#def getPackageVersionAvailable	

	def isLliurexUpIsUpdated(self,args=None):
		'''
			return Boolean 
		'''
		sourceslistDefaultPath = os.path.join(self.processSourceslist,'default')

		isADI=self.searchMeta("adi")		

		if not isADI:
			if self.connectionWithADI:
				if not args:
					sources=self.readSourcesList()
					if sources==0:
						sourceslistDefaultPath = os.path.join(self.processSourceslist,'default_mirror')
					else:
						if not self.canConnectToLliurexNet()['status']:
							sourceslistDefaultPath = os.path.join(self.processSourceslist,'default_mirror')
						

		self.optionsLlxUp = "-o Dir::Etc::sourcelist={sourceslistOnlyLliurex} -o Dir::Etc::sourceparts=/dev/null".format(sourceslistOnlyLliurex=sourceslistDefaultPath)

		self.updateCacheApt(self.optionsLlxUp)
		result = self.getPackageVersionAvailable('lliurex-up',self.optionsLlxUp)

		if result['installed'] != result['candidate']:
			return False
		return True

	#def isLliurexUpIsUpdated	

	def installLliurexUp(self,options=""):
		'''
			Args :
				options String
			return dictionary => result
			result : {'returncode':Int,'stdout':String,'stderr':String}

			options are Apt options
			

			This function install lliurex-up
		'''
		self.updateCacheApt(self.optionsLlxUp)
		command = "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get install --allow-downgrades --allow-remove-essential --allow-change-held-packages --yes lliurex-up {options}".format(options=self.optionsLlxUp)
		p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		poutput,perror = p.communicate()

		if len(poutput)>0:
			if type(poutput) is bytes:
				poutput=poutput.decode()

		if len(perror)>0:
			if type(perror) is bytes:
				perror=perror.decode()
								
		return {'returncode':p.returncode,'stdout':poutput,'stderrs':perror}

	#def installLliurexUp	

	def lliurexMirrorIsUpdated(self):
		'''
			return None | dictionary => result
			result : {'status':Boolean,'msg':String,'action':String}
			result.msg : message of status
			result.action : Action to launch
		'''
		isADI=self.searchMeta("adi")

		if self.haveLliurexMirror and (isADI):
			result = self.n4d.is_update_available('','MirrorManager',self.defaultMirror)
			if result['status_code']==0:
				if result["return"]["action"]=="update":
					return {"action":"update","data":result}
				else:
					return {"action":"nothing-to-do","data":result}
			else:
				return {"action":"nothing-to-do","data":result}
		
		return None

	#def lliurexMirrorIsUpdated	

	def lliurexMirrorIsRunning(self):
		'''
			return Boolean
		'''
		isADI=self.searchMeta("adi")

		if self.haveLliurexMirror and (isADI):
			result = self.n4d.is_alive('','MirrorManager')
			return result['return']['status']
		return False

	#def lliurexMirrorIsRunning	

	def clientCheckingMirrorIsRunning(self):

		isADI=self.searchMeta("adi")

		if not isADI:
			try:
				context=ssl._create_unverified_context()
				client=n4dclient.ServerProxy('https://server:9779',context=context,allow_none=True)
				result=client.is_alive('','MirrorManager')
				return {'ismirrorrunning':result['return']['status'],'exception':False,'data':result}
			
			except Exception as e:
				self.connectionWithADI=False					

		return {'ismirrorrunning':False,'exception':False,'data':""}	

	#def clientCheckingMirrorIsRunning	

	def clientCheckingMirrorExists(self):

		isADI=self.searchMeta("adi")
		
		if not isADI:				
			try:
				context=ssl._create_unverified_context()
				client=n4dclient.ServerProxy('https://server:9779',context=context,allow_none=True)
				try:
					result=client.is_mirror_available('','MirrorManager')
					if result['status']==0:
						return {'ismirroravailable':True,'exception':False,'data':result}
					else:
						return {'ismirroravailable':False,'exception':False,'data':result}
				except Exception as e :
					self.connectionWithADI=False
					return {'ismirroravailable':False,'exception':False,'data':''}
				
			except Exception as e:
				self.connectionWithADI=False
				return {'ismirroravailable':False,'exception':False,'data':''}					
		else:
			return {'ismirroravailable':True,'exception':False,'data':''}	

	#def clientCheckingMirrorExists	

	def getPercentageLliurexMirror(self):
		'''
			return int | None
		'''
		isADI=self.searchMeta("adi")

		if self.haveLliurexMirror and (isADI):
	
			try:
				result = self.n4d.get_percentage('','MirrorManager',self.defaultMirror)['return']
				return result
			except:
				return None	
		return None

	#def getPercentageLliurexMirror	
	
	def checkFlavour(self,args=None):
		'''
			return None|String
			If metapackages has been uninstalled, this function return 
			package to must install. If return None, you are ok and don't need 
			install anything.
		'''
		self.updateFlavoursList(args)
		targetMetapackage = []
				
		if args==None:
			recoveryMeta=False
			if 'None' in self.flavours:
				recoveryMeta=True

			if recoveryMeta:
				cmd='lliurex-version --history'
				p=subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)
				result=p.communicate()[0]
				if type(result) is bytes:
					result=result.decode()

				if result:
					history = [ x.strip().split('\t')[0].strip() for x in result.split('\n') ]
					history = [ x for x in history if not 'lliurex-meta-live' in x ]
					for x in reversed(history):
						if x.startswith('-'):
							targetMetapackage.append(x[2:])
							break

			if len(targetMetapackage)>0:
				self.saveTargetMetapackage(targetMetapackage)				
			return targetMetapackage
		else:
			if 'None' in self.lastFlavours:
				if 'None' in self.flavours:
					if 'None' not in self.previousFlavours:
						targetMetapackage.append(self.previousFlavours)
					if 'None' not in self.metapackageRef:
						targetMetapackage=list(set(targetMetapackage+self.metapackageRef))
				else:
					targetMetapackage=self.flavours
					if 'None' not in self.previousFlavours:
						targetMetapackage=list(set(targetMetapackage+self.previousFlavours))
					if 'None' not in self.metapackageRef:	
						targetMetapackage=list(set(targetMetapackage+self.metapackageRef))
			else:
				tmp=[]
				if 'None' in self.flavours:
					if 'None' not in self.previousFlavours:
						tmp.append(self.previousFlavours)
					if 'None' not in self.metapackageRef:
						tmp=list(set(tmp+self.metapackageRef))
				else:
					tmp=self.flavours
					if 'None' not in self.previousFlavours:
						tmp=list(set(tmp+self.previousFlavours))
					if 'None' not in self.metapackageRef:
						tmp=list(set(tmp+self.metapackageRef))
				targetMetapackage=list(set(tmp)-set(self.lastFlavours))
			tmpList=[]
			for item in targetMetapackage:
				if item not in ['edu','live']:
					if "lliurex-meta" not in item:
						tmp="lliurex-meta-"+item
					tmpList.append(tmp)	
			
			return tmpList		
					
	#def checkFlavour	

	def canConnectToLliurexNet(self):
		
		'''
			return dictionary => result
			result : {'status':bool,'data':String}
		'''
		try:
			res=urllib.request.urlopen(self.defaultUrltoCheck)
			return {'status':True,'data':str(res)}
		except Exception as e:
			return {'status':False,'data':str(e)}

	#def canConnectToLliurexNet		
				
	def getLliurexVersionLliurexNet(self):
		'''
			return dictionary => result
			result : {'installed':String,'candidate':String}
		'''
		sourceslistDefaultPath = os.path.join(self.processSourceslist,'default')
		options = ""
		if self.canConnectToLliurexNet()['status']:
			options = "-o Dir::Etc::sourcelist={sourceslistOnlyLliurex} -o Dir::Etc::sourceparts=/dev/null".format(sourceslistOnlyLliurex=sourceslistDefaultPath)
		self.updateCacheApt(options)
		
		return self.getPackageVersionAvailable('lliurex-version-timestamp',options)

	#def getLliurexVersionLliurexNet	
	
	def getLliurexVersionLocal(self):
		
		self.updateCacheApt('')
		
		return self.getPackageVersionAvailable('lliurex-version-timestamp','',True)		

	#def getLliurexVersionLocal

	def initActionsScript(self,arg):
		
		return 'run-parts --arg=' +str(arg) + ' ' + self.initActionsPath

	#def initActionsScript

	def preActionsScript(self):
		
		return 'run-parts --arg="preActions" ' + self.preActionsPath

	#def preActionsScript

	def postActionsScript(self):
		
		return 'run-parts --arg="postActions" ' + self.postActionsPath

	#def postActionsScript

	def installInitialFlavour(self,flavourToInstall,options=""):
		'''
			Args :
				flavourToInstall String
				options String
			return dictionary => result
			result : {'returncode':Int,'stdout':String,'stderr':String}

			options are Apt options
			

			This function install lliurex-up
		'''
		tmpList=""
		for item in flavourToInstall:
			tmpList=tmpList+item+" "
		self.updateCacheApt(options)
		command = "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get install --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages " + tmp_list + "{options} ".format(options=options)
		p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		poutput,perror = p.communicate()
		
		if p.returncode!=0:
			command = "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get install -f --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages {options} ".format(options=options)
			p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			poutput,perror = p.communicate()
			if len(poutput)>0:
				if type(poutput) is bytes:
					poutput=poutput.decode()

			if len(perror)>0:
				if type(perror) is bytes:
					perror=perror.decode()
					
		return {'returncode':p.returncode,'stdout':poutput,'stderrs':perror}	

	#def installInitialFlavour

	def getPackagesToUpdate(self):
		'''
			packageInfo definition
			{
				'PACKAGENAME' : {
						'install' : 'INSTALLEDVERSION',
						'candidate' : 'CANDIDATEVERSION',
						'icon' : 'ICONNAME',
						'changelog' : 'CHANGELOGTEXT'
				}
			}
		'''
		self.packageInfo = {}
		self.updateCacheApt("")
		psimulate = subprocess.Popen('LANG=C LANGUAGE=en apt-get dist-upgrade -sV',shell=True,stdout=subprocess.PIPE)
		rawoutputpsimulate = psimulate.stdout.readlines()
		rawpackagestoinstall = [ aux.decode().strip() for aux in rawoutputpsimulate if aux.decode().startswith('Inst') ]
		r = [ aux.replace('Inst ','') for aux in rawpackagestoinstall ]
		for allinfo in r :
			self.packageInfo[allinfo.split(' ')[0]] = {}
			self.packageInfo[allinfo.split(' ')[0]]['raw'] = ' '.join(allinfo.split(' ')[1:])

		for package in self.packageInfo:
			raw = self.packageInfo[package]['raw'].split(' ')
			if raw[0].startswith('['):
				self.packageInfo[package]['install'] = raw[0][1:-1]
				self.packageInfo[package]['candidate'] = raw[1][1:]
				for item in raw:
					if item.endswith(')'):
						self.packageInfo[package]['architecture']=item[1:-1][:-1]
						
			elif raw[0].startswith('('):
				self.packageInfo[package]['install'] = None
				self.packageInfo[package]['candidate'] = raw[0][1:]
				for item in raw:
					if item.endswith(')'):
						self.packageInfo[package]['architecture']=item[1:-1][:-1]

			self.packageInfo[package].pop('raw')
		
		return self.packageInfo

	#def getPackagesToUpdate
		
	def checkIncorrectFlavours(self):
		
		self.incorrectFlavours=[]
		otherFlavours=[]
		count=0
		stopMeta=True
		errorFlavours=['edu','live']

		for item in self.packageInfo:
			if item in self.flavourReference:
				self.incorrectFlavours.append(item)

		if len(self.incorrectFlavours)>0:
			if len(self.flavours)>0:
				if len(self.flavours)==1 and self.flavours[0] in errorFlavours:
					stopMeta=False

			if stopMeta:	
				for item in self.incorrectFlavours:
					if len(self.targetMetapackage)>0:
						if item not in self.targetMetapackage:
							count=count+1
							otherFlavours.append(item)

					else:
						metaSplit=item.split("-")
						meta=metaSplit[2]
						if len(metaSplit)==4:
							meta=meta+"-"+metaSplit[3]
								
						if 'None' in self.previousFlavours:
							if not meta in self.metapackageRef:
								count=count+1
								otherFlavours.append(meta)

						else:		
							if not meta in self.previousFlavours:
								count=count+1
								otherFlavours.append(meta)

		if count>0:
			return {"status":True,"data":otherFlavours}
		else:
			return {"status":False,"data":otherFlavours}	

	#def checkIncorrectFlavours

	def distUpgradeProcess(self):
	
		return 'apt-get dist-upgrade --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages'

	#def distUpgradeProcess

	def checkErrorDistUpgrade(self):

		countPostaction=0
		countMetapackage=0
		error=False
		errorDetails=""
		lines=""
		pkgsNotInstalled=[]

		if os.path.exists(self.errorPostActionToken):
			aux = open(self.errorPostActionToken,'r')
			lines = aux.readlines()
			for x in lines:
				if 'E: ' in x:
					countPostaction=countPostaction+1
			aux.close()

		if countPostaction==0:

			if os.path.exists(self.errorFinalMetapackageToken):
				aux = open(self.errorFinalMetapackageToken,'r')
				lines = aux.readlines()
				for x in lines:
					if 'E: ' in x:
						countMetapackage=countMetapackage+1
				aux.close()
			if countMetapackage==0:
				
				cmd='dpkg -l | grep "^i[^i]" >' + self.errorUpgradeToken
				os.system(cmd)
			
				if os.path.exists(self.errorUpgradeToken):
					aux = open(self.errorUpgradeToken,'r')
					lines = aux.readlines()
					aux.close()
				
					if len(lines)>0:
						error=True
						errorDetails="There are packages that have not been configured correctly. Details: "+str(lines)
						
					else:
						j=0
						cmd='apt-get dist-upgrade -sV >' + self.finalUpgradeToken
						os.system(cmd)
						if os.path.exists(self.finalUpgradeToken):
							aux = open(self.finalUpgradeToken,'r')
							lines = aux.readlines()
							aux.close()

							for x in lines:
								if 'Inst' in x:
									j=j+1
									pkgsNotInstalled.append(x)
							if j>0:
								error=True
								errorDetails="There are packages that have not been updated/installed. Details: "+str(pkgsNotInstalled)
			else:
				error=True
				errorDetails="Error when installing metapackage. Details: "+str(lines)					
		else:
			error=True
			errorDetails="Error when running Postactions.Details: "+str(lines)

		return [error,errorDetails]	

	#def checkErrorDistUpgrade	

	def installFinalFlavour(self,flavourToInstall):

		tmpList=""
		for item in flavourToInstall:
			tmpList=tmpList+item +" "
		
		return 'apt-get install ' + tmpList + ' --yes  --allow-downgrades --allow-remove-essential --allow-change-held-packages'		
      	
	#def installFinalFlavour

	def get_process_list(self):
		
		self.process_list=[]
		
		p=subprocess.Popen(["ps","aux"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]
		
		if type(output) is bytes:
			output=output.decode()

		lst=output.split("\n")
		lst.pop(0)
		
		for item in lst:
			processed_line=item.split(" ")
			tmp_list=[]
			
			if len(processed_line) >= 10:
				for object in processed_line:
					if object!="":
						tmp_list.append(object)
				processed_line=tmp_list
				
				process={}
				process["user"]=processed_line[0]
				process["pid"]=processed_line[1]
				process["cpu"]=processed_line[2]
				process["mem"]=processed_line[3]
				process["vsz"]=processed_line[4]
				process["rss"]=processed_line[5]
				process["tty"]=processed_line[6]
				process["stat"]=processed_line[7]
				process["start"]=processed_line[8]
				process["time"]=processed_line[9]
				cmd=""
				for line in processed_line[10:]:
					if cmd!="":
						cmd+=" "
					cmd+=line
					
				process["command"]=cmd.split(" ")[0]
				self.process_list.append(process)

	#def get_process_list			

	def find_process(self,filter):
		
		self.get_process_list()
		ret_list=[]
		for process in self.process_list:
			if filter in process["command"]:
				ret_list.append(process)
				
				
		if len(ret_list)>0:
			return ret_list
		else:
			return None

	#def find_process	

	def searchMeta(self,meta):

		metaList=list(self.targetMetapackage)
		metaList.extend(x for x in self.previousFlavours if x not in metaList)
		metaList.extend(x for x in self.metapackageRef if x not in metaList)
		metaList.extend(x for x in self.flavours if x not in metaList)
		match=False
		for item in metaList:
			if meta in item:
				match=True
				break

		return match
	
	#def searchMeta

	def isAutoUpgradeAvailable(self):

		check=False

		if not self.searchMeta("adi"):
			if not self.connectionWithADI:
				check=True
		else:
			check=True

		if check:
			if os.path.exists(self.autoUpgradeService):
				return True
			else:
				return False
		else:
			return False

	#def isAutoUpgradeAvailable

	def isAutoUpgradeEnabled(self):

		try:
			result = self.n4d.is_auto_update_enabled('','LliurexUpManager')
			return result['return']
		except:
			return False
	
	#def isAutoUpgradeEnabled

	def isAutoUpgradeRun(self):

		try:
			result = self.n4d.is_auto_update_running('','LliurexUpManager')
			return result['return']
		except:
			return True

	#def isAutoUpgradeRun

	def isAutoUpgradeActive(self):

		try:
			result = self.n4d.is_auto_update_active('','LliurexUpManager')
			return result['return']
		except:
			return False

	#def isAutoUpgradeActive 	

	def manageAutoUpgrade(self,enable):

		try:
			with open('/etc/n4d/key','r') as fd:
				n4dKey=fd.readlines()[0].strip()

			result=self.n4d.manage_auto_update_service(n4dKey,"LliurexUpManager",enable)

			if result['return'] and not enable:
				return self.stopAutoUpgrade()
			else:
				return result['return']

		except:
			return False

	#def manageAutoUpgrade

	def stopAutoUpgrade(self):

		if self.isAutoUpgradeAvailable():
			try:
				result = self.n4d.stop_auto_update_service('','LliurexUpManager',True)
				return result['return']
			except:
				return True
		
		return True

	#def stopAutoUpgrade

#def LliurexUpCore

if __name__ == '__main__':
	x = LliurexUpCore()
