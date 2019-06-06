#!/bin/bash
#version=1.0

MAIN=$*
num=0
UPGRADE_DIR="/tmp/dma-upgrade"
DMA_DIR="/tmp/dma/bin"
OFFLINE_MSG_DIR="/home/duhj/dma-data/mqtt-offline-msgs"
MQTT_MSG_URL="http://127.0.0.1:7788/mqtt/publish/offlinecache"

cp_check(){
    if [ $? -eq 0 ];then
        cpstatus=ok
    else
        cpstatus=err
    fi
}

append_upgrade_result(){
    

    if [ ${num} -eq 0 ];then
        upgrade_result="${upgrade_result}\
            {\
                \"name\":\"${name}\",\
                \"cpstatus\":\"${cpstatus}\",\
                \"ver\":\"${ver}\"\
            }"
    else
        upgrade_result="${upgrade_result},\
            {\
                \"name\":\"${name}\",\
                \"cpstatus\":\"${cpstatus}\",\
                \"ver\":\"${ver}\"\
            }"
    fi

    num=1
}

init(){
    if [ ! -n "${CMD_ID}" ];then
        CMD_ID=0
    fi

    if [ ! -n "${CMD_FROM}" ];then
        CMD_FROM=""
    fi

    if [ -n "${DMA_UPGRADE_PATH}" ];then
        UPGRADE_DIR=${DMA_UPGRADE_PATH}
    fi

    upgrade_result="{\
    \"from\":\"upgrade.sh\",\
    \"topic\":\"dma/resp/upgrade\",\
    \"qos\":2, \
    \"payload\":\
    {\
        \"id\":${CMD_ID},\
        \"time\":$(date +%s),\
        \"from\":\"${CMD_FROM}\",\
        \"stage\":\"finished\",\
        \"d\":[\
        "
}

publish_upgrade_start_msg(){
    upgrade_start_msg="{\
    \"from\":\"upgrade.sh\",\
    \"topic\":\"dma/resp/upgrade\",\
    \"qos\":2, \
    \"payload\":\
    {\
        \"id\":${CMD_ID},\
        \"time\":$(date +%s),\
        \"from\":\"${CMD_FROM}\",\
        \"stage\":\"start\"\
    }\
}"
    echo ${upgrade_start_msg} > /tmp/upgrade_start_msg.txt
    curl -H "token: MQRROJMAjKxaUy&kGMLoGc7YJDLLaiTu" -d @/tmp/upgrade_start_msg.txt $MQTT_MSG_URL
    # in case of sending failed
    if [ $? -ne 0 ];then
        echo ${upgrade_start_msg} > ${OFFLINE_MSG_DIR}/$(date +%s)-31.cache
    fi
}

publish_upgrade_finish_msg(){
end_tag="\
        ]\
    }\
}"
    upgrade_finish_msg="${upgrade_result} ${end_tag}"
    echo ${upgrade_finish_msg} > /tmp/upgrade_finish_msg.txt
    curl -H "token: MQRROJMAjKxaUy&kGMLoGc7YJDLLaiTu" -d @/tmp/upgrade_finish_msg.txt $MQTT_MSG_URL
    # in case of send failed
    if [ $? -ne 0 ];then
        echo ${upgrade_finish_msg} > ${OFFLINE_MSG_DIR}/$(date +%s)-31.cache
    fi
}

kill_process() {
    pids=`ps aux | grep "$1" | grep -v grep | grep -v PPID | awk '{print $2}'`
    for pid in $pids
        do
            echo "app $1 (pid: $pid) was killed successfully"
            kill -9 $pid
        done
}

need_update_dma_file() {
    dmaFile=$1
    dmaConf="${dmaFile}.ini"

    # dma file is missing
    if [ ! -f "${DMA_DIR}/${dmaFile}" ] || [ ! -f "${DMA_DIR}/${dmaConf}" ]; then
        return 1
    fi

    # upgrade exe file exists
    if [ -f "${UPGRADE_DIR}/${dmaFile}"  ]; then
        md5DmaFile=`md5sum ${DMA_DIR}/${dmaFile} | awk {'print $1'}`
        md5DmaFileNew=`md5sum ${UPGRADE_DIR}/${dmaFile} | awk {'print $1'}`
        if [ "$md5DmaFile" != "$md5DmaFileNew" ]; then 
            return 1
        fi        
    fi

    # upgrade conf file exists
    if [ -f "${UPGRADE_DIR}/${dmaConf}"  ]; then
        md5DmaConf=`md5sum ${DMA_DIR}/${dmaConf} | awk {'print $1'}`
        md5DmaConfNew=`md5sum ${UPGRADE_DIR}/${dmaConf} | awk {'print $1'}`
        if [ "$md5DmaConf" != "$md5DmaConfNew" ]; then 
            return 1
        fi        
    fi   

    return 0
}

