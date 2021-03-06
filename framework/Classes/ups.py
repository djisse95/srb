from Classes.AbstractService import Service
from BuiltInService import requests 
from Modules.data_converter import data_converter as converter
from Modules.data_validator import Validator 
from Modules.network import networking as netw
from BuiltInService import xmltodict
import os
from random import randrange

import re
import time
import datetime
import xml.etree.ElementTree as ET
import json
import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection


date = datetime.datetime.now()
curdate = re.sub(r'\s.*','',str(date))

UPS_LABEL_URL = os.environ["UPS_LABEL_URL"] 
UPS_USERNAME =  os.environ["UPS_USERNAME"]
UPS_PASSWD = os.environ["UPS_PASSWD"]
UPS_ACCESSLICENCE_NUMBER  =  os.environ["UPS_ACCESSLICENCE_NUMBER"]
UPS_TRACK_URL = os.environ["UPS_TRACK_URL"]
UPS_STATUS_URL = os.environ["UPS_STATUS_URL"]

class ups(Service):
	"""docstring for envialia"""
	def root(self,userparamlist):
		true=True
		data={
			"/":{
				"get":true
			},
			"type":{
				"get":true
			},
			"label":{
				"post":true
			},
			"status":{
				"get":true
			},
			"tracking":{
				"get":true
			}
		}
		return data

	def type(self,paramlist):
		true=True
		false=False
		data={
			"type": "dropoff",
			"postal": false,
			"pickup": false,
			"dropoff": true,
			"linehaul": false
		}
		return data
	def status(self,paramlist):	
		paramlabel={
		  "origin": {
		    "name": "Test Type",
		    "first_name": "Ithyvan",
		    "last_name": "Schreys",
		    "phone": "0622889977",
		    "email": "eddy@shoprunback.com",
		    "company": "Company Origin",
		    "line1": "11 avenue de la habette",
		    "line2": "la habette",
		    "street_number": "212121",
		    "street_name":"test",
		    "state": "",
		    "zipcode": "94000",
		    "country": "France",
		    "country_code": "FR",
		    "city": "CRETEIL",
		    "place_description": "At home"
		  },
		  "destination": {
		    "name": "Client Base fulfilment ltd",
		    "shipment_id": "return_id_at_srb",
		    "first_name": "Leo",
		    "last_name": "Martin",
		    "company": "Company Destination",
		    "street_number": "121212",
		    "street_name":"test",
		    "line1": "Clientbase Fulfilment",
		    "line2": "Woodview Road",
		    "state": "IDF",
		    "zipcode": "TQ4 7SR",
		    "country": "France",
		    "country_code": "GB",
		    "phone": "07801123456",
		    "email": "tom.smith@royalmail.com",
		    "city": "PAIGNTON"
		  },
		  "parcel": {
		    "length_in_cm": 10,
		    "width_in_cm": 10,
		    "height_in_cm": 10,
		     "contents": "TESTS",
		    "weight_in_grams": 1950
		  },
		  "shipment_date": curdate,
		 
		  "shipment_id": "9999"
		}
		datadropoff={}
		paramtracking='FL067074022GB'
		objfunction=["root","type","label","tracking"]
		instance = Validator()
		api_url_request = os.environ["API_DEVEVELOPER_URL"]
		result = instance.get_all_status("ups",api_url_request,objfunction,paramlabel,"",datadropoff,paramtracking,"")
		return result
			

	def tracking(self,paramlist):
		trackingNumber = str(paramlist)
		payload="""<soapenv:Envelope
			xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
			xmlns:v1="http://www.ups.com/XMLSchema/XOLTWS/UPSS/v1.0"
			xmlns:v3="http://www.ups.com/XMLSchema/XOLTWS/Track/v2.0"
			xmlns:v11="http://www.ups.com/XMLSchema/XOLTWS/Common/v1.0">
			<soapenv:Header>
				<v1:UPSSecurity>
					<v1:UsernameToken>
						<v1:Username>"""+UPS_USERNAME+"""</v1:Username>
						<v1:Password>"""+UPS_PASSWD+"""</v1:Password>
					</v1:UsernameToken>
					<v1:ServiceAccessToken>
						<v1:AccessLicenseNumber>"""+UPS_ACCESSLICENCE_NUMBER+"""</v1:AccessLicenseNumber>
					</v1:ServiceAccessToken>
				</v1:UPSSecurity>
			</soapenv:Header>
			<soapenv:Body>
				<v3:TrackRequest>
					<v11:Request>
						<v11:RequestOption>1</v11:RequestOption>
						<v11:TransactionReference>
							<v11:CustomerContext>Your Test Case Summary Description</v11:CustomerContext>
						</v11:TransactionReference>
					</v11:Request>
					<v3:InquiryNumber>"""+trackingNumber+"""</v3:InquiryNumber>
				</v3:TrackRequest>
			</soapenv:Body>
		</soapenv:Envelope>"""
		headersConfig = {'content-type': 'text/xml;charset="utf-8"'}
		try:
			response=requests.post(UPS_TRACK_URL, data=payload, headers=headersConfig).text
			data = xmltodict.parse(response)
		except:
			# return response
			responseErr = {
	        	"status": 500,
	        	"errors": [
	            	{
	              		"detail": str(response)
	            	}
	        	]
	        }
			raise Exception(responseErr)

		try:
			# allres = data["soapenv:Envelope"]["soapenv:Body"]["trk:TrackResponse"]["trk:Shipment"]["trk:Package"]["trk:Activity"]
			location =  data["soapenv:Envelope"]["soapenv:Body"]["trk:TrackResponse"]["trk:Shipment"]["trk:Package"]["trk:Activity"]["trk:ActivityLocation"]["trk:Address"]["trk:City"]
			status = data["soapenv:Envelope"]["soapenv:Body"]["trk:TrackResponse"]["trk:Shipment"]["trk:Package"]["trk:Activity"]["trk:Status"]["trk:Description"]
		except:
			responseErr = {
	        	"status": 500,
	        	"errors": [
	            	{
	              		"detail": str(response)
	            	}
	        	]
	        }
			raise Exception(responseErr)

		if "processed" in status.lower():
			datastatus="processed"
		elif "transit" in status.lower():
			datastatus ="transit"
		elif "delivered" in status.lower():
			datastatus="delivered"
		else:
			datastatus ="unknown"
		
		final_data=[{
			"status":datastatus,
			"steps": [{
				"status": status,
				"location": location
			}]
		}]
		return final_data
	
	def label(self,userparamlist):
		
		req_list=["origin/first_name","origin/last_name","origin/city","origin/zipcode","origin/country_code","destination/first_name","destination/last_name","destination/phone","destination/line1","destination/zipcode","destination/country_code"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			# paramlist=userparamlist
			reqEmpty=["parcel/weight_in_grams","destination/first_name","destination/last_name","destination/street_name","destination/street_number","destination/line1","origin/line1","origin/phone"]
			paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)

			paramlist["origin"]["name"] = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
			paramlist["destination"]["name"] = str(paramlist["destination"]["first_name"])+" "+str(paramlist["destination"]["last_name"])
			
			data_line1= str(paramlist["origin"]["line1"])
			street_info = instance.json_check_line1(data_line1)
			paramlist["origin"]["street_number"]  = street_info["street_number"]
			paramlist["origin"]["street_name"]  =street_info["street_name"]
			if paramlist["origin"]["street_number"]=="":
				paramlist["origin"]["street_number"]="0"

			dest_line1= str(paramlist["origin"]["line1"])
			dest_street_info = instance.json_check_line1(dest_line1)
			paramlist["destination"]["street_number"]  = dest_street_info["street_number"]
			paramlist["destination"]["street_name"]  =dest_street_info["street_name"]
			if paramlist["destination"]["street_number"]=="":
				paramlist["destination"]["street_number"]="0"

		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		attentionNameOri = str(paramlist["origin"]["first_name"]) +" "+ str(paramlist["origin"]["last_name"])
		attentionNameDes =str(paramlist["destination"]["first_name"])+" "+str(paramlist["destination"]["last_name"])
		weight_in_kg = str(float(paramlist["parcel"]["weight_in_grams"])/1000)

		#new addreess
		fulladdressOrigin = str(paramlist["origin"]["street_number"]) +str(paramlist["origin"]["street_name"]) #+str(paramlist["origin"]["line1"])
		fulladdressDestination = str(paramlist["destination"]["street_number"]) +str(paramlist["destination"]["street_name"]) #+str(paramlist["destination"]["line1"])
		
		payload="""<envr:Envelope xmlns:auth="http://www.ups.com/schema/xpci/1.0/auth"
			xmlns:envr="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
			xmlns:upss="http://www.ups.com/XMLSchema/XOLTWS/UPSS/v1.0"
			xmlns:common="http://www.ups.com/XMLSchema/XOLTWS/Common/v1.0"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
			<envr:Header>
			          <upss:UPSSecurity>
			          <upss:UsernameToken>
			          <upss:Username>"""+UPS_USERNAME+"""</upss:Username>
			          <upss:Password>"""+UPS_PASSWD+"""</upss:Password>
			          </upss:UsernameToken>
			          <upss:ServiceAccessToken>
			          <upss:AccessLicenseNumber>"""+UPS_ACCESSLICENCE_NUMBER+"""</upss:AccessLicenseNumber>
			          </upss:ServiceAccessToken>
			          </upss:UPSSecurity>
			</envr:Header>
			<envr:Body>
			      <ship:ShipmentRequest xsi:schemaLocation="http://www.ups.com/XMLSchema/XOLTWS/Ship/v1.0"
			      xmlns:ship="http://www.ups.com/XMLSchema/XOLTWS/Ship/v1.0"
			      xmlns:ifs="http://www.ups.com/XMLSchema/XOLTWS/IF/v1.0">
			      <common:Request>
			            <common:RequestOption>nonvalidate</common:RequestOption>
			            <common:TransactionReference>
			            <common:CustomerContext>Your Customer Context</common:CustomerContext>
			            </common:TransactionReference>
			            </common:Request>
			      <ship:Shipment>
			              <ship:ReturnService>
			                    <ship:Code>9</ship:Code>
			              </ship:ReturnService>

			              <ship:Description>Description</ship:Description>
			              <ship:Shipper>
			                    <ship:Name>Hamza Alaya</ship:Name>
			                    <ship:AttentionName>ALAYA</ship:AttentionName>
			                    <ship:Phone>
			                    <ship:Number>1234567890</ship:Number>
			                    </ship:Phone>
			                    <ship:ShipperNumber>9R5R36</ship:ShipperNumber>
			                    <ship:FaxNumber>1234567890</ship:FaxNumber>
			                    <ship:Address>
			                    <ship:AddressLine>21 rue du bas</ship:AddressLine>
			                    <ship:City>AMSTERDAM</ship:City>
			                    <ship:PostalCode>1093</ship:PostalCode>
			                    <ship:CountryCode>NL</ship:CountryCode>
			                    </ship:Address>
			              </ship:Shipper>
			              <ship:ShipTo>
			                    <ship:Name>"""+paramlist["destination"]["company"]+"""</ship:Name>
			                    <ship:AttentionName>"""+attentionNameDes+"""</ship:AttentionName>
			                    <ship:Phone>
			                    <ship:Number>"""+paramlist["destination"]["phone"]+"""</ship:Number>
			                    </ship:Phone>
			                    <ship:Address>
			                    <ship:AddressLine>"""+fulladdressDestination+"""</ship:AddressLine>
			                    <ship:City>"""+paramlist["destination"]["city"]+"""</ship:City>
			                    <ship:PostalCode>"""+paramlist["destination"]["zipcode"]+"""</ship:PostalCode>
			                    <ship:CountryCode>"""+paramlist["destination"]["country_code"]+"""</ship:CountryCode>
			                    </ship:Address>
			              </ship:ShipTo>
			              <ship:ShipFrom>
			                    <ship:Name>"""+paramlist["origin"]["company"]+"""</ship:Name>
			                    <ship:AttentionName>"""+attentionNameOri+"""</ship:AttentionName>
			                    <ship:Phone>
			                    <ship:Number>"""+paramlist["origin"]["phone"]+"""</ship:Number>
			                    </ship:Phone>
			                    <ship:Address>
			                    <ship:AddressLine>"""+fulladdressOrigin+"""</ship:AddressLine>
			                    <ship:City>"""+paramlist["origin"]["city"]+"""</ship:City>
			                    <ship:PostalCode>"""+paramlist["origin"]["zipcode"]+"""</ship:PostalCode>
			                    <ship:CountryCode>"""+paramlist["origin"]["country_code"]+"""</ship:CountryCode>
			                    </ship:Address>
			              </ship:ShipFrom>
			              <ship:PaymentInformation>
			                    <ship:ShipmentCharge>
			                    <ship:Type>01</ship:Type>
			                    <ship:BillShipper>
			                    <ship:AccountNumber>9R5R36</ship:AccountNumber>
			                    </ship:BillShipper>
			                    </ship:ShipmentCharge>
			              </ship:PaymentInformation>
			              <ship:Service>
			                    <ship:Code>11</ship:Code>n>
			              </ship:Service>
			             <ship:Package>
			                <ship:Description>Description</ship:Description>
			                <ship:Packaging>
			                      <ship:Code>02</ship:Code>
			                      <ship:Description>Description</ship:Description>
			                </ship:Packaging>
			                <ship:Dimensions>
			                      <ship:UnitOfMeasurement>
			                            <ship:Code>CM</ship:Code>
			                      </ship:UnitOfMeasurement>
			                      <ship:Length>"""+str(paramlist["parcel"]["length_in_cm"])+"""</ship:Length>
			                      <ship:Width>"""+str(paramlist["parcel"]["width_in_cm"])+"""</ship:Width>
			                      <ship:Height>"""+str(paramlist["parcel"]["height_in_cm"])+"""</ship:Height>
			                </ship:Dimensions>
			                <ship:PackageWeight>
			                      <ship:UnitOfMeasurement>
			                            <ship:Code>KGS</ship:Code>
			                      </ship:UnitOfMeasurement>
			                      <ship:Weight>"""+str(weight_in_kg)+"""</ship:Weight>
			                </ship:PackageWeight>
			             </ship:Package>
			      </ship:Shipment>
			      <ship:LabelSpecification>
			              <ship:LabelImageFormat>
			                    <ship:Code>GIF</ship:Code>
			                    <ship:Description>GIF</ship:Description>
			              </ship:LabelImageFormat>
			              <ship:HTTPUserAgent>Mozilla/4.5</ship:HTTPUserAgent>
			      </ship:LabelSpecification>
			      </ship:ShipmentRequest>
			</envr:Body>
			</envr:Envelope>"""
		headersConfig = {'content-type': 'text/xml;charset="utf-8"'}
		response = netw.sendRequestHeaderConfig(UPS_LABEL_URL, payload, "post", headersConfig)
		data = xmltodict.parse(response)
		try:
			img_data = data["soapenv:Envelope"]["soapenv:Body"]["ship:ShipmentResponse"]["ship:ShipmentResults"]["ship:PackageResults"]["ship:ShippingLabel"]["ship:GraphicImage"]
			
		except:
			# return response
			responseErr = {
	        	"status": 500,
	        	"errors": [
	            	{
	              		"detail": str(response)
	            	}
	        	]
	        }
			raise Exception(responseErr)
		try:
			shipment_id = data["soapenv:Envelope"]["soapenv:Body"]["ship:ShipmentResponse"]["ship:ShipmentResults"]["ship:ShipmentIdentificationNumber"]
		except:
			shipment_id ='0000'
		c = boto.connect_s3(os.environ["AWS_S3_KEY1"], os.environ["AWS_S3_KEY2"])
		bucket = c.get_bucket("srbstickers", validate=False)
		name_file = str(time.time()) + ".pdf"
		k = Key(bucket)
		k.key = name_file
		k.contentType="application/pdf"
		k.ContentDisposition="inline"
		# k.set_contents_from_string(base64.b64decode(img_data.encode('ascii')))
		imgpic =str(time.time()) + ".png"
		with open('/tmp/'+imgpic, 'wb') as f:
	 		f.write(base64.b64decode(img_data.encode('ascii')))
	 		# f.write(base64.b64decode(img_data))
		filedir = '/tmp/'+imgpic
		k.set_contents_from_filename(filedir)
		link_pdf = "https://s3-us-west-2.amazonaws.com/srbstickers/" + name_file
		data = {
			"origin": paramlist["origin"],
			"destination": paramlist["destination"],
			"parcel": paramlist["parcel"],
			"carrier_shipment_id": shipment_id,
			"label_url": link_pdf
		}
		return data