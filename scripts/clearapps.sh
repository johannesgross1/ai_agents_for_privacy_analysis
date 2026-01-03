#!/bin/bash

# This script clears the app data for all user-installed apps on the device
# except for the ones in the exclude list.

# List of apps to exclude from data clearing
EXCLUDE_APPS=("de.tomcory.heimdall" "com.topjohnwu.magisk")

# Get a list of all installed packages on the device
PACKAGES=$(adb shell pm list packages -3 | sed 's/package://g' | sort)

# Loop through each package
for PACKAGE in $PACKAGES; do
    # Check if current package is in the exclude list
    if [[ " ${EXCLUDE_APPS[*]} " != *" $PACKAGE "* ]]; then
        # If not in exclude list, clear app data
        echo "Clearing data for $PACKAGE..."
        adb shell pm clear $PACKAGE
    else
        echo "Skipping $PACKAGE..."
    fi
done

echo "Data cleared for all user-installed apps except excluded ones."

