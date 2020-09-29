#!/bin/bash

# Make a deployment. Copy all files below main/ into a deploy directory, but not the .git repos. 



# Move out of scripts dir
cd ..

rm -rf deploy
mkdir deploy

cp -r main/* deploy/

rm -rf deploy/*/.git
#ls deploy/*/.git
