#!/bin/bash


function phelp()
{
    echo "Use args: ${0} [mode] [build] [path]"
    echo "mode: use an option at once"
    echo "      -r, --run       : run mode        - run image background (quit)"
    echo "      -f, --front     : frontend mode   - run image frontend (no quit)"
    echo "      -d, --down      : down mode       - shutdown image (quit)"
    echo "build: use an option at once"
    echo "      -b, --build     : build image       - build image "
    echo "      -n, --notbuild  : not build image       - not build imagee "
    echo "path: image docker-compose.yml"
}
if [ $# -lt 2 ]; then
    phelp ${0}
    exit 1
fi

function eoption()
{
    OPTION=${1}
    if [ ${OPTION} = "-r" ] || [ ${OPTION} = "--run" ]; then
        echo  "run"
    elif [ ${OPTION} = "-f" ] || [ ${OPTION} = "--front" ]; then
        echo "frontend"
    elif [ ${OPTION} = "-d" ] || [ ${OPTION} = "--down" ]; then
        echo "shutdown"
    else
        echo "None"
    fi
}
OPTION=`eoption ${1}`


if [ ${OPTION} == "None" ]; then
  phelp ${0}
  exit 1
fi

BUILD_IMG=${2}
BUILD_PATH=${3}
if [ ${#BUILD_PATH} -gt 0 ];then
    #TODO 待处理后续设置成 BUILD PATH
    PB_PATH="$( cd "$( dirname "$BUILD_PATH"  )" && pwd  )"
    BUILD_PATH="-f $BUILD_PATH"
else
    PB_PATH="$( pwd )"
fi

if [ ${OPTION} = "shutdown" ]; then
    echo -e "[\033[32m-\033[0m] no building executed"
elif [ ${BUILD_IMG} = "-b" ] || [ ${BUILD_IMG} = "--build" ]; then
    echo -e "[\033[32m+\033[0m] image will building at:"
    echo "${PB_PATH}"
    docker-compose $BUILD_PATH build
    #TODO 待处理后续设置成 BUILD PATH
    echo -e "[\033[32m+\033[0m] build executed "
else
    echo -e "[\033[32m-\033[0m] no building executed"
fi

if [ ${OPTION} = "run" ]; then
    # ================================
    # run image background
    # ================================
    docker-compose $BUILD_PATH up -d 
    echo -e "[\033[32m+\033[0m] ${OPTION} executed"
elif [ ${OPTION} = "frontend" ]; then
    # ================================
    # run image frontend
    # ================================
    echo -e "[\033[32m+\033[0m] ${OPTION} will be executed"
    docker-compose $BUILD_PATH up

elif [ ${OPTION} = "shutdown" ]; then
    # ================================
    # shutdown image
    # ================================
    docker-compose $BUILD_PATH down
    echo -e "[\033[32m+\033[0m] ${OPTION} executed"
fi
