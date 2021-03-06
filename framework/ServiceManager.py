import time
import datetime
from Classes.dhl import dhl
from Classes.relaiscolis import relaiscolis
from Classes.parcel import parcel
from Classes.bpostEasyPlus import bposteasyplus
from Classes.couriier import couriier
from Classes.royalmail import royalmail
from Classes.hermes import hermes
from Classes.envialia import envialia
from Classes.pvs import pvs
from Classes.swisspost import swisspost
from Classes.ups import ups
from Classes.colissimo import colissimo
from Classes.gophr import gophr
from Classes.postnord import postnord
from Classes.shoprunback import shoprunback
class ServiceManager(object):
		
	def call_service(self, company, service, paramlist):
		selected_class = globals()[company]
		instance = selected_class()
		method = getattr(instance, service)
		return method(paramlist)


# README
# This class is a factory class that will decide which concrete class to create an instance and which function to call
# It use function call_service to convert string from parameter to a class and a method