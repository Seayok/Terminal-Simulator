#!/bin/bash

num=1
raw=`sed 's/$ /$ \n/g'`
IFS=$'\n'
for line in $raw
do
    if [[ $line == *"$ " ]]; then
        command=`head -n $num $1 | tail -1`
        echo $line$command
        num=$(( $num + 1 ))
    else
        echo $line
    fi
done