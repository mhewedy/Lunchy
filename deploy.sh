#!/bin/bash

# for deploy new changes:
fly deploy --wg=false --ha=false

# to stop the app:
# fly scale count 0

# to restart the app:
# fly app restart
