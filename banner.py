# -*- coding: utf-8 -*-

import dbs
import informe
import sys
import argparse
import socket
from netaddr import *
import urllib2
import os
#import ipwhois
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from BeautifulSoup import BeautifulSoup
import re
#from os import path
import time


fecha = (time.strftime("%d-%m-%y"))

if not os.path.isdir(fecha):
        os.mkdir(fecha)
os.chdir(fecha)


template = "{0:16}{1:3}{2:40}"
diro = os.getcwd()
dominios=[]

def infogathering(domi,puerts):
    print "[+] Search Online"
    response = urllib2.urlopen('http://api.hackertarget.com/hostsearch/?q='+domi)
    response2 = urllib2.urlopen('http://viewdns.info/dnsrecord/?domain='+domi)
    if response.code == 200:
        for line2 in response:
                #print '{0:<55}{1:<10}'.format(line2.rstrip().split(',')[0],line2.rstrip().split(',')[1])
                tempo=[line2.rstrip().split(',')[0],line2.rstrip().split(',')[1]]
                dominios.append(tempo)
                #print tempo
    else:
        print "[-] Site Down"
    soup = BeautifulSoup(response2.read())
    table = soup.findAll('table')
    tr = table[3].findAll('tr')
    for tdtemp in tr:
        td = tdtemp.findAll('td')
        a = td[5].text.encode("utf-8")[-1]
        if (a == "."):
            tempo=[td[0].text.encode("utf-8")[:-1],td[5].text.encode("utf-8")[:-1]]
        else:
            tempo=[td[0].text.encode("utf-8")[:-1],td[5].text.encode("utf-8")]
        dominios.append(tempo)
    for line in dominios:
        #print "Dominio: " + line[0] + " IP: " + line[1]
        if ((line[0] == domi) or (line[0] == "Nam")):
            next
        else:
            hostinfo(line[0], puerts)
            #print type(line[0])
            #print '{0:<55}{1:<10}'.format(line[0], line[1])


def takeScreenshot(host, port):
    try:
        print "    [*] Taking Screenshot"
        #browser = webdriver.Firefox(timeout=100)
        binary = FirefoxBinary('C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe')
        browser = webdriver.Firefox(firefox_binary=binary)
        #browser = webdriver.Firefox()
        browser.implicitly_wait(100)
        browser.set_page_load_timeout(200)
        browser.get('http://' + str(host) + ":" + str(port))    
        #print "        [+] Path: " + os.getcwd()
        if not os.path.isdir(str(host)):
            os.mkdir(str(host))
        os.chdir(str(host))
        a = str(port) + ".png"
        print "        [+] Filename: " + a
        browser.get('http://' + str(host) + ":" + str(port))
        browser.get_screenshot_as_file(a)
        browser.quit()
        os.chdir(diro)
        return a

    except Exception as e:
        print("ERROR: Do you have Firefox installed?")
        #exit(1)

    except Exception as e:
        print("[Error] takeScreenShot: {0}".format(e))
        browser.quit()


def hostinfo(ip, portz):
    ports = portz.split(",")
    for port in ports:
        try:
            print "    [*] Connecting to", str(ip), "port", port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((str(ip), int(port)))
            print "        [+]", ip, ":", port, '->', 'Open Port'
            s.close()
            url = ('http://' + str(ip) + ":" + str(port))
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            print "        [+] Banner: ", response.info()['server']
            print "        [+] Response: ", response.code
            pant = takeScreenshot(ip, str(port))
            cms = detectcms(ip, port)
            print "        [+] Storing in DB"
            almaDB(ip, port, cms, response.info()['server'], pant)
        except socket.error:
            print "        [-]", ip, ":", port, '->', 'Close Port'
            next
        except urllib2.HTTPError:
            print "        [+] Response: 403"
        except Exception as e:
            print "Error", e
            next


def hostsinfo(ips, port):
    try:
        print "[+] Network", ips
        for ip in IPNetwork(ips).iter_hosts():
            hostinfo(ip, port)
    except:
        sys.exit()


