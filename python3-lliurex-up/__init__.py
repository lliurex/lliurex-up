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
import datetime
import pwd
import grp
import math

from pathlib import Path


class LliurexUpCore(object):
	"""docstring for LliurexUpCore"""
	def __init__(self):
		super(LliurexUpCore, self).__init__()
		self.flavourReference = ["lliurex-meta-desktop"]
		self.versionReference = ["desktop","None"] 
		self.defaultVersion = "noble"
		self.defaultUrltoCheck = "http://lliurex.gva.es/noble"
		self.lockTokenPath=Path("/var/run/lliurexUp.lock")
		self.processPath = Path("/var/run/lliurex-up")
		self.sourcesListPath= Path("/etc/apt")
		self.changelogsPath = self.processPath /'changelogs'
		self.origsourcesfile = self.sourcesListPath / "sources.list"
		self.sourcesListToUpdate = self.processPath / "lliurexup_sources.list"
		self.targetMetapackagePath = self.processPath / "targetMetapackage"
		self.previousflavourspath = self.processPath / "previousflavours"
		self.errorpostaction_token = self.processPath / "errorpostaction_token"
		self.errorfinalmetapackage_token = self.processPath / "errorfinalmetapackage_token"
		self.errorupgrade_token = self.processPath / "errorupgrade_token"
		self.finalupgrade_token = self.processPath / "finalupgrade_token"

		self.initActionsPath = Path("/usr/share/lliurex-up/initActions")
		self.preActionsPath = Path("/usr/share/lliurex-up/preActions")
		self.postActionsPath = Path("/usr/share/lliurex-up/postActions")
		self.optionsLlxUp =""
		self.dpkgUnlocker = DpkgUnlockerManager.DpkgUnlockerManager()
		context=ssl._create_unverified_context()
		self.n4d = n4dclient.ServerProxy('https://localhost:9779',context=context,allow_none=True)
		self.sourcesListDPath = self.sourcesListPath / "sources.list.d"
		self.sourcesListLliurexTemplate = Path("/usr/share/lliurex-up/templates/lliurex.sources")
		self.optionsToUpdate = ""
		self.flatpakActionsPath = Path("/usr/share/lliurex-up/flatpakActions")
	
	#def __init__	

	def startLliurexUp(self):

		self.createLockToken()
		self.retryN4d=True
		self.n4dStatus=True
		
		self.checkN4dStatus()
		
		self.metapackageRef=[]
		self.previousFlavours = []

		self.getTargetMetapackage()
		self.flavours = []
		self.lastFlavours=[]
		self.getPreviousFlavours()

		self.retryN4d=True
		self.prepareEnvironment()

	#def startLliurexUp	

	def checkLocks(self):

		self.locks_info=self.dpkgUnlocker.checkingLocks()

	#def checkLocks
	
	def isLliurexUpLocked(self):

		"""
		 0: Lliurex-Up is not running
		 1: Lliurex-Up is running
		 2: Lliurex-Up is locked for previous failed process
		""" 

		return self.locks_info.get("Lliurex-Up")

	#def isLliurexUpLocked		

	def isAptLocked(self):

		"""
		 0: Apt is not running
		 1: Apt is running
		 2: Apt is locked for previous failed process
		"""
		return self.locks_info.get("Apt")	

	#def isAptLocked
		
	def isDpkgLocked(self):

		"""
		 0: Dpkgis not running
		 1: Dpkg is running
		 2: Dpkg is locked for previous failed process
		 3: Apt is running
		
		""" 
		return self.locks_info.get("Dpkg")		
			
	#def isAptLocked			

	def unlockerCommand(self):

		return "/usr/sbin/dpkg-unlocker-cli unlock -u"

	#def unlockeCommand				

	def createLockToken(self):

		if not self.lockTokenPath.exists():
			self.lockTokenPath.write_text(str(os.getpid()))

	#def createLockToken		

	def getPreviousFlavours(self):
		
		if self.previousflavourspath.exists():
			lines = self.previousflavourspath.read_text().splitlines()
			self.previousFlavours.extend(line.strip() for line in lines if line.strip())

	#def getPreviousFlavours		

	def checkN4dStatus(self):

		canRetry = self.retryN4d

		while True:
			try:
				self.n4d.get_methods()
				self.n4dStatus = True
				return
			except Exception:
				if canRetry:
					self.retryN4d = False
					canRetry = False
					try: 
						result = subprocess.run(
							['systemctl','restart','n4d.service'],
							stdout=subproces.DEVNULL,
							stderr=subprocess.DEVNULL
						)
						time.sleep(5)
						if result.returncode == 0:
							continue
					except Exception:
						pass
				
				self.n4dStatus = False
				return 
				
	#def checkN4dStatus		
			
	def getTargetMetapackage(self):

		if self.targetMetapackagePath.exists():
			lines = self.targetMetapackagePath.read_text().splitlines()
			self.metapackageRef.extend(line.strip() for line in lines if line.strip())

	#def getTargetMetapackage
			
	def saveTargetMetapackage(self,targetMetapackage):

		line = []

		for lines in targetMetapackage:
			parts = lines.split("-")
			if len(parts) > 2:
				lines.append(parts[2])

		lines.append("edu")

		self.targetMetapackagePath.write_text("\n".join(lines)+"\n")

	#def saveTargetMetapackage	

	def checkInitialFlavour(self,args=None):

		self.targetMetapackage = self.checkFlavour()
		
		if len(self.metapackageRef) == 0:
			self.getTargetMetapackage()
			
		self.metapackageRef = sorted(self.metapackageRef)	
		 	 
		if len(self.previousFlavours) ==0:
			self.getPreviousFlavours()
	
		self.checkFlavourType()
		self.testConnectionWithADI()
		
		return self.targetMetapackage

	#def checkInitialFlavour	
		
	def updateFlavoursList(self,args=None):

		result = subprocess.run(
			["lliurex-version", "-v" ],
			stdout=subprocess.PIPE,
			stderr=subprocess.DEVNULL,
			text=True
			)

		targetList = self.lastFlavours if args is not None else self.flavours

		for item in result.stdout.split(","):
			flavour = item.strip()

			if flavour in ["edu", "live"]:
				continue

			if flavour not in targetList and flavour in self.versionReference:
				targetList.append(flavour)

		if args is None and len(self.flavours) > 0:
			self.previousflavourspath.write_text("\n".join(self.flavours)+"\n")
		
	#def updateFlavoursList		

	def prepareEnvironment(self):
		"""
			This funcion delete all environment and rebuild environment

		"""
		self.cleanEnvironment()
		self.processPath.mkdir(parents=True,exist_ok=True)
		self.changelogsPath.mkdir(parents=True,exist_ok=True)

	#def prepareEnvironment	

	def addSourcesListLliurex(self,args=None):
		
		newsourcesfile = ""
		extrasources = []
		
		textsearch_lliurex=f"/lliurex.net/{defaultVersion}"
		textsearch_lliurex_2=f"/lliurex.gva.es/{defaultVersion}"	

		if self.origsourcesfile.exists():
			lines = self.origsourcesfile.read_text().splitlines()
		
			for line in lines:
				hasLliurex = textsearch_lliurex in line or textsearch_lliurex_2 in line
				if  not hasLliurex:
					extrasources.append(line.strip())
				
			if len(extrasources)>0:
				self.sourcesListToUpdate.write_text("\n".join(extrasources)+"\n")
				
		self.optionsToUpdate=f"-o Dir::Etc::sourcelist={self.sourcesListToUpdate}"
		self._addSourcesListTemplate()

	#def addSourcesListLliurex 		

	def _addSourcesListTemplate(self):

		if self.sourcesListLliurexTemplate.exists():
			shutil.copy(self.sourcesListLliurexTemplate,self.sourcesListDPath)

	#def _addSourcesListTemplate

	def cleanEnvironment(self):

		if self.processPath.exists():
			shutil.rmtree(self.processPath)

	#def cleanEnvironment	

	def cleanLliurexUpLock(self):

		if self.lockTokenPath.exists():
			self.lockTokenPath.unlink(missing_ok=True)

	#def cleanLliurexUpLock		

	def updateCacheApt(self,options=""):

		env = os.environ.copy()

		env["LANG"] = "C"
		env["LANGUAGE"] = "en"

		command = ["apt-get","update","-y"]

		if options:
			command.extend(options)

		subprocess.run(
			command,
			env=env,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL
		)
	
	#def updateCacheApt	

	def getPackageVersionAvailable(self,package,options="",checkRepo=False):
		
		"""
			Args :
				package String
				options String

			return dictionary => result
			result : {'installed':String,'candidate':String}

			Options are Apt options 
		
		"""
		env = os.environ.copy()
		env["LANG"] = "C"
		env["LANGUAGE"] = "en"

		command = ["apt-cache", "policy", package]

		if options:
			command.extend(options)

		result = subprocess.run(
			command,
			env=env,
			stdout = subprocess.PIPE,
			stderr = subprocess.DEVNULL,
			text = True
		)

		installed = None
		candidate = None
		getRepo = False
		updateSource = None

		for line in result.stdout.splitlines():
			stripedline=line.strip()

			if stripedline.startswith("Installed:"):
				installed = stripedline.replace("Installed: ","").strip()
			elif stripedline.startswith("Candidate: "):
				candidate = stripedline.replace("Candidate: ", "").strip()

			if checkRepo and candidate is not None:
				if candidate in stripedline:
					getRepo = True

			if getRepo:
				if stripedline.startswith("666"):
					parts = stripedline.split()
					if len(parts) > 1:
						updateSource = parts[1]

					getRepo = False

		return {
			"installed": installed,
			"candidate": candidate,
			"updateSource": updateSource
		}

	#def getPackageVersionAvailable	

	def isLliurexUpIsUpdated(self,args=None):
		'''
			return Boolean 
		'''
		
		sourceslistDefaultPath = self.sourcesListLliurexTemplate

		if self.isDesktopInADI:
			if self.isMirrorInADI:
				sourceslistDefaultPath = self.sourcesListAllTemplate
	
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
		if self.haveLliurexMirror:
			if self.isADI:
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
		if self.haveLliurexMirror:
			if self.isADI:
				result = self.n4d.is_alive('','MirrorManager')
				return result['return']['status']
		return False

	#def lliurexMirrorIsRunning	

	def desktopCheckingMirrorIsRunning(self):

		if self.canConnectToADI:
			try:
				context=ssl._create_unverified_context()
				client=n4dclient.ServerProxy('https://server:9779',context=context,allow_none=True)
				result=client.is_alive('','MirrorManager')
				return {'ismirrorrunning':result['return']['status'],'exception':False,'data':result}
			except Exception as e:
				pass

		return {'ismirrorrunning':False,'exception':False,'data':""}	

	#def desktopCheckingMirrorIsRunning	

	def desktopCheckingMirrorExists(self):

		if self.canConnectToADI:	
			try:
				context=ssl._create_unverified_context()
				client=n4dclient.ServerProxy('https://server:9779',context=context,allow_none=True)
				result=client.is_mirror_available('','MirrorManager')
				if result['status']==0:
					self.isMirrorInADI=True
					return {'ismirroravailable':True,'exception':False,'data':result}
				else:
					return {'ismirroravailable':False,'exception':False,'data':result}
			except Exception as e :
				pass
		
		return {'ismirroravailable':True,'exception':False,'data':''}	

	#def desktopCheckingMirrorExists	

	def getPercentageLliurexMirror(self):
		'''
			return int | None
		'''
		if self.haveLliurexMirror:
			if self.isADI:
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
				# get last flavour
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
							if x[2:] in self.flavourReference:
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
					#tmp=[]
					tmp=self.flavours
					if 'None' not in self.previousFlavours:
						tmp=list(set(tmp+self.previousFlavours))
					if 'None' not in self.metapackageRef:
						tmp=list(set(tmp+self.metapackageRef))
				targetMetapackage=list(set(tmp)-set(self.lastFlavours))
			tmp_list=[]
			for item in targetMetapackage:
				if item not in ['edu','live']:
					if "lliurex-meta" not in item:
						tmp="lliurex-meta-"+item
					tmp_list.append(tmp)	
			
			return tmp_list		

	#def checkFlavour	

	def canConnectToLliurexNet(self):
		
		'''
			return dictionary => result
			result : {'status':bool,'data':String}
		'''
		try:
			res=urllib.request.urlopen(self.defaultUrltoCheck,timeout=15)
			return {'status':True,'data':str(res)}
		except Exception as e:
			return {'status':False,'data':str(e)}

	#def canConnectToLliurexNet		
				
	def getLliurexVersionLliurexNet(self):
		'''
			return dictionary => result
			result : {'installed':String,'candidate':String}
		'''
		sourceslistDefaultPath = os.path.join(self.sourcesListLliurexTemplate)
		options = ""
		if self.canConnectToLliurexNet()['status']:
			options = "-o Dir::Etc::sourcelist={sourceslistOnlyLliurex} -o Dir::Etc::sourceparts=/dev/null".format(sourceslistOnlyLliurex=sourceslistDefaultPath)
		self.updateCacheApt(options)
		
		return self.getPackageVersionAvailable('lliurex-version-timestamp',options)

	#def getLliurexVersionLliurexNet	
	
	def getLliurexVersionLocal(self):
		
		self.updateCacheApt(self.optionsToUpdate)
		
		return self.getPackageVersionAvailable('lliurex-version-timestamp',self.optionsToUpdate,True)

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
		tmp_list=""
		for item in flavourToInstall:
			tmp_list=tmp_list+item+" "
		self.updateCacheApt(self.optionsToUpdate)
		command = "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get install --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages " + tmp_list + "{options} ".format(options=self.optionsToUpdate)
		p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		poutput,perror = p.communicate()
		
		if p.returncode!=0:
			command = "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get install -f --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages {options} ".format(options=self.optionsToUpdate)
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
		self.updateCacheApt(self.optionsToUpdate)
		cmd='LANG=C LANGUAGE=en apt-get dist-upgrade -sV {options} '.format(options=self.optionsToUpdate)
		psimulate = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
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
				#self.packageInfo[package]['architecture']=raw[-1:][0][1:][:-2]
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
		
		self.incorrect_flavours=[]
		other_flavours=[]
		count=0
		stopMeta=True
		error_flavours=['edu','live']
		cdd_path="/usr/share/lliurex-cdd"
		count_cdd=0

		for item in self.packageInfo:
			if item in self.flavourReference:
				self.incorrect_flavours.append(item)

		if len(self.incorrect_flavours)>0:
			if len(self.flavours)>0:
				if len(self.flavours)==1 and self.flavours[0] in error_flavours:
					stopMeta=False
			
			if stopMeta:	
				for item in self.incorrect_flavours:
					if len(self.targetMetapackage)>0:
						if item not in self.targetMetapackage:
							count=count+1
							other_flavours.append(item)

					else:
						meta_split=item.split("-")
						meta=meta_split[2]
						if len(meta_split)==4:
							meta=meta+"-"+meta_split[3]
								
						if 'None' in self.previousFlavours:
							if not meta in self.metapackageRef:
								count=count+1
								other_flavours.append(meta)

						else:		
							if not meta in self.previousFlavours:
								count=count+1
								other_flavours.append(meta)

		if count>0:
			return {"status":True,"data":other_flavours}

		else:
			return {"status":False,"data":other_flavours}	

	#def checkIncorrectFlavours

	def distUpgradeProcess(self):
	
		return 'apt-get dist-upgrade --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages {options} '.format(options=self.optionsToUpdate)

	#def distUpgradeProcess

	def checkErrorDistUpgrade(self):

		countPostaction=0
		countMetapackage=0
		error=False
		error_details=""
		lines=""
		pkgs_not_installed=[]

		if os.path.exists(self.errorpostaction_token):
			aux = open(self.errorpostaction_token,'r')
			lines = aux.readlines()
			for x in lines:
				if 'E: ' in x:
					countPostaction=countPostaction+1
			aux.close()

		if countPostaction==0:

			if os.path.exists(self.errorfinalmetapackage_token):
				aux = open(self.errorfinalmetapackage_token,'r')
				lines = aux.readlines()
				for x in lines:
					if 'E: ' in x:
						countMetapackage=countMetapackage+1
				aux.close()
			if countMetapackage==0:
				
				cmd='dpkg -l | grep "^i[^i]" >' + self.errorupgrade_token
				os.system(cmd)
			
				if os.path.exists(self.errorupgrade_token):
					aux = open(self.errorupgrade_token,'r')
					lines = aux.readlines()
					aux.close()
				
					if len(lines)>0:
						error=True
						error_details="There are packages that have not been configured correctly. Details: "+str(lines)
						
					else:
						j=0
						cmd='apt-get dist-upgrade -sV {options} > {token}'.format(options=self.optionsToUpdate,token=self.finalupgrade_token)
						os.system(cmd)
						if os.path.exists(self.finalupgrade_token):
							aux = open(self.finalupgrade_token,'r')
							lines = aux.readlines()
							aux.close()

							for x in lines:
								if 'Inst' in x:
									j=j+1
									pkgs_not_installed.append(x)
							if j>0:
								error=True
								error_details="There are packages that have not been updated/installed. Details: "+str(pkgs_not_installed)
			else:
				error=True
				error_details="Error when installing metapackage. Details: "+str(lines)					
		else:
			error=True
			error_details="Error when running Postactions.Details: "+str(lines)

		return [error,error_details]	

	#def checkErrorDistUpgrade	

	def installFinalFlavour(self,flavourToInstall):

		tmp_list=""
		for item in flavourToInstall:
			tmp_list=tmp_list+item +" "
		
		return 'apt-get install ' + tmp_list + ' --yes  --allow-downgrades --allow-remove-essential --allow-change-held-packages ' + '{options}'.format(options=self.optionsToUpdate)

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

	def search_meta(self,meta):

		meta_list=list(self.targetMetapackage)
		meta_list.extend(x for x in self.previousFlavours if x not in meta_list)
		meta_list.extend(x for x in self.metapackageRef if x not in meta_list)
		meta_list.extend(x for x in self.flavours if x not in meta_list)
		match=False
		for item in meta_list:
			if meta in item:
				match=True
				break

		return match
	
	#def search_meta

	def isAutoUpgradeAvailable(self):

		if os.path.exists(self.autoUpgradeService):
			return True
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
		except Exception as e:
			return False

	#def isAutoUpgradeActive

	def canCancelAutoUpdate(self):

		try:
			result = self.n4d.can_cancel_auto_upgrade('','LliurexUpManager')
			return result['return']
		except Exception as e:
			return False

	#def canCancelAutoUpdate

	def getAutoUpgradeConfig(self):

		try:
			ret=self.n4d.read_current_config('','LliurexUpManager')["return"]

			if ret['status']:
				if len(ret['data']):
					self.cancellationsAvailables=ret['data']["cancellationsAvailables"]
					self.dateToUpdate=ret['data']["dateToUpdate"]
					self.weeksOfPause=ret['data']["weeksOfPause"]
					self.extensionPause=ret['data']["extensionPause"]
		except:
			pass
			
	#def getAutoUpgradeConfig	

	def manageAutoUpgrade(self,enable):

		try:
			with open('/etc/n4d/key','r') as fd:
				n4dKey=fd.readlines()[0].strip()

			result=self.n4d.manage_auto_update_service(n4dKey,"LliurexUpManager",enable)

			return result['return']

		except:
			return False

	#def manageAutoUpgrade

	def stopAutoUpgrade(self, restartConfig=True):

		if self.isAutoUpgradeAvailable():
			try:
				result = self.n4d.stop_auto_update_service('','LliurexUpManager',restartConfig)
				return result['return']
			except:
				return True
		
		return True

	#def stopAutoUpgrade

	def manageUpdatePause(self,enablePause,weeksOfPause):

		try:
			with open('/etc/n4d/key','r') as fd:
				n4dKey=fd.readlines()[0].strip()

			result=self.n4d.manage_auto_update_pause(n4dKey,"LliurexUpManager",enablePause,weeksOfPause)
			return result['return']

		except Exception as e:
			return False

	#def manageUpdatePause

	def isUserAdmin(self):
		
		isAdmin=False

		try:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			gid = pwd.getpwnam(user).pw_gid
			groupsGids = os.getgrouplist(user, gid)
			userGroups = [ grp.getgrgid(x).gr_name for x in groupsGids ]

			if 'sudo' in userGroups or 'admins' in userGroups:
				isAdmin=True

		except Exception as e:
			isAdmin=True

		return isAdmin

	#def isUserAdmin

	def checkFlavourType(self):

		if os.path.exists(self.adiServerRef):
			self.isADI=True
		else:
			if os.path.exists(self.adiClientRef):
				self.isDesktopInADI=True
		
	#def checkFlavourType

	def testConnectionWithADI(self):

		if self.isDesktopInADI:
			try:
				context=ssl._create_unverified_context()
				n4c=n4dclient.ServerProxy('https://server:9779',context=context,allow_none=True)
				ret=n4c.get_variable("LLIUREXMIRROR")
				self.canConnectToADI=True
			except Exception as e:
				self.canConnectToADI=False
				self.isDesktopInADI=False

	#def testConnectionWithADI

	def flatpakActionsScript(self):
		
		return 'run-parts --arg="flatpakActions" ' + self.flatpakActionsPath

		
	#def flatpakActionsScript

	def getFlatpakUpdateInfo(self):
		
		totalFlatpak=0
		totalSize="0"
		cmd=r"'n\n' 2>/dev/null | flatpak update | grep -Eo '^[\ ][0-9]*\.?+[\ ]*.*'"
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		pout=p.communicate()[0].decode().split("\n")
		if len(pout)>0:
			pout.pop(-1)
			sizeToUpdate=0
			for item in pout:
				try:
					tmpItem=item.split("\t")[6].split("<")[1]
					tmpSize=tmpItem.replace('\xa0',' ').split(" ")[1].strip().replace(",",".")
					if "kB" in tmpItem:
						sizeItem=float(tmpSize)*1024
					elif "MB" in tmpItem:
						sizeItem=float(tmpSize)*1024*1024
					elif "GB" in tmpItem:
						sizeItem=float(tmpSize)*1024*1024*1024
					else:
						sizeItem=float(tmpSize)

					totalFlatpak+=1
					sizeToUpdate=sizeToUpdate+sizeItem
				except:
					sizeItem=0
	
			if sizeToUpdate>0:
				totalSize=self._convertSize(sizeToUpdate)
				
		return [totalFlatpak,totalSize]
	
	#def getFlatpakUpdateInfo
						
	def _convertSize(self,sizeBytes):

		sizeName = ("B", "KB", "MB", "GB")
		i = int(math.floor(math.log(sizeBytes, 1024)))
		p = math.pow(1024, i)
		s = round(sizeBytes/p,)
		s=int(s)
		return '%s %s' % (s, sizeName[i])

	#def convertSize

#def LliurexUpCore

if __name__ == '__main__':
	x = LliurexUpCore()