need_update_file() {
    file=$1

    if [ ! -f "${DMA_DIR}/${file}" ]; then
        return 1
    fi

    if [ -f "${UPGRADE_DIR}/${file}" ]; then
        md5File=`md5sum "${DMA_DIR}/${file}" | awk {'print $1'}`
        md5FileNew=`md5sum "${UPGRADE_DIR}/${file}" | awk {'print $1'}`

        if [ "$md5File" != "$md5FileNew" ]; then 
            return 1
        fi 
    fi

    return 0    
}

dma() {
    echo "executing dma..."

    # create backup dir
    mkdir -p "${DMA_DIR}/bak"
    mkdir -p "${DMA_DIR}/bak/ext"

    # check dma exe upgrade 
    for file in "dma.msghub" "dma.monitor" "dma.cmdhandler"
        do
            need_update_dma_file ${file}

            # need upgarde
            if [ $? -eq 1 ];then
                dmaFile=${file}
                dmaConf="${dmaFile}.ini"

                # upgrade status
                name=${file}
                cpstatus=ignore
                ver=ignore

                # kill process
                kill_process $dmaFile

                if [ -f "${UPGRADE_DIR}/${dmaFile}" ]; then
                    # backup
                    cp -rf ${DMA_DIR}/${dmaFile} ${DMA_DIR}/bak/${dmaFile}
                    # updage
                    cp -rf ${UPGRADE_DIR}/${dmaFile} ${DMA_DIR}/${dmaFile}

                    cp_check
                fi

                if [ -f "${UPGRADE_DIR}/${dmaConf}" ]; then
                    # backup
                    cp -rf ${DMA_DIR}/${dmaConf} ${DMA_DIR}/bak/${dmaConf}
                    # upgrade
                    cp -rf ${UPGRADE_DIR}/${dmaConf} ${DMA_DIR}/${dmaConf}

                    cp_check
                fi

                chmod +x ${DMA_DIR}/${dmaFile}

                ver=$(${DMA_DIR}/${dmaFile} --version)

                append_upgrade_result

                #restart
                ${DMA_DIR}/${dmaFile}
            fi

        done

    # check other files
    for file in "dma.daemon.sh" "zlog.conf" "ext/zlog.conf" "ext/dma.upgrade.cmd"
        do
            name=$file
            need_update_file ${name}

            if [ $? -eq 1 ];then
                cpstatus=ignore
                ver=ignore

                if [ "$name" == "dma.daemon.sh" ]; then 
                    kill_process ${name}
                fi 

                if [ -f "${UPGRADE_DIR}/${name}" ]; then
                    # backup
                    cp -rf ${DMA_DIR}/${name} ${DMA_DIR}/bak/${name}
                    # upgrade
                    cp -rf ${UPGRADE_DIR}/${name} ${DMA_DIR}/${name}

                    cp_check
                fi

                if [ "$name" == "dma.daemon.sh" ]; then 
                    chmod +x ${DMA_DIR}/${name}
                    ver=`head -3 ${DMA_DIR}/${name}| grep version  | awk -F "=" {'print $2'}`
                    ${DMA_DIR}/${name} &
                fi 

                if [ "$name" == "ext/dma.upgrade.cmd" ]; then 
                    chmod +x ${DMA_DIR}/${name}
                    ver=$(${DMA_DIR}/${name} --version)
                fi 

                append_upgrade_result
            fi
        done
}

start_working(){

    publish_upgrade_start_msg

    ${UPGRADE_DIR}/INSTALL

    echo "1" > /tmp/dma-upgrade-result

    publish_upgrade_finish_msg
}

init
start_working

