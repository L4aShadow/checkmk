#!/usr/bin/env python
# author: Joe McManus joe.mcmanus@solidfire.com
# file: checkClusterApi.py
# version: 1.0 2018/09/12
# use: Query clusters and nodes for nagios info, or stand-alone command line
# coding: utf-8

# modified by: Sebastian Fornfischer
# sebastian.fornfischer@prosiebensat1.com

# date: 2018/09/12

# place file in /usr/lib/check_mk_agent

# the following is used in the plugins directory:
# host:/usr/lib/check_mk_agent# cat plugins/slfr-cluster.sh
# /usr/bin/python /usr/lib/check_mk_agent/SolidFireAgentCluster.py ipaddress 443 acctname password mvip

# change the variable murl further down to set the appropriate solidfire api value

import urllib3
import urllib.request, urllib.error, urllib.parse
import base64
import json
import sys
import io
import os.path
import math
import socket
import re
import textwrap
import time
import ssl
from urllib import request, parse


context=ssl.create_default_context() 
context.check_hostname=False 
context.verify_mode=ssl.CERT_NONE 

version="1.0 2018/09/12"

#This is a nagios thing, nagionic you might say.
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3
STATE_DEPENDENT=4
exitStatus=STATE_OK


checkDiskUse=1          #Generate Alerts on disk access
checkUtilization=1 	#Generate Alerts on the utilization of cluster space
checkSessions=1    	#Generate Alerts on the number of iSCSI sessions
checkDiskUse=1     	#Generate Alerts on disk access 
checkClusterFaults=0    #Generate Alerts on cluster Faults

def printUsage(error):
        print(("ERROR: " + error))
        print(("USAGE: " + sys.argv[0] + " (IP|HOSTNAME) PORT USERNAME PASSWORD (mvip|node)"))
        sys.exit(STATE_UNKNOWN)

#Check command line options that are passed
def commandLineOptions():
        if len(sys.argv) < 6:
                printUsage("Incorrect Number of Arguments.")
        ip=sys.argv[1]
        port=sys.argv[2]
        username=sys.argv[3]
        password=sys.argv[4]
        ipType=sys.argv[5]
        if ipType != "mvip" and ipType != "node":
                printUsage("Invalid type specified, use node or mvip")
        return ip, port, username, password, ipType

import sys
import urllib.request
import base64
import json
import ssl

# Send requests to the target
def sendRequest(ip, port, murl, username, password, jsonData, ipType):
    url = 'https://' + ip + ":" + port + murl
    authKey = base64.b64encode((username + ":" + password).encode()).decode()
    request = urllib.request.Request(url, data=jsonData.encode(), headers={
        "Content-Type": "application/json-rpc",
        "Authorization": "Basic " + authKey
    })
    try:
        response = urllib.request.urlopen(request, timeout=20, context=context)
        jsonResponse = json.loads(response.read().decode())
        #print(jsonResponse)
    except Exception as e:
        printUsage("Unable to connect to host: " + ip)

    # Check to see if we got a valid jsonResponse
    if 'result' not in jsonResponse:
        printUsage("Invalid response received.")
    else:
        return jsonResponse['result']
        print(jsonResponse)
        
#Check for a valid IP
def ipCheck(ip):
        pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        if re.match(pattern, ip):
                return True
        else:
                return False

#Resolve Hostnames
def checkName(hostname):
        try:
                socket.gethostbyname(hostname)
        except:
                printUsage("Unable to resolve hostname " + hostname)

#Add a asterik to values that are in error
def addNote(testResult, exitStatus, value):
	if testResult != 0:
		value=value + "*"
		if testResult > exitStatus:
			exitStatus = testResult
	return exitStatus, value				

#Print a table
def prettyPrint(description, value, width):
        #When printing values wider than the second column, split and print them
        if len(value) > (width/2):
                print(("| "  + description.ljust(width/2) + " |" ), end=' ')
                i=0
                wrapped=textwrap.wrap(value, 29)
                for loop in wrapped:
                        if i == 0:
                                print((loop + "|".rjust(width/2-(len(loop)))))
                        else:
                                print(("| ".ljust(width/2+2) + " | " + loop + "|".rjust(width/2-(len(loop)))))
                        i=i+1
        else:
                print(( "| " + description.ljust(width/2) + " | " + value  + "|".rjust(width/2-(len(value)))))

