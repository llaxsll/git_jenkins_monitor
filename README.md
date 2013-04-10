Description
======
 Simple script to trigger and monitor Jenkins CI job. Intended for hooking up with git to get Heroku style console output.

Usage
======
 Usage with post-commit git hook:

 #!/bin/bash

 branch=$(git rev-parse --symbolic --abbrev-ref $1)
 echo Update pushed to branch $branch

 if [ $branch == "stage" ]; then
   echo '==============================================='
   echo ' Starting deploy via CI to Staging environment '
   echo '==============================================='

   python ./hooks/ci_mon.py "http://jenkins.example.com:8080" cserv-stage-deploy
 fi


