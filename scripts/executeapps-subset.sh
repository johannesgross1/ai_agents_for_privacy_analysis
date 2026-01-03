#!/bin/bash

# This script launches a given list ($PACKAGES) of user-installed apps on the device
# except for the ones in the exclude list, waits for user input, and then terminates the apps.

# List of apps to exclude from data clearing, execution, and termination
EXCLUDE_APPS=("de.tomcory.heimdall" "com.topjohnwu.magisk")

# List of apps to execute
PACKAGES=("com.example.app1" "com.example.app2")
# Execution time per app
EXEC_TIME=60

# Initialize todo.txt
> todo.txt

# Flag to mark if we should skip execution and just log to todo.txt
SKIP_EXECUTION=false

# Loop through each package
for PACKAGE in "${PACKAGES[@]}"; do
    # Check if the heimdall app is not running, then mark to skip execution
    if [[ $(adb shell pidof de.tomcory.heimdall) == "" ]]; then
        #SKIP_EXECUTION=true
        echo "Heimdall is not running. Skipping execution and logging to todo.txt instead."
    fi

    # Check if current package is in the exclude list
    if [[ " ${EXCLUDE_APPS[*]} " != *" $PACKAGE "* ]]; then
        if [ "$SKIP_EXECUTION" = false ]; then
            # If not in exclude list, terminate the app and clear its app data
            echo "Terminating $PACKAGE..."
            adb shell am force-stop $PACKAGE
            echo "Clearing data for $PACKAGE..."
            adb shell pm clear $PACKAGE

            echo "Launching $APP..."
            adb shell monkey -p $PACKAGE -c android.intent.category.LAUNCHER 1

            # Wait for EXEC_TIME seconds before terminating the app
            #echo "Waiting for $EXEC_TIME seconds..."
            #sleep $EXEC_TIME

            echo "Press Enter to terminate $PACKAGE..."
            read -r -p "Waiting for user input..."

            # Terminate the app
            echo "Terminating $PACKAGE..."
            adb shell am force-stop $PACKAGE

            sleep 2
        else
            # If heimdall is not running, add the current and all remaining apps to todo.txt
            echo $PACKAGE >> todo.txt
        fi
    else
        echo "Skipping $PACKAGE..."
    fi
done

if [ "$SKIP_EXECUTION" = true ]; then
    echo "Heimdall is not running. Added apps to todo.txt instead of executing."
else
    echo "Done, all apps executed!"
fi