#Print Exit Status in English
def prettyStatus(exitStatus):
        if exitStatus == 0:
                printStatus="OK"
        elif exitStatus == 1:
                printStatus="*Warning"
        elif exitStatus == 2:
                printStatus="*Critical"
        elif exitStatus == 3:
                printStatus="*Unknown"
        return printStatus

murl="/json-rpc/10.1"
#Check the command line options
commandOpts=commandLineOptions()

ip=commandOpts[0]
port=commandOpts[1]
username=commandOpts[2]
password=commandOpts[3]
ipType=commandOpts[4]

#Check to see if we were provided a name, and check that we can resolve it.
if ipCheck(ip) == False:
  checkName(ip)

# =========== cluster ===================

jsonData = json.dumps( { 'method': 'GetClusterCapacity', 'params': {}, 'id': 1 } )
response = sendRequest( ip, port, murl, username, password, jsonData, ipType )
print("WEITER")
print(response)
capacity = response['clusterCapacity']

print( '<<<slfr_cluster>>>' )

print(( 'totalOps' + ' ' + str(capacity['totalOps']) ))

print(( 'clusterRecentIOSize' + ' ' + str(capacity['clusterRecentIOSize']) ))
print(( 'currentIOPS' + ' ' + str(capacity['currentIOPS']) ))

print(( 'zeroBlocks' + ' ' + str(capacity['zeroBlocks']) ))
print(( 'nonZeroBlocks' + ' ' + str(capacity['nonZeroBlocks']) ))
print(( 'uniqueBlocks' + ' ' + str(capacity['uniqueBlocks']) ))
print(( 'uniqueBlocksUsedSpace' + ' ' + str(capacity['uniqueBlocksUsedSpace']) ))

print(( 'timestamp' + ' ' + capacity['timestamp'] ))


print( '<<<slfr_cluster_sessions>>>' )

#Number of iSCSI Sessions
jsonData=json.dumps({"method":"ListISCSISessions","params":{},"id":1})
response=sendRequest(ip, port, murl, username, password, jsonData, ipType)
details=response['sessions']
numSessions=len(details)

print(( 'sessions' + ' ' + str(numSessions)))

print( '<<<slfr_cluster_faults>>>' )

#Cluster Faults
if checkClusterFaults == 1:
	clusterFaults=""
	jsonData=json.dumps({"method":"ListClusterFaults","params":{},"id":1})
	response=sendRequest(ip, port, murl, username, password, jsonData, ipType)
	clusterFaultsResponse=response['faults']
	for fault in clusterFaultsResponse:
		if fault['resolved'] != True:
			testResult=STATE_CRITICAL
			date=fault['date'][:-8]
			if clusterFaults == "":
				clusterFaults=date + " " +  fault['details']
			else:
				clusterFaults=clusterFaults + ",  " + date + " " +  fault['details']
	if clusterFaults == "":
		clusterFaults="None";
		testResult=STATE_OK
	exitStatus, clusterFaults=addNote(testResult, exitStatus, clusterFaults)
else:
	clusterFaults="n/a"

print(( 'clusterFaults' + ' ' + clusterFaults))


print( '<<<slfr_cluster_members>>>' )

#Get name and members from GetClusterInfo
jsonData=json.dumps({"method":"GetClusterInfo","params":{},"id":1})
response=sendRequest(ip, port, murl, username, password, jsonData, ipType)
details=response['clusterInfo']
clusterName=details['name']
ensemble=details['ensemble']
ensembleCount=len(ensemble)

print(("ensembleMembers" + ' ' +  str(', '.join(map(str, ensemble)))))


# ========= volume ================

#jsonData = json.dumps( { "method": "ListVolumes", "params": {}, "id": 1 } )
#response = sendRequest( ip, port, murl, username, password, jsonData, ipType )

#print( '<<<slfr_volumes>>>' )

