from netmiko import Netmiko
from pythonping import ping
from ndct.core.device import Device
from ndct.core.log import log

class Connection(Device):
	def __init__(self, name, ip, username, password, os):
		'''
		Takes: 
		ip: IP address of the device
		username: Username to authentication against
		password: Password to authenticate with
		os: Operating system of the device
		'''
		super().__init__(name, ip, username, password, os)

	def get_connection(self):
		'''
		Summary:
		Tests device connectivity then creates an SSH connection if successful.

		Returns:
		Connection object
		'''
		ping_result = ping(self.ip, count=1)

		if 'Request timed out' not in str(ping_result):
			log('[{}] Reachable, getting connection...'.format(self.name), 'info')

			connection = Netmiko(
				self.ip,
				username=self.username,
				password=self.password,
				device_type=self.os
			)

			log('[{}] Connected'.format(self.name), 'info')
			return connection
		else:
			log('[{}] Not reachable'.format(self.name), 'info')
			return

	def close_connection(self, connection):
		'''
		Summary:
		Closes an SSH connection to a device.

		Takes:
		connection: Connection object to close
		'''
		connection.disconnect()

		log('[{}] Disconnected'.format(self.name), 'info')