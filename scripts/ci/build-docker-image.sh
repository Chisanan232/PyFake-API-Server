#!/usr/bin/env bash

#####################################################################################################################
#
# Target:
# Automate to build Docker image with the software version which be recorded in package info module (<pacakge>/__pkg_info__.py)
#
# Description:
# Build the Docker image and tag it by current software version.
#
# Allowable options:
#  -r [Release type]              Release type of project. Different release type it would get different version format. [options: python-package]
#  -p [Python package name]       The Python package name. It will use this naming to get the package info module (__pkg_info__.py) to get the version info.
#  -v [Version format]            Which version format you should use. [options: general-2, general-3, date-based]
#  -i [Docker image name]         Set the naming to the Docker image this shell will build.
#  -d [Run mode]                  Running mode. Set 'dry-run' or 'debug' to let it only show log message without exactly working. [options: general, dry-run, debug]
#  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, i, d, h]
#
#####################################################################################################################

while getopts "r:p:v:i:d:h:?" argv
do
     case $argv in
         "r")    # Release type
           Input_Arg_Release_Type=$OPTARG
           ;;
         "p")    # Python package name
           Input_Arg_Python_Pkg_Name=$OPTARG
           ;;
         "v")    # Software version format
           Input_Arg_Software_Version_Format=$OPTARG
           ;;
         "i")    # Use this to name Docker image it will build
           Docker_Image_Name=$OPTARG
           ;;
         "d")    # Dry run
           Running_Mode=$OPTARG
           ;;
         "h")    # Help for display all usage of each arguments
           echo "Shell script usage: bash ./scripts/ci/build-docker-image.sh [OPTION] [VALUE]"
           echo " "
           echo "This is a shell script for building Docker image with software version which be get from package info module (__pkg_info__) from Python package."
           echo " "
           echo "options:"
           if [ "$OPTARG" == "r" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
               echo "  -r [Release type]              Release type of project. Different release type it would get different version format. [options: python-package]"
           fi
           if [ "$OPTARG" == "p" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
               echo "  -p [Python package name]       The Python package name. It will use this naming to get the package info module (__pkg_info__.py) to get the version info."
           fi
           if [ "$OPTARG" == "v" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
               echo "  -v [Version format]            Which version format you should use. [options: general-2, general-3, date-based]"
           fi
           if [ "$OPTARG" == "i" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
               echo "  -i [Docker image name]         Set the naming to the Docker image this shell will build."
           fi
           if [ "$OPTARG" == "d" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
               echo "  -d [Run mode]                  Running mode. Set 'dry-run' or 'debug' to let it only show log message without exactly working. [options: general, dry-run, debug]"
           fi
           echo "  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, i, d, h]"
           exit
           ;;
         ?)
           echo "Invalid command line argument. Please use option *h* to get more details of argument usage."
           exit
           ;;
     esac
done

declare Docker_Image_Tag
generate_image_tag() {
    Docker_Image_Tag=$(bash ./scripts/ci/generate-docker-image-tag.sh -r "$Input_Arg_Release_Type" -p "$Input_Arg_Python_Pkg_Name" -v "$Input_Arg_Software_Version_Format")
    echo "🐳 🖼️ 🏷️  Docker_Image_Tag: $Docker_Image_Tag"
}

build_docker_image() {
    if [ "$Running_Mode" == "dry-run" ] || [ "$Running_Mode" == "debug" ]; then
        echo "🕵️   Docker_Image_Tag: $Docker_Image_Tag"
        echo "It would run command line 'docker build ./ -t $Docker_Image_Name:$Docker_Image_Tag'"
    else
        echo "🏃‍♂️    Docker_Image_Tag: $Docker_Image_Tag"
        docker build ./ -t "$Docker_Image_Name":"$Docker_Image_Tag"
    fi
}

final_display() {
    docker images "$Docker_Image_Name"

    echo "🍻 Build Docker image successfully!"
}

# The process what the shell script want to do truly start here
echo "👷  Start to build Docker image with tag which be generated by software version ..."

generate_image_tag
build_docker_image
final_display