#volumes = response[ 'volumes' ]
#for volume in volumes:
  #print( str( volume['accountID'] ) + ', ' +str(volume['volumeID']) + ', ' + volume['name'] + ', ' + volume['status'] + ', ' + str(volume['totalSize']) )

#  jsonData = json.dumps( { 'method': 'GetVolumeStats', 'params': { 'volumeID': volume['volumeID'] }, 'id': 1 } )
#  response = sendRequest( ip, port, murl, username, password, jsonData, ipType )

#  stats = response['volumeStats']
#  print((
#      volume['name'] + '-' + str(stats['volumeID'])
#    + ' actualIOPS ' + str(stats['actualIOPS'] )
#    + ' averageIOPSize ' + str(stats['averageIOPSize'] )
#    + ' burstIOPSCredit ' + str(stats['burstIOPSCredit'] )
#    + ' readBytes ' + str(stats['readBytes'] )
#    + ' writeBytes ' + str(stats['writeBytes'] )
#    + ' readOps ' + str(stats['readOps'] )
#    + ' writeOps ' + str(stats['writeOps'] )
#    + ' unalignedReads ' + str(stats['unalignedReads'] )
#    + ' unalignedWrites ' + str(stats['unalignedWrites'] )
#    + ' throttle ' + str(stats['throttle'] )
#    + ' clientQueueDepth ' + str(stats['clientQueueDepth'] )
#    + ' zeroBlocks ' + str(stats['zeroBlocks'] )
#    + ' nonZeroBlocks ' + str(stats['nonZeroBlocks'] )
#    + ' latencyUSec ' + str(stats['latencyUSec'] )
#    + ' readLatencyUSec ' + str(stats['readLatencyUSec'] )
#    + ' writeLatencyUSec ' + str(stats['writeLatencyUSec'] )
#    + ' volumeUtilization ' + str(stats['volumeUtilization'] )
#    + ' volumeSize ' + str(stats['volumeSize'] )
#    ))

# ========= node ================

jsonData = json.dumps( { 'method': 'ListActiveNodes', 'params': {}, "id": 1 } )
response = sendRequest( ip, port, murl, username, password, jsonData, ipType )

print( '<<<slfr_nodes>>>' )

nodes = response['nodes']
for node in nodes:

  jsonData = json.dumps( { 'method': 'GetNodeStats', 'params': { 'nodeID': node['nodeID'] }, 'id': 1 } )
  response = sendRequest( ip, port, murl, username, password, jsonData, ipType )

  stats = response['nodeStats']
  print((
      node[ 'name' ] + '-' + str(node['nodeID'])
    + ' cpu ' + str(stats['cpu'])
    + ' cBytesIn ' + str(stats['cBytesIn'])
    + ' cBytesOut ' + str(stats['cBytesOut'])
    + ' mBytesIn ' + str(stats['mBytesIn'])
    + ' mBytesOut ' + str(stats['mBytesOut'])
    + ' sBytesIn ' + str(stats['sBytesIn'])
    + ' sBytesOut ' + str(stats['sBytesOut'])
    ))

#capacity = response['clusterCapacity']
#print(
#  '0'
#  + ' SLFR-Capacity'
#  + ' clusterRecentIOSize=' + str(capacity['clusterRecentIOSize'])
#  + '|currentIOPS=' + str(capacity['currentIOPS'])
#  + '|maxIOPS=' + str(capacity['maxIOPS'])
#  + '|nonZeroBlocks=' + str(capacity['nonZeroBlocks'])
#  + '|zeroBlocks=' + str(capacity['zeroBlocks'])
#  + ' timestamp: ' + capacity['timestamp']
#  )

#print(
#          'zeroBlocks' + ' ' + str(capacity['zeroBlocks'])
#  + ' ' + 'nonZeroBlocks' + ' ' + str(capacity['nonZeroBlocks'])
#  + ' ' + 'uniqueBlocks' + ' ' + str(capacity['uniqueBlocks'])
#  + ' ' + 'uniqueBlocksUsedSpace' + ' ' + str(capacity['uniqueBlocksUsedSpace'])
#  )

sys.exit(0)
