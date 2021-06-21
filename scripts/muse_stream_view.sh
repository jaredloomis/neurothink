#!/bin/bash

# Start muse lsl stream with all sensor data
muselsl stream -pcg &
STREAM_PID=$!

# Wait for startup
echo "Waiting 10 seconds to initialize connection..."
sleep 10
echo "Starting viewer."

# Start viewer
muselsl view --version 2

# Stop the muse stream once the viewer has exited
kill ${STREAM_PID} 2> /dev/null
