import sys
import json
import smtplib
from pathlib import Path

class GmailServer(smtplib.SMTP_SSL):
	host='smtp.gmail.com'
	port=465

	def __init__(self):
		super(GmailServer,self).__init__('smtp.gmail.com',465)
		self.email_address=''
		print(self.host)
		#self.connect('smtp.gmail.com',self.port)
		
	def login(self,f_credentials):
		with open(f_credentials) as json_file:
			data=json.load(json_file)
			super(GmailServer,self).login(data['email'],data['password'])
			self.email_address=data['email']

def main():
	f_credentials=Path(sys.path[0]) / 'private' / 'gmail_credentials.json'
	server=GmailServer()
	server.login(f_credentials)
	server.sendmail(
  	server.email_address, 
	server.email_address,
 	"this message is from python")
	server.close()
	

if __name__=="__main__":
	main()