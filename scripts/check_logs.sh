#!/bin/bash

if [ $# != 1 ] || [[ ! $1 =~ [a-z]{3}[0-9]{6} ]]; then
   echo "Incorrect arguments supplied. Usage:"
   echo ""
   echo "bash check_logs.sh <ref code>"
   echo ""
   echo "Aborting..."
   exit 0
fi

echo "Searching for last mention of ref code $1 in the log files ~/macro*/tmp/macro.log..."
echo ""

for i in $(find ~/macro*/tmp -iname macro.log); do
   grep -H -A 1 $1 $i | tail -n 2; echo ""
done
# for i in $(find ~/macro*/tmp -iname macro.log); do grep -H -A 1 dnm12 $i | tail -n 2; echo ""; done
