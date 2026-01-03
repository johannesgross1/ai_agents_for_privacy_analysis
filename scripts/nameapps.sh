#!/bin/bash

# This script lists all user-installed apps on the device along with their labels.

packages=$(adb shell pm list packages -3 | sed 's/package://g')

echo "User-installed apps and their labels:"

# Loop through the packages to get their labels
for package in $packages; do
    # Fetching the application label using dumpsys
    label=$(adb shell dumpsys package $package | grep -m1 "applicationInfo.labelRes" | awk '{print $1}')
    if [[ $label == *"0x0"* ]]; then
        # Some apps might not have labelRes; try another method
        label=$(adb shell dumpsys package $package | grep -m1 "Application Label" | cut -d= -f2)
    else
        # Convert labelRes to actual string
        label=$(adb shell dumpsys package $package | grep -A18 "Package $package")
    fi
    # Print package and label, remove any new lines or carriage returns
    echo "${package},${label}"
done
