#!/bin/bash

# start virtualen
virtualenv policy-ve -p python2.7
source policy-ve/bin/activate
pip install -r ./parser/requirements.txt
python parse.py $1 $2 $3
