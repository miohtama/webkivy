#!/bin/bash
#
# Generate index.html in all subdirectories of the current working directory
#

set -e

# Walk through all directories which are not Python caches
for dir in $(find -L -type d -not -path "*/__pycache__") ; do
    pushd $dir > /dev/null
    out=index.html
    # Generate local index.html in the directory
    echo "<p>Generated index.html for <a href='https://github.com/miohtama/webkivy'>Webkivy</a></p>" > $out
    echo "<ul>" >> $out
    for file in $(find -L . -maxdepth 1 -not -name *.pyc -not -path "*/__pycache__" -printf '%P\n') ; do
        if [ -d $file ] ; then
            # Add ending slash to the directories
            file=$file/
        fi
        echo "<li>" >> $out
        echo "<a href='$file'>$file</a>" >> $out
        echo "</li>" >> $out
    done
    echo "  </ul>" >> $out

    # Report to the shell owner
    echo "Generated $PWD/index.html"
    popd  > /dev/null
done