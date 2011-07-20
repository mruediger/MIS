#!/bin/bash

directory=$1

find $directory -name \*py | while read file; do
    todoline=`grep -n \#TODO $file`;
    if [ -n "$todoline" ] ; then
        echo $file;
        grep -n \#TODO $file | sed -r 's/([0-9]*:).*#TODO(.*)/\1\t\2/'
    fi
done
