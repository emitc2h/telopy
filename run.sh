#!/bin/bash

cd app

export FLASK_APP=app
export FLASK_DEBUG=1
export TLPY_PATH=$1

flask run