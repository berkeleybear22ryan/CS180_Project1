#!/bin/bash

for file in *.mp4; do
    if [[ $file != *__c.mp4 ]]; then
        ffmpeg -i "$file" -vcodec libx264 -crf 28 "${file%.mp4}__c.mp4"
    fi
done
