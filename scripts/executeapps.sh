#!/bin/bash

# This script launches all user-installed apps on the device
# except for the ones in the exclude list, waits for a specified amount of time,
# and then terminates the apps.

# List of apps to exclude from data clearing, execution, and termination
EXCLUDE_APPS=("de.tomcory.heimdall" "com.topjohnwu.magisk")
# Get a list of all installed packages on the device, sort them alphabetically
PACKAGES=$(adb shell pm list packages -3 | sed 's/package://g' | sort)

# Array to hold apps that will be executed and then terminated
EXECUTE_APPS=()

EXEC_TIME=60

# Loop through each package
for PACKAGE in $PACKAGES; do
    # Check if current package is in the exclude list
    if [[ " ${EXCLUDE_APPS[*]} " != *" $PACKAGE "* ]]; then
        # If not in exclude list, terminate the app and clear its  app data
	echo "Terminating $PACKAGE..."
	adb shell am force-stop $PACKAGE
#	sleep 1
        echo "Clearing data for $PACKAGE..."
        adb shell pm clear $PACKAGE
        # Add the app to the list of apps to be executed
        EXECUTE_APPS+=($PACKAGE)
    else
        echo "Skipping $PACKAGE..."
    fi
done

sleep 5

# Execute each app in the sorted list, then wait and terminate
for APP in "${EXECUTE_APPS[@]}"; do
    echo "Launching $APP..."
    adb shell monkey -p $APP -c android.intent.category.LAUNCHER 1
    
    # Wait for x seconds before terminating the app
    echo "Waiting for $EXEC_TIME seconds..."
    sleep $EXEC_TIME
    
    # Terminate the app
    echo "Terminating $APP..."
    adb shell am force-stop $APP

    sleep 5
done

echo "Done, all apps executed!"

