#!/usr/bin/env bash

#####################################################################################################################
#
# Target:
# Send the specific API request to fake API server and check the request result is successfully or not.
#
# Description:
# Use command line *curl* and use regular expression to check the running result.
#
# Allowable options:
#  -a [Server host]              The fake API server host.
#  -p [Python package name]       The API URL path to request.
#  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, i, d, h]
#
#####################################################################################################################

show_help() {
    echo "Shell script usage: bash ./scripts/ci/verify_fake_api_server_state.sh [OPTION] [VALUE]"
    echo " "
    echo "This is a shell script for generating tag by software version which be recorded in package info module (__pkg_info__) from Python package for building Docker image."
    echo " "
    echo "options:"
    if [ "$OPTARG" == "" ] || [ "$OPTARG" == "a" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
        echo "  -a [Server host]              The fake API server host."
    fi
    if [ "$OPTARG" == "" ] || [ "$OPTARG" == "p" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
        echo "  -p [Python package name]       The API URL path to request."
    fi
    echo "  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, d]"
}

# Show help if no arguments provided
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Handle arguments
if [ $# -gt 0 ]; then
    case "$1" in
        -h|--help)    # Help for display all usage of each arguments
            show_help
            exit 0
            ;;
    esac
fi

while getopts "a:p:?" argv
do
     case $argv in
         "a")    # fake sever host address
           Fake_API_Server_Host=$OPTARG
           ;;
         "p")    # API URL path
           API_Path=$OPTARG
           ;;
         ?)
           echo "Invalid command line argument. Please use option *h* to get more details of argument usage."
           exit
           ;;
     esac
done

#Fake_API_Server_Host="127.0.0.1:9672"
#API_Path="/api/v1/test/foo?date=2025-03-29T00:00:00.000Z&fooType=ENUM1"

request_response=$(curl http://$Fake_API_Server_Host"$API_Path")
echo "Response result: $request_response"
# shellcheck disable=SC2046
# shellcheck disable=SC2143
if [ $(echo "$request_response" | grep -E "[F,f]ail|[E,e]rror") ]; then
    echo "❌ Request fail. Please check.";
    exit 1;
else
    echo "✅ Request successfully.";
    exit 0;
fi
