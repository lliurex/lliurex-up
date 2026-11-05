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
		self.errorPostactionToken = self.processPath / "errorPostactionToken"
		self.errorFinalMetapackageToken = self.processPath / "errorFinalMetapackageToken"
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
		self.retryN4d = True
		self.n4dStatus = True
		
		self.checkN4dStatus()
		
		self.metapackageRef=[]
		self.previousFlavours = []

		self.getTargetMetapackage()
		self.flavours = []
		self.lastFlavours = []
		self.getPreviousFlavours()

		self.retryN4d = True
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
		 	 
		if len(self.previousFlavours) == 0:
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
		
		textsearch_lliurex = f"/lliurex.net/{defaultVersion}"
		textsearch_lliurex_2 = f"/lliurex.gva.es/{defaultVersion}"	

		if self.origsourcesfile.exists():
			lines = self.origsourcesfile.read_text().splitlines()
		
			for line in lines:
				hasLliurex = textsearch_lliurex in line or textsearch_lliurex_2 in line
				if  not hasLliurex:
					extrasources.append(line.strip())
				
			if len(extrasources) > 0:
				self.sourcesListToUpdate.write_text("\n".join(extrasources)+"\n")
				
		self.optionsToUpdate = f"-o Dir::Etc::sourcelist={self.sourcesListToUpdate}"
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
			command.extend(options.split())

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
			command.extend(options.split())

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
		"""
			return Boolean 
		"""
		
		sourceslistDefaultPath = self.sourcesListLliurexTemplate
	
		self.optionsLlxUp = f"-o Dir::Etc::sourcelist={sourceslistDefaultPath} -o Dir::Etc::sourceparts=/dev/null"
		
		self.updateCacheApt(self.optionsLlxUp)
		result = self.getPackageVersionAvailable("lliurex-up",self.optionsLlxUp)

		if result.get("installed") != result.get("candidate"):
			return False
		
		return True

	#def isLliurexUpIsUpdated	

	def installLliurexUp(self):
		"""
			Args :
				options String
			return dictionary => result
			result : {'returncode':Int,'stdout':String,'stderr':String}

			options are Apt options
			

			This function install lliurex-up
		"""
		self.updateCacheApt(self.optionsLlxUp)

		env = os.environ.copy()
		env["LANG"] = "C"
		env["LANGUAGE"] = "en"
		env["DEBIAN_FRONTEND"] = "noninteractive"

		command = [
			"apt-get", 
			"install", 
			"--allow-downgrades",
			"--allow-remove-essential",
			"--allow-change-held-packages",
			"--yes",
			"lliurex-up"
		]

		command.extend(self.optionsLlxUp.split())

		result=subprocess.run(
			command,
			env=env,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)

		return {
			"returncode":result.returncode,
			"stdout": result.stdout,
			"stderr": result.stderr
		}

	#def installLliurexUp	
	
	def checkFlavour(self,args=None):
		"""
			return None|String
			If metapackages has been uninstalled, this function return 
			package to must install. If return None, you are ok and don't need 
			install anything.
		"""
		self.updateFlavoursList(args)
		targetMetapackage = []
				
		if args == None:
			recoveryMeta=False
			if 'None' in self.flavours:
				recoveryMeta = True
	
			if recoveryMeta:
				command = ["lliurex-version","--history"]
				result = subprocess.run(
					command,
					stdout=subprocess.PIPE,
					stderr=subprocess.DEVNULL,
					text=True
					)
				if result.stdout:
					history = [ x.strip().split('\t')[0].strip() for x in result.split('\n') if x.strip()]
					history = [ x for x in history if not 'lliurex-meta-live' in x ]
					for x in reversed(history):
						if x.startswith('-'):
							if x[2:] in self.flavourReference:
								targetMetapackage.append(x[2:])
								break

			if len(targetMetapackage) > 0:
				self.saveTargetMetapackage(targetMetapackage)				
			
			return targetMetapackage
		
		else:
			if 'None' in self.lastFlavours:
				if 'None' in self.flavours:
					if 'None' not in self.previousFlavours:
						targetMetapackage = list (set(targetMetapackage+self.previousFlavours))
					if 'None' not in self.metapackageRef:
						targetMetapackage = list(set(targetMetapackage+self.metapackageRef))
				else:
					targetMetapackage=self.flavours
					if 'None' not in self.previousFlavours:
						targetMetapackage=list(set(targetMetapackage+self.previousFlavours))
					if 'None' not in self.metapackageRef:	
						targetMetapackage=list(set(targetMetapackage+self.metapackageRef))
			else:
				tmp = []

				if 'None' in self.flavours:
					if 'None' not in self.previousFlavours:
						tmp = list(set(tmp+self.previousFlavours))
					if 'None' not in self.metapackageRef:
						tmp = list(set(tmp+self.metapackageRef))
				else:
					if 'None' not in self.previousFlavours:
						tmp = list(set(tmp+self.previousFlavours))
					if 'None' not in self.metapackageRef:
						tmp  =list(set(tmp+self.metapackageRef))
				
				targetMetapackage=list(set(tmp)-set(self.lastFlavours))
			
			tmp_list = []

			for item in targetMetapackage:
				if item not in ['edu','live']:
					meta_name = item if "lliurex-meta" in  item else f"lliurex-meta-{item}"
					tmp_list.append(meta_name)	
			
			return tmp_list		

	#def checkFlavour	

	def canConnectToLliurexNet(self):
		
		"""
			return dictionary => result
			result : {'status':bool,'data':String}
		"""
		try:
			with urllib.request.urlopen(self.defaultUrltoCheck,timeout=15) as res:
				statusCode=res.getcode()
				return {"status":True,"data":str(statusCode)}
		except Exception as e:
			return {"status":False,"data":str(e)}

	#def canConnectToLliurexNet		
				
	def getLliurexVersionLliurexNet(self):
		
		"""
			return dictionary => result
			result : {'installed':String,'candidate':String}
		"""
		sourceslistDefaultPath = self.sourcesListLliurexTemplate
		options = ""

		if self.canConnectToLliurexNet().get("status"):
			options = f"-o Dir::Etc::sourcelist={sourceslistDefaultPath} -o Dir::Etc::sourceparts=/dev/null"
		
		self.updateCacheApt(options)
		
		return self.getPackageVersionAvailable('lliurex-version-timestamp',options)

	#def getLliurexVersionLliurexNet	
	
	def getLliurexVersionLocal(self):
		
		self.updateCacheApt(self.optionsToUpdate)
		
		return self.getPackageVersionAvailable('lliurex-version-timestamp',self.optionsToUpdate,True)

	#def getLliurexVersionLocal

	def initActionsScript(self,arg):
		
		return ["run-parts", f"--arg={arg}", self.initActionsPath]

	#def initActionsScript

	def preActionsScript(self):
		
		return f'run-parts --arg="preActions" {self.preActionsPath}'

	#def preActionsScript

	def postActionsScript(self):
		
		return f'run-parts --arg="postActions" {self.postActionsPath}'
		
	#def postActionsScript

	def installInitialFlavour(self,flavourToInstall):
		
		"""
			Args :
				flavourToInstall String
				options String
			return dictionary => result
			result : {'returncode':Int,'stdout':String,'stderr':String}

			options are Apt options
			

			This function install lliurex-up
		"""

		self.updateCacheApt(self.optionsToUpdate)

		env = os.environ.copy()
		env["LANG"] = "C"
		env["LANGUAGE"] = "en"
		env["DEBIAN_FRONTEND"] = "noninteractive"

		command = [
			"apt-get",
			"install",
			"--yes",
			"--allow-downgrades",
			"--allow-remove-essential",
			"--allow-change-held-packages"
		]

		if isistance(flavourToInstall):
			command.extend(flavourToInstall.split())

		command.extend(self.optionsToUpdate.split())

		result = subprocess.run(
			command,
			env=env,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)

		if result.returncode != 0:
			fixCommand=[
				"apt-get","install","-f",
				"--yes",
				"--allow-downgrades",
				"--allow-remove-essential",
				"--allow-change-held-packages"
			]

			fixCommand.extend(self.optionsToUpdate.split())

			result = subprocess.run(
				command,
				env=env,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True
			)

		return {'returncode':result.returncode,'stdout':result.stdout,'stderrs':result.stderr}	

	#def installInitialFlavour

	def getPackagesToUpdate(self):

		"""
			packageInfo definition
			{
				'PACKAGENAME' : {
						'install' : 'INSTALLEDVERSION',
						'candidate' : 'CANDIDATEVERSION',
						'icon' : 'ICONNAME',
						'changelog' : 'CHANGELOGTEXT'
				}
			}
		"""

		self.packageInfo = {}
		self.updateCacheApt(self.optionsToUpdate)

		env = os.environ.copy()
		env["LANG"] = "C"
		env["LANGUAGE"] = "en"

		command=[
			"apt-get",
			"dist-upgrade",
			"-sV"
		]

		command.extend(self.optionsToUpdate.split())

		result = subprocess.run(
			command,
			env=env,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)

		for line in result.stdout.splitlines():
			stripedLine=line.strip()
			if stripedline.startswith("Inst"):
				parts=stripedline[5:].split()
				if not parts:
					continue

				packageName = parts[0]
				raw = parts[1:]

				if not raw:
					continue

				self.packageInfo[packageName] = {}

				if raw[0].startswith("["):
					self.packageInfo[packageName]["install"] = raw[0][1:-1]
					self.packageInfo[packageName]["candidate"] = raw[1][1:] if len(raw) > 1 else ""

					for item in raw:
						if item.endswith(")"):
							self.packageInfo[packageName]["architecture"] = item.strip("() ")

				elif raw[0].startswith("("):
					self.packageInfo[packageName]["install"] = None
					self.packageInfo[packageName]["candidate"] = raw[0][1:]

					for item in raw:
						if item.endswith(")"):
							self.packageInfo[packageName]["architecture"] = item.strip("() ")


		return self.packageInfo

	#def getPackagesToUpdate
		
	def checkIncorrectFlavours(self):
		
		self.incorrectFlavours = []
		otherFlavours = []
		count = 0
		stopMeta = True
		errorFlavours = ['edu','live']
	
		for item in self.packageInfo:
			if item in self.flavourReference:
				self.incorrectFlavours.append(item)

		if len(self.incorrectFlavours) > 0:
			if len(self.flavours) == 1 and self.flavours[0] in errorFlavours:
				stopMeta=False
			
			if stopMeta:	
				for item in self.incorrectFlavours:
					if len(self.targetMetapackage) > 0:
						if item not in self.targetMetapackage:
							count +=1
							otherFlavours.append(item)

					else:
						metaSplit=item.split("-")
						if len(metaSplit) >= 3:
							meta = metaSplit[2]
							if len(metaSplit) == 4:
								meta=f"{meta}-{metaSplit[3]}"
						else:
							meta = item

						if 'None' in self.previousFlavours:
							if meta not  in self.metapackageRef:
								count +=1
								otherFlavours.append(meta)

						else:		
							if meta not  in self.previousFlavours:
								count +=1
								otherFlavours.append(meta)

		return {"status":count > 0,"data":otherFlavours}

	#def checkIncorrectFlavours

	def distUpgradeProcess(self):
	
		return f'apt-get dist-upgrade --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages {self.optionsToUpdate}'

	#def distUpgradeProcess

	def checkErrorDistUpgrade(self):

		countPostaction = 0
		countMetapackage = 0
		error = False
		errorDetails = ""
		lines = ""
		pkgsNotInstalled = []

		if self.errorPostactionToken.exits():
			lines = self.errorPostactionToken.read_text().splitlines()
			for x in lines:
				if 'E' in x:
					countPostaction +=1

		if countPostaction==0:

			if self.errorFinalMetapackageToken.exists():
				lines = self.errorFinalMetapackageToken.read_text().splitlines()
				for x in lines:
					if 'E' in x:
						countMetapackage+=1

			if countMetapackage==0:

				result = subprocess.run(
					["dpkg","-l"],
					stdout=subprocess.PIPE,
					stderr=subprocess.DEVNULL,
					text=True	
				)

				unconfiguredPkgs = [
					line for line in result.stdout.splitlines()
					if line.startswith("i") and len(line) > 1 and line[1] != "i"
				]

				if unconfiguredPkgs:
					self.errorupgrade_token.write_text("\n".join(unconfiguredPkgs) + "\n")
					error = True
					errorDetails=f"There are packages that have not been configured correctly. Details: {unconfiguredPkgs}"
						
				else:
					env = os.environ.copy()
					env["LANG"] = "C"
					env["LANGUAGE"] = "en"

					command=["apt-get","dist-upgrade","-sv"]
					command.extend(self.optionsToUpdate)

					result=subprocess.run(
						command,
						env=env,
						stdout=subprocess.PIPE,
						stderr=subprocess.PIPE
					)

					if result.stdout:
						self.finalupgrade_token.write_text(result.stdout)

					for line in result.stdout.splitlines():
						if 'Ins' in line:
							pkgsNotInstalled.append(line)

					if len(pkgsNotInstalled) > 0:
						error = True 
						errorDetails=f"There are packages that have not been updated/installed. Details: {pkgsNotInstalled}"
			else:
				error = True
				errorDetails = f"Error when installing metapackage. Details: {lines}"					
		else:
			error = True
			errorDetails = f"Error when running Postactions.Details: {lines}"

		return {"status":error,"data":errorDetails}

	#def checkErrorDistUpgrade	

	def installFinalFlavour(self,flavourToInstall):

		commandParts = [
			"apt-get","install",
		]
		commandParts.extend(flavourToInstall)
		commandParts.extend([
			"--yes",
			"--allow-downgrades",
			"--allow-remove-essential",
			"--allow-change-held-packages"
		])

		commandParts.extend(self.optionsToUpdate)

		return " ".join(command_parts)
		
	#def installFinalFlavour

	def getProcessList(self):
		
		self.processList=[]

		result = subprocess.run(
			["ps","aux"],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)

		if not result.stdout:
			return

		lines = result.stdout.splitlines()

		if len(lines) <= 1:
			return

		lines.pop(0)

		for item in lines:
			processedLine = item.split()
			if len(processedLine) >= 11:
				process = {
					"user":processedLine[0],
					"pid":processedLine[1],
					"cpu":processedLine[2],
					"mem":processedLine[3],
					"vsz":processedLine[4],
					"rss":processedLine[5],
					"tty":processedLine[6],
					"stat":processedLine[7],
					"start":processedLine[8],
					"time":processed_line[9],
					"command":" ".join(processedLine[10:])
				}

				self.processList.append(process)

	#def getProcessList			

	def findProcess(self,processFilter):
		
		self.getProcessList()

		retList = []
		
		for process in self.processList:
			if processFilter in process.get("command"):
				retList.append(process)
				
				
		if len(retList)>0:
			return retList
		else:
			return None

	#def findProcess	

	def searchMeta(self,meta):

		metaList=list(set(
			self.targetMetapackage + 
			self.previousFlavours + 
			self.metapackageRef +
			self.flavours
		))

		return any(meta in item for item in metaList)
		
	#def searchMeta

	def isUserAdmin(self):
		
		isAdmin=False

		try:
			pkexec_uid = os.environ["PKEXEC_UID"]
			if pkexec_uid is None:
				return False

			user = pwd.getpwuid(int(pkexec_uid)).pw_name
			gid = pwd.getpwnam(user).pw_gid
			groupsGids = os.getgrouplist(user, gid)
			userGroups = [ grp.getgrgid(x).gr_name for x in groupsGids ]

			if 'sudo' in userGroups or 'admins' in userGroups:
				isAdmin=True

		except Exception as e:
			return False

		return isAdmin

	#def isUserAdmin

	def flatpakActionsScript(self):
		
		return f'run-parts --arg="flatpakActions" {flatpakActionsPath}'

		
	#def flatpakActionsScript

	def getFlatpakUpdateInfo(self):
		
		totalFlatpak = 0
		totalSize = "0"
		commnand=["flatpak","update"]

		result = subprocess.run(
			command,
			input="\n\n",
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
			)

		if result.stdout:
			lines = result.stdout.splitlines()
			for line in lines:
				stripedline = line.split().replace('\xa0',' ').replace(",",".")

				if not stripedline or "ID" in stripedline or "Proceed with these changes" in stripedline:
					continue

				parts = stripedline.split()

				for i in range(len(parts) -1 ):
				 	item = parts[i]
				 	nextItem = parts[i + 1].upper()
				 	if nextItem in ["B","KB","MB","GB"]:
				 		try:
				 			tmpSize = float(item)
				 			if "KB" in nextItem:
				 				sizeItem = tmpSize*1024
				 			elif "MB" in nextItem:
				 				sizeItem = tmpSize*1024*1024
				 			elif "GB" in nextItem:
				 				sizeItem = tmpSize*1024*1024*1024
				 			else:
				 				sizeItem = tmpSize

				 			sizeToUpdate += sizeItem
				 			totalFlatpak +=1
				 			break

				 		except ValueError:
				 			continue

			if sizeToUpdate > 0:
				totalSize = self._convertSize(sizeToUpdate)

				
		return {"totalFlatpak":totalFlatpak,"size":totalSize}
	
	#def getFlatpakUpdateInfo
						
	def _convertSize(self,sizeBytes):

		if sizeBytes == 0:
			return "0 B"

		sizeName = ("B", "KB", "MB", "GB")
		i = int(math.floor(math.log(sizeBytes, 1024)))
		i = min(i,len(sizeName) - 1)
		
		p = math.pow(1024, i)
		s = int(round(sizeBytes/p,))

		return f"{size} {sizeName[i]}"

	#def convertSize

#def LliurexUpCore

if __name__ == '__main__':
	x = LliurexUpCore()
