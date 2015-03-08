#!/bin/bash
PATH_TO_SCRIPT=$(cd ${0%/*} && echo $PWD/${0##*/})
PATH_TO_FOLDER=`dirname "$PATH_TO_SCRIPT"`
export PYTHONPATH=$PYTHONPATH:$PATH_TO_FOLDER
cd $PATH_TO_FOLDER; nosetests tests/unit/*

