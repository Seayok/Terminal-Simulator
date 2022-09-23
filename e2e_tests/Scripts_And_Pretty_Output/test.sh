#!/bin/bash

IFS=$'\n'
test_list=`ls -l e2e_tests | awk '$9 ~ ".*\.in$" {print $9}'|awk 'BEGIN{FS="."} {print $1}' |tail -n+1`
for command in $test_list
do
    cat e2e_tests/$command.in | python3 nautilus.py | \
    e2e_tests/Scripts_And_Pretty_Output/pretty.sh e2e_tests/$command.in > \
    e2e_tests/Scripts_And_Pretty_Output/Pretty_Output/$command.out
done