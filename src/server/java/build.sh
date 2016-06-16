#!/bin/bash
cd $(dirname "$0")/policynet-layout

# export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-1.8.0-openjdk.x86_64/}
echo "---- Begin: Compiling ---"
mvn install -q
exitCode=$?
echo "---- Done: Compiling ---"
exit $exitCode
