#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-03-02 11:11:36
# @Author  : weiping 
# @Link    : https://github.com/Weiping1992

import memcache
import sys,os
import json
import commands

dicMemcache={}

def checkProcess():
	ProcessExists=commands.getoutput("ps aux|grep \"MemcacheBackupRestore.py restore\"|grep -v grep|wc -l")
	return ProcessExists

def GenerateMemcacheBackupFile(MemcacheClient):
	exist=checkProcess()
	#print exist
	if (int(exist) > 0):
		print "restore is running!exiting!"
		exit(0)
	else:
		if os.path.exists(tmpfilepath):
			os.rename(tmpfilepath,filepath)
		keyfile=commands.getoutput('memdump --servers='+memcache_ip+':'+port)
		#print keyfile
		for key in keyfile.split(os.linesep):
			value=MemcacheClient.get(key)
			#print key,value
			dicMemcache[key]=value
		#print dicMemcache
		f=open(tmpfilepath,'w')
		f.write(json.dumps(dicMemcache))
		f.close()

def RestoreMemcacheKeysValue(MemcacheClient):
	if os.path.exists(filepath):
		#print filepath+"exists"
		f=open(filepath,'r')
		dicWaitWrite=json.load(f)
		#print dicWaitWrite
		for key in dicWaitWrite.keys():
			result=MemcacheClient.add(key,dicWaitWrite[key])
			print "add KEY:"+str(key)+"  VALUE:"+str(dicWaitWrite[key])+"  "+str(result)
		f.close()
	else:
		print "ERROR: Don't have backup files!"

def AddMemcacheKeyValue(MemcacheClient,key,value):
	#check whether key exists
	GenerateMemcacheBackupFile(MemcacheClient)
	if dicMemcache.has_key(key):
		print "memcache has key: "+key
		result=MemcacheClient.replace(key,value)
		print "change the value of KEY: "+str(key)+" to VALUE: "+value+"  "+str(result)
	else:
		print "memcache doesn't have key: "+key
		result=MemcacheClient.add(key,value)
		print "add the value of KEY: "+str(key)+" to VALUE:"+value+"  "+str(result)
	#update json file
	GenerateMemcacheBackupFile(MemcacheClient)

def DeleteMemcacheKeyValue(MemcacheClient,key):
	#check whether key exists
	GenerateMemcacheBackupFile(MemcacheClient)
	if dicMemcache.has_key(key):
		print "memcache has key: "+key
		result=MemcacheClient.delete(key)
		print "delete KEY: "+str(key)+"  "+str(result)
	else:
		print "memcache doesn't have KEY: "+str(key)
	#update
	GenerateMemcacheBackupFile(MemcacheClient)

if __name__ == '__main__':

	filepath="/root/MemcacheDataBackup.json"
	tmpfilepath="/root/MemcacheDataBackup_tmp.json"

	#connect to memcache server
	memcache_ip=os.popen("ps aux|grep \"/usr/local/bin/memcache\"|grep -v \"grep\"|awk '{print $22}'").readline().strip(os.linesep)
	#print memcache_ip
	port=os.popen("ps aux|grep \"/usr/local/bin/memcache\"|grep -v \"grep\"|awk '{print $24}'").readline().strip(os.linesep)
	#print port
	mc=memcache.Client([memcache_ip+':'+port],debug=0)

	#option
	option_available=['backup','restore','addValue','delete']
	if not (len(sys.argv) < 2):
		option=sys.argv[1]
		if option not in option_available:
			print "ERROR: not support option: "+option
		else:
			if option == 'backup':
				GenerateMemcacheBackupFile(mc)
			elif option == 'restore':
				RestoreMemcacheKeysValue(mc)
			elif option == 'addValue':
				if not (len(sys.argv) < 4):
					key_add=sys.argv[2]
					value_add=sys.argv[3]
					AddMemcacheKeyValue(mc,key_add,value_add)
				else:
					print "ERROR: Please input parameter key_add and value_add! "
					print "Usage: python "+sys.argv[0]+" addValue key_add value_add"
			elif option == 'delete':
				if not (len(sys.argv) < 3):
					key_delete=sys.argv[2]
					DeleteMemcacheKeyValue(mc,key_delete)
				else:
					print "ERROR: Please input parameter key_delete! "
					print "Usage: python "+sys.argv[0]+" delete key_delete"
	else:
		print "Usage Error: python "+sys.argv[0]+" [option]"
		print "[option]: "
		for i in range(len(option_available)):
			if option_available[i] == "addValue":
				print "        addValue key value"
			elif option_available[i] == "delete":
				print "        delete key"
			else:
				print "        "+option_available[i]