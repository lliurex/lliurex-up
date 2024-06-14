 
import os
import subprocess
import n4d.server.core as n4dcore
import n4d.responses


class LliurexUpManager:

	def __init__(self):

		self.enabledAutoUpgradeToken="/etc/systemd/system/multi-user.target.wants/lliurex-up-auto-upgrade.service"
		self.lliurexUpAutoToken="/var/run/lliurex-up-auto.token"
		self.lliurexUpAutoRunToken="/var/run/lliurex-up-auto.lock"

	#def __init__

	def manage_auto_update_service(self,enable):
		
		result=True
		if enable:
			if not os.path.exists(self.enabledAutoUpgradeToken):
				cmd="systemctl enable lliurex-up-auto-upgrade.service"
				p=subprocess.run(cmd,shell=True,check=True)
				returnCode=p.returncode
				if returnCode!=0:
					if os.path.exists(self.enabledAutoUpgradeToken):
						result=True
					else:
						result=False
				else:
					result=True
			else:
				result=True
					
		else:
			if os.path.exists(self.enabledAutoUpgradeToken):
				cmd="systemctl disable lliurex-up-auto-upgrade.service"
				p=subprocess.run(cmd,shell=True,check=True)
				returnCode=p.returncode
				if returnCode!=0:
					if not os.path.exists(self.enabledAutoUpgradeToken):
						result=True
					else:
						result=False
				else:
					result=True
			else:
				result=True

		return n4d.responses.build_successful_call_response(result)	

	#def manage_auto_update_service 
			
	def stop_auto_update_service(self):

		result=True

		if not os.path.exists(self.lliurexUpAutoRunToken):
			cmd="systemctl stop lliurex-up-auto-upgrade.service"
			p=subprocess.run(cmd,shell=True,check=True)
			returnCode=p.returncode

			if returnCode==0:
				if os.path.exists(self.lliurexUpAutoToken):
					os.remove(self.lliurexUpAutoToken)
			else:
				result=False

		return n4d.responses.build_successful_call_response(result)	
	
	#def stop_auto_update_service

	def is_auto_update_active(self):

		result=False

		cmd="systemctl is-active lliurex-up-auto-upgrade.service"
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		pout=p.communicate()[0].decode().strip()

		if pout=="active":
			result=True

		return n4d.responses.build_successful_call_response(result)	
	
	#def is_auto_update_active

	def is_auto_update_enabled(self):

		result=False

		if os.path.exists(self.enabledAutoUpgradeToken):
			result=True

		return n4d.responses.build_successful_call_response(result)	

	#def is_auto_update_enabled

	def is_auto_update_running(self):

		result=False

		if os.path.exists(self.lliurexUpAutoRunToken):
			result=True

		return n4d.responses.build_successful_call_response(result)	
	
	#def is_auto_update_running	

#def LliurexUpManager
	
