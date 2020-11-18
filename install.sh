#!/bin/bash

                        #Colors
#---------------------------------------------------

c_Default="\e[39m"
c_Black="\e[30m"
c_White="\e[97m"
c_Red="\e[31m"
c_Green="\e[32m"
c_Yellow="\e[33m"
c_Blue="\e[34m"
c_Magenta="\e[35m"
c_Cyan="\e[36m"
c_lGray="\e[37m"
c_dGray="\e[90m"
c_lRed="\e[91m"
c_lGreen="\e[92m"
c_lYellow="\e[93m"
c_lBlue="\e[94m"
c_lMagenta="\e[95m"
c_lCyan="\e[96m"

#---------------------------------------------------

check_internet(){
    echo -e "Проверка соединения ..."
    ping -c 5 archlinux.org > /dev/null
    if [ "$?" == "0" ]; then
        echo -e "Соединение ${c_lGreen}установлено!${c_Default}"
    else
        echo -e "Соединение ${c_lRed}не установлено!\nДля работы установщика нужно интернет соединение.${c_Default}"
        exit 0
    fi
}

set_ru_lang(){
    echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen
    echo "LANG=ru_RU.UTF-8" > /etc/locale.conf
    echo "LOCALE=ru_RU.UTF-8" >> /etc/vconsole.conf
    echo "KEYMAP=ru" >> /etc/vconsole.conf
    echo "FONT=cyr-sun16" >> /etc/vconsole.conf
    locale-gen
    loadkeys ru
    setfont cyr-sun16
}


#selectdisk(){ 

#}
#selectdisk
echo -e "${c_Yellow}Список устройств:${c_Default}"
lsblk -d -p -n -l -o NAME,SIZE -e 7,11

#set_ru_lang
#clear
#check_internet
             read -p "Устройство: " device
             parted ${device} mklabel gpt
             sgdisk ${device} -n=1:0:+1024M -t=1:ef00
             swapsize=$(cat /proc/meminfo | grep MemTotal | awk '{ print $2 }')
             swapsize=$((${swapsize}/1000))"M"
             sgdisk ${device} -n=3:0:+${swapsize} -t=3:8200
             sgdisk ${device} -n=4:0:0
             if [ "${device::8}" == "/dev/nvm" ]; then
                 bootdev=${device}"p1"
                 swapdev=${device}"p3"
                 rootdev=${device}"p4"
             else
                 bootdev=${device}"1"
                 swapdev=${device}"3"
                 rootdev=${device}"4"
             fi
             efimode="1"

#lsblk