def infodom(dom, portz):
    try:
        print "\n### Obtain information about", dom, "###"
        ip = socket.gethostbyname(dom)
        hostinfo(ip, portz)
        print "    [*] Trying access with DNS"
        ports = portz.split(",")
        for port in ports:
            url = ('http://'+ str(dom) + ":" + str(port))
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            print "        [+] Banner: ", response.info()['server']
            print "        [+] Response: ", response.code
            pant = takeScreenshot(dom, str(port))
            cms = detectcms(dom, port)
            print "        [+] Saving result in DB"
            almaDB(dom, port, cms, response.info()['server'], pant)
    except socket.gaierror:
        print "Can't resolve", dom
        next
    except urllib2.HTTPError:
        print "        [+] Response: 503"
        next
    #except Exception as e:
     #   print "Errorsss", e
      #  next


def detectcms(domi, ptr):
    try:
        print "    [*] Detecting CMS " + str(domi)
        response = urllib2.urlopen('http://' + str(domi))
        soup = BeautifulSoup(response.read())
        if re.search('Joomla', str(soup('meta'))):
            response2 = urllib2.urlopen('http://' + str(domi) + ":" + str(ptr) + '/administrator/manifests/files/joomla.xml')
            soup2 = BeautifulSoup(response2.read())
            for message in soup2.findAll('version'):
                print "        [+] Found Joomla " + str(message.text)
                return "Joomla " + str(message.text)
        elif re.search('moodle', str(soup('meta'))):
            print "        [+] Found Moodle"
            return "Moodle"
        elif re.search('Drupal', str(soup('meta'))):
            print "        [+] Found Drupal"
            bandera = True
            url = "http://" + str(domi) + "/CHANGELOG.txt"
            data = urllib2.urlopen(url)
            for line in data:
                if len(line) == 24 and bandera:
                    version = line
                    bandera = False
                    print "        [+] Found Drupal", version
                    return "Drupal " + str(version)
        elif re.search('DSpace', str(soup('meta'))):
            print "        [+] Found DSpace"
            return "DSpace"
        else:
            logo = 'http://' + str(domi) + '/readme.html'
            resa = urllib2.urlopen(logo)
            print resa
            if (resa.code == 200):
                soup2 = BeautifulSoup(resa.read())
                for line in soup2('h1'):
                    if re.search('WordPress', str(line)):
                        print "        [+] Found Wordpress Version " + str(line.text)
                        return "Wordpress " + str(line.text)
    except urllib2.URLError:
        print "         [-] CMS not found"   # str(response.code)
        return "Not Found"
    except urllib2.HTTPError:
        print 'The server couldn\'t fulfill the request.'
    except socket.timeout:
        print " [-] Timed out!"
    except Exception as e:
        print "error", e


def listdom(ldom, port):
    archi = open(ldom, 'r')
    lineas = (l.rstrip('\n') for l in file(ldom, "Ur"))
    for l in lineas:
        infodom(l, port)
    archi.close()


def almaDB(ipa, porta, cmsa, reqa, panta):
#sqlite_insert_data( ip, port, cms, banner, screenshot )
    dbs.sqlite_insert_data(ipa, porta, cmsa, reqa, panta)

if __name__ == "__main__":
    try:
        dbs.sqlite_create_table()
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', action='store', dest='dom', help='Domain')
        parser.add_argument('-i', action='store', dest='ips', help='IP / CIDR')
        parser.add_argument('-p', action='store', type=str, dest='ports',
                            default='80', help='Port\'s separated by -')
        parser.add_argument('-f', action='store', dest='arch',
                            help='File with domains')
        parser.add_argument('-inf', action='store_true', help='Report')
        args, unknown = parser.parse_known_args()

        if args.ips:
            try:
                hosts = IPNetwork(args.ips)
                hostsinfo(hosts, args.ports)
            except Exception as e:
                print "a", e
                sys.exit()

        if args.dom:
            #infodom(args.dom, args.ports)
            infogathering(args.dom, args.ports)

        if args.arch:
            listdom(args.arch, args.ports)

        if args.inf:
            print "Opening Firefox"
            browsers = webdriver.Firefox(timeout=200)
            browsers.implicitly_wait(200)
            browsers.set_page_load_timeout(200)
            browsers.get('http://127.0.0.1:5000')
            informe.app.run(debug=False)

    except KeyboardInterrupt as e:
        print("[+] Bye!")
