import json
import os
import random

import urllib.parse

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from lxml import etree


def crypto_encode(data, iv):
    key = b'1234567887654321'
    iv_bytes = iv.encode('utf-8')

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv_bytes), backend=default_backend())
    encryptor = cipher.encryptor()

    # 使用ZeroPadding填充
    padded_data = data.ljust((len(data) // 16 + 1) * 16, b'\0'.decode('utf-8'))

    ciphertext = encryptor.update(padded_data.encode('utf-8')) + encryptor.finalize()
    encrypted_data = base64.b64encode(ciphertext).decode('utf-8')

    return {'data': encrypted_data, 'iv': iv}


def is_internet_connected():
    try:
        requests.get('https://www.baidu.com', headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        }, timeout=3)
        return True
    except:
        return False


num = int(random.random() * 1000)

header = {
    'Host': '210.44.64.60',
    'Origin': 'http://210.44.64.60',
    'Referer': 'http://210.44.64.60/gportal/web/login',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

url = 'http://210.44.64.60/gportal/web/authLogin?round=' + str(int(random.random() * 1000))

if os.path.exists('config'):
    # 读取配置文件
    with open('config', 'r', encoding='utf-8') as file:
        jsondata = json.load(file)
        username = jsondata['username']
        password = jsondata['password']

    if not is_internet_connected():
        res = requests.get('http://210.44.64.60/gportal/web/login', headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        })

        cookie = res.cookies

        x = etree.HTML(res.text)

        sign_value = x.xpath('//*[@id="frmLogin"]/ul/input[9]//@value')[0]
        ip_value = x.xpath('//*[@id="frmLogin"]/ul/input[3]//@value')[0]
        nasname_value = x.xpath('//*[@id="frmLogin"]/ul/input[1]//@value')[0]
        pid_value = x.xpath('//*[@id="frmLogin"]/ul/input[7]//@value')[0]
        iv_value = x.xpath('//*[@id="iv"]//@value')[0]
        redirecturl_value = x.xpath('//*[@id="redirectUrl"]//@value')[0]
        redirecturl_value = urllib.parse.quote(redirecturl_value, safe="")
        protaltemplatedid_value = x.xpath('//*[@id="portalTemplateId"]//@value')[0]

        # 解密

        # 加密
        message = f'nasName={nasname_value}&nasIp=&userIp={ip_value}&userMac=&ssid=&apMac=&pid={pid_value}&vlan=&sign={sign_value}&iv={iv_value}&redirectUrl={redirecturl_value}&portalTemplateId={protaltemplatedid_value}&name={username}&password={password}'

        jsondata = crypto_encode(message, iv_value)
        # 发送POST请求
        response = requests.post(url, data=jsondata, headers=header, cookies=cookie, timeout=5)
        if response.status_code != 200 or response.json().get('info') == '页面超时':
            for i in range(15):
                print(f'认证失败，正在重试{i + 1}/15')
                response = requests.post(url, data=jsondata, headers=header, cookies=cookie, timeout=5)
                if response.status_code == 200 and response.json().get('info') != '页面超时':
                    print(response.status_code, response.json())
                    break
                if i + 1 == 15:
                    print('连接失败，请手动连接')
        else:
            print(response.status_code, response.json())
    else:
        print('已经联网')

else:
    jsondata = {
        "username": 'info',
        "password": "info"
    }
    with open('config', 'w', encoding='utf-8') as file:
        json.dump(jsondata, file, indent=4)
    for i in range(25):
        print('第一次运行，请修改配置，修改之后重新运行')
