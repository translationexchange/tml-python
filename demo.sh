#!/bin/bash
PATH_TO_SCRIPT=$(cd ${0%/*} && echo $PWD/${0##*/})
PATH_TO_FOLDER=`dirname "$PATH_TO_SCRIPT"`
echo $PATH_TO_FOLDER
export PYTHONPATH=$PYTHONPATH:$PATH_TO_FOLDER
echo $PYTHONPATH
cd $PATH_TO_FOLDER; python demo/app.py
