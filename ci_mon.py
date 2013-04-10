#
# Simple script to trigger and monitor Jenkins CI job. Intended for hooking up with git to get Heroku style console output.
#
#
# Usage with post-commit git hook:
#
# #!/bin/bash
#
# branch=$(git rev-parse --symbolic --abbrev-ref $1)
# echo Update pushed to branch $branch
#
# if [ $branch == "stage" ]; then
#   echo '==============================================='
#   echo ' Starting deploy via CI to Staging environment '
#   echo '==============================================='
#
#   python ./hooks/ci_mon.py "http://jenkins.example.com:8080" cserv-stage-deploy
# fi
#
#

import urllib2
import time
import json
import sys

if (len(sys.argv) != 3):
  print "Usage: ci_mon.py <server> <task>"
  exit(1)

server = sys.argv[1]
task = sys.argv[2]

def get_next_build_url():
   qurl =  '{0}/job/{1}/api/json?depth=0'.format(server,task)
   status = json.loads(urllib2.urlopen(qurl).read())

   result = { 'in_queue': status['inQueue'], 'build_url': "{0}/job/{1}/{2}/".format(server, task, status['nextBuildNumber'])}

   return result

def kick_off_build():
   print 'Kicking off build'

   queue_build = get_next_build_url()

   urllib2.urlopen('{0}/job/{1}/polling'.format(server,task)).read()
   urllib2.urlopen('{0}/job/{1}/build'.format(server,task)).read()

   return queue_build

def get_queued_build():
   print 'Checking if queued...'
   qurl =  '{0}/job/{1}/api/json?depth=0'.format(server,task)
   status = json.loads(urllib2.urlopen(qurl).read())

   result = None
   if status['inQueue']:
      print 'Queued build found'
      result = { 'in_queue': status['inQueue'], 'build_url': "{0}{1}/".format(status['queueItem']['task']['url'], status['nextBuildNumber'])}

   return result

def monitor_build(mon_url):
   print 'Monitoring {0}'.format(mon_url)
   build_url = '{0}api/json?depth=1'.format(mon_url)
   console_url = '{0}console'.format(mon_url)
   progressive_url = '{0}logText/progressiveHtml'.format(mon_url)

   out = ''
   is_building = True
   print 'Waiting for build'
   while is_building or not len(out) :
       try:
           new_out = urllib2.urlopen(progressive_url).read()

           diff = new_out.replace(out,'')

           if len(diff) > 0:
               print diff
           else:
               sys.stdout.write('.')
               sys.stdout.flush()

           out = new_out
       except:
           sys.stdout.write(',')
           sys.stdout.flush()

       try:
           is_building = json.loads(urllib2.urlopen(build_url).read())['building']
       except:
           sys.stdout.write(',')
           sys.stdout.flush()

       if is_building:
           time.sleep(1)

queued = kick_off_build()
while not queued:
   queued = get_queued_build()

monitor_build(queued['build_url'])
