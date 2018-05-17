#!/usr/bin/python
# -*- coding: utf-8 -*-

from nrf24 import NRF24
import time
import requests
import string
import json

#参数
max_retry_time  = 8
irq_wait_timeout = 0.1
scan_interval = 0.15

#设备相关
pipes = [[0x34, 0x43, 0x10, 0x10, 0x01],[0x24,0x24,0x14,0x15,0x02], [0x13,0x25,0x35,0x46,0x04]]
max_device_num = 3 
addrList = []

#初始化 RF24
radio = NRF24()
radio.begin(0, 0, 25, 24) #Set CE and IRQ pins
radio.setPayloadSize(32)
radio.write_register(NRF24.EN_AA,0x01)
radio.write_register(NRF24.EN_RXADDR,0x01)
radio.write_register(NRF24.SETUP_RETR,0x1a)
radio.write_register(NRF24.RF_CH,40)
radio.write_register(NRF24.RF_SETUP,0x0e)
radio.write_register(NRF24.CONFIG,0x0c)

#API相关
host = 'http://58.87.89.234'
#host = 'http://192.168.1.8:8080'
upload_url = host + '/sensor/saveData'
downloadaddr_url = host + '/sensor/loadAllAddr'

#初始化变量
device_num = 0
retry_time = 5

#采集数据
json_data = ""
full_sign = 20
test_data = [full_sign,full_sign,full_sign]
test_data_str = ""

class SensorAddrTemp(object):
    sensor_name = 'sn'
    sensor_addr = [0,0,0,0,0]
    def __init__(self,name,addr):
        self.sensor_name = name
        self.sensor_addr = addr.split(',')
        for i in range(len(self.sensor_addr)):
            self.sensor_addr[i] = int(self.sensor_addr[i])

try:
    resp = requests.get(downloadaddr_url,timeout=25)
    addrs = json.loads(resp.text)
    for addr in addrs:
        s = SensorAddrTemp(addr['sensor_name'],addr['sensor_addr'])
        addrList.append(s)
except requests.exceptions.ConnectTimeout:        
    print "timeout"
except requests.exceptions.ReadTimeout:
    print "timeout"
except requests.exceptions.ConnectionError:
    print "timeout"
                
for v in addrList:
    print v.sensor_addr
    print v.sensor_name

while True:
    
    #nrf24 config
    radio.openWritingPipe(addrList[device_num].sensor_addr)
    radio.openReadingPipe(0,addrList[device_num].sensor_addr)

    radio.stopListening()
    radio.write("01234567890123456789012345678901")
    radio.startListening()
    
    #nrf24 timeout op
    t_s = time.time()
    while not radio.available([0],False):
        t_e = time.time()
        if t_e-t_s > irq_wait_timeout:
            break
        continue

    if t_e-t_s > irq_wait_timeout:
        test_data[device_num] -= 1
        if test_data[device_num] < 0:
            test_data[device_num] = 0
        retry_time += 1
        if retry_time < max_retry_time:
            continue
        else:  
            device_num += 1
            if device_num == 3:
                device_num = 0            
            continue
    else:
        test_data[device_num] += 1
        if test_data[device_num] > full_sign:
            test_data[device_num] = full_sign
        

    recv_buffer = []
    radio.read(recv_buffer)
 
    # string op
    for i in range(len(recv_buffer)):
        recv_buffer[i] = chr(recv_buffer[i])
    try: 
        json_data = json_data + '{"sensorName":"' + addrList[device_num].sensor_name + '","dataMap":' + string.strip(''.join(recv_buffer),' ').replace('{','{\"').replace(',',',\"').replace(':','\":') + '},'
    except UnicodeDecodeError:
        print recv_buffer

    time.sleep(scan_interval)
        
    device_num += 1
    if device_num == max_device_num:
        test_data_str =' {"sensorName":"NRF24L01","dataMap":{"' + addrList[0].sensor_name + '":%d,"'+addrList[1].sensor_name+'":%d,"'+addrList[2].sensor_name+'":%d}},'
        test_data_str = test_data_str%(test_data[0],test_data[1],test_data[2])
        json_data +=  test_data_str
        json_data = '[' + string.strip(json_data,',') + ']'
        print json_data 
        print time.time()
        print test_data

        try:
            resp = requests.post(upload_url, json_data,timeout=10)
        except requests.exceptions.ConnectTimeout:        
            print "timeout"
        except requests.exceptions.ReadTimeout:
            print "timeout"
        except requests.exceptions.ConnectionError:
            print "timeout"
    
        json_data = ""
        device_num = 0


