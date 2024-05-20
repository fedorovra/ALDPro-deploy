#!/usr/bin/env python3

import locale
import dialog
import re
import os
import ipaddress
from jinja2 import Template
import ansible_runner
import sys


def network_addr_check(address, netmask):
    try:
        ipaddress.ip_interface("{}/{}".format(address, netmask))
    except:
        return False
    else:
        return True

domain_regex = r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
hostname_regex = r'^((?![_-])[a-z0-9-_]{1,63}(?<![_-]))$'

inventory_template = """
all:
  hosts:
    localhost:
      ansible_user: ansible
      ansible_become: true
      role: first_dc
      admin_password: {{ passw }}
      FQDN: {{ fqdn }}
      ip_address: {{ ip }}
      ip_netmask: {{ mask }}
      ip_gateway: {{ gw }}
"""

locale.setlocale(locale.LC_ALL, '')

d = dialog.Dialog(dialog="dialog")
d.set_background_title("Конфигуратор ALDPro")

menu_text = "Выберите необходимую опцию"
menu_choices = [
                ("1", "Установка первого контроллера"), 
                ("2", "Установка второго контроллера"), 
                ("3", "Установка чего-нибудь еще")
]
while True:
    code, tag = d.menu(menu_text, height=None, width=None, menu_height=None, choices=menu_choices)
    if code == d.CANCEL or code == d.ESC:
        if d.yesno("Вы хотите выйти из конфигуратора?", height=None, width=None) == "ok":
            break

    if tag == "1":
        password1 = ""
        password2 = ""
        hostname = ""
        domain = ""
        ip = ""
        mask = ""
        gateway = ""

        form_text = "Введите настройки первичного контроллера. \nВсе поля обязательны для заполнения"
        
        while True:
            form_fields = [
                            ("Домен:",                         1, 1, domain,    1, 32, 20, 0, 0),
                            ("Имя компьютера:",                2, 1, hostname,  2, 32, 20, 0, 0),
                            ("IP-адрес:",                      3, 1, ip,        3, 32, 20, 0, 0),
                            ("Маска сети:",                    4, 1, mask,      4, 32, 20, 0, 0),
                            ("Шлюз:",                          5, 1, gateway,   5, 32, 20, 0, 0),
                            ("Задайте пароль администратора:", 6, 1, password1, 6, 32, 20, 0, 1),
                            ("Повторите ввод пароля:",         7, 1, password2, 7, 32, 20, 0, 1),
            ]

            code, fields = d.mixedform(form_text, form_fields, insecure=True)
            if fields:
                domain, hostname, ip, mask, gateway, password1, password2 = fields
            if code == d.OK:
                if not domain or not hostname or not ip or not mask or not gateway or not password1 or not password2:
                    d.msgbox("Заполнены не все поля!", height=None, width=None)
                    continue
                if password1 != password2:
                    d.msgbox("Пароли не совпадают!", height=None, width=None)
                    continue
                if not network_addr_check(ip, mask):
                    d.msgbox("Ошибка во вводимых данных!\nПроверьте, пожалуйста, корректность IP-адреса и маски сети", height=None, width=None)
                    continue
                if not network_addr_check(gateway, mask):
                    d.msgbox("Ошибка во вводимых данных!\nПроверьте, пожалуйста, корректность адреса шлюза", height=None, width=None)
                    continue
                if ipaddress.ip_interface("{}/{}".format(ip, mask)).network != ipaddress.ip_interface("{}/{}".format(gateway, mask)).network:
                    d.msgbox("Ошибка во вводимых данных!\nIP-адрес контроллера и шлюз в разных сетях", height=None, width=None)
                    continue
                if not re.match(domain_regex, domain):
                    d.msgbox("Домен содержит недопустимые символы!", height=None, width=None)
                    continue
                if not re.match(hostname_regex, hostname):
                    d.msgbox("Имя компьютера содержит недопустимые символы!", height=None, width=None)
                    continue
                with open("/home/localadmin/ALDPro-deploy/inventory/hosts", "w+") as output:
                    output.write(Template(inventory_template).render(fqdn="{}.{}".format(hostname, domain), 
                                                                     ip=ipaddress.ip_interface("{}/{}".format(ip, mask)).ip,
                                                                     mask=ipaddress.ip_interface("{}/{}".format(ip, mask)).netmask,
                                                                     gw=ipaddress.ip_interface("{}/{}".format(gateway, mask)).ip,
                                                                     passw=password1))
                
                template = """
                           задача 1 : {{ tags[0]["status"] }}
                           задача 2 : {{ tags[1]["status"] }}
                           задача 3 : {{ tags[2]["status"] }}
                           задача 4 : {{ tags[3]["status"] }}
                           задача 5 : {{ tags[4]["status"] }}
                           задача 6 : {{ tags[5]["status"] }}
                           задача 7 : {{ tags[6]["status"] }}
                           задача 8 : {{ tags[7]["status"] }}
                           задача 9 : {{ tags[8]["status"] }}
                           задача 10 : {{ tags[9]["status"] }}
                           задача 11 : {{ tags[10]["status"] }}
                """
                
                tags = [ 
                        { "name" : "NetworkManager", "progress" : 10, "status" : "В очереди", "skip" : False },
                        { "name" : "interfaces", "progress" : 20, "status" : "В очереди", "skip" : False },
                        { "name" : "resolv1", "progress" : 30, "status" : "В очереди", "skip" : False },
                        { "name" : "hostname", "progress" : 40, "status" : "В очереди", "skip" : False },
                        { "name" : "hosts", "progress" : 50, "status" : "В очереди", "skip" : False },
                        { "name" : "update", "progress" : 60, "status" : "В очереди", "skip" : False },
                        { "name" : "install-aldpro-mp", "progress" : 70, "status" : "В очереди", "skip" : False },
                        { "name" : "resolv2", "progress" : 80, "status" : "В очереди", "skip" : False },
                        { "name" : "deploy", "progress" : 90, "status" : "В очереди", "skip" : False },
                        { "name" : "firefox", "progress" : 98, "status" : "В очереди", "skip" : False },
                        { "name" : "post-deploy", "progress" : 99, "status" : "В очереди", "skip" : False },
                ]

                d.gauge_start(text=Template(template).render(tags=tags), height=20, percent=0)

                for tag in tags:
                    if not tag["skip"]:
                        tag["status"] = "В работе"
                        d.gauge_update(tag["progress"], text=Template(template).render(tags=tags), update_text=True)

                        runner_config = ansible_runner.RunnerConfig(
                                                        private_data_dir="/home/localadmin/ALDPro-deploy", 
                                                        playbook="playbook.yaml", 
                                                        tags="role::deploy-ald-servers:{}".format(tag["name"]),
                                                        quiet=True,
                                                        suppress_ansible_output=True,
                        )
                        runner_config.prepare()
                        runner_instance = ansible_runner.Runner(config=runner_config)
                        runner_instance.run()
                        if runner_instance.rc != 0:
                            d.msgbox("Что то пошло не так!", height=None, width=None)
                            sys.exit()
                        
                        tag["status"] = "Завершено"
                    else:
                        tag["status"] = "Пропускаем"

                d.gauge_update(100, text=Template(template).render(tags=tags), update_text=True)
                d.gauge_stop()

                d.msgbox("Работы завершены!", height=None, width=None)
                # ansible_runner.run(
                #                    private_data_dir="/home/localadmin/ALDPro-deploy", 
                #                    module="shell", 
                #                    module_args="reboot", 
                #                    host_pattern="localhost", 
                #                    quiet=True,
                # )
                os.system('clear')
                sys.exit()


            if code == d.CANCEL or code == d.ESC:
                if d.yesno("Вы хотите выйти из меню?", height=None, width=None) == "ok":
                    os.system('clear')
                    break
                
    if tag == "2":
        print("2")
        break