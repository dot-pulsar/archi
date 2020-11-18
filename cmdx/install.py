import os
from shell import sh
import json

sh('yes | pacman -Sy --needed python-pip')
sh('pip install termcolor')

from termcolor import colored


def print_no_such_opt():
    print(colored('\\\\\ There is no such option!', 'red'))


def print_label(label: str):
    print(colored(label, 'green'))


def print_text(text: str):
    print(colored(text, 'white'))


def input_opt():
    return input(colored('>>> ', 'blue'))


class Locale:
    def __init__(self, j: str):
        data = json.load(j)
        self.text_choose_language = data['text_choose_language']
        self.text_select_system_language = data['text_select_system_language']


def load_locale(filename_json: str):
    with open(filename_json, "r") as read_file:
        return Locale(read_file)


lc = load_locale('en_US.json')
# =====================================================================


def set_ru_lan():
    print(colored('Installing russian language...', 'green'))
    lc_gen = open('/etc/locale.gen', 'a')
    lc_gen.write('\nru_RU.UTF-8 UTF-8')
    lc_gen.close()

    lc_conf = open('/etc/locale.conf', 'w')
    lc_conf.write('LANG=ru_RU.UTF-8')
    lc_conf.close()

    vconsole = open('/etc/vconsole.conf', 'w')
    vconsole.write(
        '\nLOCALE=ru_RU.UTF-8' +
        '\nKEYMAP=ru' +
        '\nFONT=cyr-sun16')
    vconsole.close()

    sh("locale-gen")
    sh("loadkeys ru")
    sh("setfont cyr-sun16")
    print(colored('Русский язык установлен!', 'green'))


def check_ping():
    print(colored('Проверка соединения ...', 'green'))
    response = sh('ping -c 2 archlinux.org').code
    if response == 0:
        print(colored('Соединенение установлено!', 'green'))
    else:
        print(colored('Соединение не установлено!' +
                      '\nДля работы установщика нужно интернет соединение.', 'red'))
    press_enter()


def press_enter():
    input("Press Enter to continue...")


def change_language():
    global lc
    languages = {
        '1': 'English:en_US.UTF-8 UTF-8:en_US.json',
        '2': 'Russian:ru_RU.UTF-8 UTF-8:ru_RU.json'
    }

    print(lc.text_choose_language)
    for lang in languages.items():
        value = lang[1].split(':')
        print(f'[{lang[0]}] {value[0]}')

    while True:
        choice = input(lc.text_select_system_language)
        selected_lang = languages.get(choice, 'invalid_choice')
        if not selected_lang == "invalid_choice":
            value = selected_lang.split(':')
            lc = load_locale(value[2])
            set_language(value[1])
            break


def set_language(lang):
    f = open('/etc/locale.gen', 'rt')
    data = f.readlines()
    for line in data:
        index = data.index(line)
        if lang in line and not line == '##  en_US.UTF-8 UTF-8\n':
            data.remove(line)
            new_line = line.replace('#', '', 1)
            data.insert(index, new_line)
        if not line.startswith('#') and not 'en_US.UTF-8 UTF-8' in line:
            data.remove(line)
            new_line = line.replace(line, '#' + line)
            data.insert(index, new_line)
    f.close()

    f = open('/etc/locale.gen', 'wt')
    f.writelines(data)
    f.close()
    sh("locale-gen", True)


# print('Arch Linux Installer (01.12.2021)')
# print()
# print('Link: https://github.com/dot-pulsar/archi')
# change_language()

# =======================================================================


class Device:
    def __init__(self, path: str, is_efi: bool):
        self.path = path
        self.is_efi = is_efi
        if '/dev/nvm' in path:
            self.boot = path + 'p1'
            self.swap = path + 'p2'
            self.home = path + 'p3'
        else:
            self.boot = path + '1'
            self.swap = path + '2'
            self.home = path + '3'


def select_device():
    devices = {}
    i = 0
    sh.clear()
    print_label('===================================')
    #print(colored('NAME             TYPE FSTYPE SYZE', 'green'))
    sh('lsblk -n -p -o NAME,TYPE,FSTYPE,SIZE -e 7,11', True)
    print_label('===================================')
    temp_devices = sh('lsblk -d -p -n -l -o NAME -e 7,11').value
    print_label('\n(Installation devices)')
    for temp_device in temp_devices.split('\n'):
        if temp_device == '':
            break
        i += 1
        devices.update({str(i): temp_device})

    for device in devices.items():
        print(f'{colored(f"[{device[0]}]","yellow")} {device[1]}')

    while True:
        selected_devices = devices.get(input_opt(), 'invalid_choice')
        if not selected_devices == 'invalid_choice':
            return str(selected_devices)
        else:
            print_no_such_opt()


