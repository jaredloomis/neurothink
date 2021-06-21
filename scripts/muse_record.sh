#!/bin/bash

# Default to a 30s recording
DURATION=${1:-30}

# Allow description for recording
DESCRIPTION="$2"

# Run muselsl, get stdout
muselsl_stdout_file="$(dirname $0)/muselsl_stdout"
muselsl record_direct -d $DURATION | tee "$muselsl_stdout_file"
muselsl_stdout=$(cat $muselsl_stdout_file)

# Find
muselsl_out_file=$(echo "$muselsl_stdout" | grep 'wrote file: ' | grep -oe '\/.*[a-zA-Z]')
readme_file="$(echo "$muselsl_out_file" | cut -f 1 -d '.').md"
cat "$muselsl_out_file"
mv "$muselsl_out_file" "$(dirname $0)/../data/muse2-recordings"
echo $DESCRIPTION > "$readme_file"
rm $muselsl_stdout_file