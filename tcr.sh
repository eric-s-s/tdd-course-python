#!/usr/bin/env bash

if pytest ; then
    black .
    git add .
    git commit -m "$(echo $@)"  # read the arguments as the commit message
fi
git reset --hard
git status