def swap_size():
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    return str(int(mem_bytes/(1024.**2))) + 'M'


def auto_partition_device_gpt():
    device = select_device()
    sh(f'parted -s {device} mklabel gpt', True)
    sh(f'sgdisk {device} -n=1:0:+1024M -t=1:ef00', True)
    sh(f'sgdisk {device} -n=2:0:+{swap_size()} -t=2:8200', True)
    sh(f'sgdisk {device} -n=3:0:0', True)
    return Device(device, True)


def auto_partition_device_dos():
    device = select_device()
    sh(f'parted -s {device} mklabel msdos')
    sh(f'echo -e "n\np\n1\n\n+512M\na\nw" | fdisk {device}')
    sh(f'echo -e "n\np\n2\n\n+{swap_size()}\nt\n\n82\nw" | fdisk {device}')
    sh(f'echo -e "n\np\n3\n\n\nw" | fdisk {device}')
    return Device(device, False)


def format_boot_partition(device: Device):
    print(f'Formatting {colored(device.boot,"red")} partition')
    if device.is_efi:
        sh(f'yes | mkfs.fat {device.boot}')
    else:
        sh(f'yes | mkfs.ext4 {device.boot}')


def format_swap_partition(device: Device):
    print(f'Formatting {colored(device.swap,"red")} partition')
    sh(f'yes | mkswap {device.swap}')


def format_home_partition(device: Device):
    print(f'Formatting {colored(device.home,"red")} partition')
    sh(f'yes | mkfs.ext4 {device.home}')


def mount_partitions(device: Device):
    print(
        f'Mounting {colored(device.home,"red")} {colored("<home>","blue")} partition in {colored("/mnt","red")}')
    sh(f'mount {device.home} /mnt', True)
    sh('mkdir /mnt/{boot,home}')
    if device.is_efi:
        sh('mkdir /mnt/boot/efi')
        print(
            f'Mounting {colored(device.boot,"red")} {colored("<boot>","blue")} partition in {colored("/mnt/boot/efi","red")}')
        sh(f'mount {device.boot} /mnt/boot/efi', True)
    else:
        print(
            f'Mounting {colored(device.boot,"red")} {colored("<boot>","blue")} partition in {colored("/mnt/boot","red")}')
        sh(f'mount {device.boot} /mnt/boot', True)
    print(
        f'Enabling {colored(device.swap,"red")} {colored("<swap>","blue")} partition')
    sh(f'swapon {device.swap}', True)


def umount_partitions(device: Device):
    print_label('Unmounting all partitions')
    sh('umount -R /mnt', True)
    sh(f'swapoff {device.swap}', True)


def install_opts(index: int):
    sh.clear()
    print_label('(Installation steps)')
    opts = {
        1: 'pacstrap',
        2: 'genfstab',
        3: 'mkinitcpio',
        4: 'grub-install',
        5: 'grub-mkconfig'
    }
    for opt in opts.items():
        if opt[0] >= index:
            print(f'{colored(f"[{opt[0]}]","yellow")} {opt[1]}')
        else:
            print(
                f'{colored(f"[{opt[0]}]","yellow")} {colored(opt[1],"blue")}')


def install(device: Device):
    chroot = 'arch-chroot /mnt'

    install_opts(1)
    sh('pacstrap /mnt base base-devel linux linux-firmware grub dhcpcd', True)
    if device.is_efi:
        sh('pacstrap /mnt efibootmgr', True)

    install_opts(2)
    sh('genfstab -p /mnt >> /mnt/etc/fstab', True)

    install_opts(3)
    sh(f'{chroot} mkinitcpio -p linux', True)
    #sh(f'{chroot} passwd root', True)

    install_opts(4)
    if device.is_efi:
        sh(f'{chroot} grub-install', True)
    else:
        sh(f'{chroot} grub-install {device.path}', True)

    install_opts(5)
    sh(f'{chroot} grub-mkconfig -o /boot/grub/grub.cfg', True)

    install_opts(6)
    print_label('Set a password for ROOT')
    sh(f'{chroot} passwd root', True)


def end():
    print_label('(Device partitioning modes)')
    print(
        f'{colored("[1]","yellow")} Automatic partitioning DOS\n' +
        f'{colored("[2]","yellow")} Automatic partitioning GPT (EFI)')
    while True:
        opt = input_opt()
        if opt == '1':
            device = auto_partition_device_dos()
            break
        elif opt == '2':
            device = auto_partition_device_gpt()
            break
        else:
            print_no_such_opt()

    sh.clear()

    format_boot_partition(device)
    format_swap_partition(device)
    format_home_partition(device)
    umount_partitions(device)
    mount_partitions(device)
    install(device)
    umount_partitions(device)
    
end()