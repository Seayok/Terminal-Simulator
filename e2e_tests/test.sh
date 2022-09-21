#!/bin/bash

cd e2e_tests
IFS=$'\n'
test_list=`ls -l Input | awk '{print $9}'|awk 'BEGIN{FS="."} {print $1}' |tail -n+2`
>.coverage
for command in $test_list
do
    cat Input/$command.in | coverage run -a --branch ../nautilus.py > Output/$command.out
    cat Output/$command.out | ./pretty.sh Input/$command.in > Pretty_Output/$command.out
done
coverage report -m