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
    if [ "$?" == "1" ]; then
        echo -e "Соединение ${c_lGreen}установлено!${c_Default}"
    else
        echo -e "Соединение ${c_lRed}не установлено!\nДля работы установщика нужно интернет соединение.${c_Default}"
        return
    fi
}

preset(){
echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
}

check_internet
preset

#lsblk