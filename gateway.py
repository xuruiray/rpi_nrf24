#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example program to send packets to the radio
#
# João Paulo Barraca <jpbarraca@gmail.com>
#

from nrf24 import NRF24
import time

pipes = [[0x34, 0x43, 0x10, 0x10, 0x01],[0x24,0x24,0x14,0x15,0x02], [0x13,0x25,0x35,0x46,0x04]]

radio = NRF24()
radio.begin(0, 0, 25, 24) #Set CE and IRQ pins

radio.init_in_my_way()
radio.setPayloadSize(32)

i = 0
data = [1,2,3]
while True:

    radio.openWritingPipe(pipes[i])
    radio.openReadingPipe(0, pipes[i])

    radio.stopListening()
    radio.write("01234567890123456789012345678901")
    radio.startListening()
    
    t_s = time.time()
    while not radio.available([0],False):
        t_e = time.time()
        if t_e-t_s > 0.1:
            break
        continue
   
    if t_e-t_s > 0.1:
        continue

    recv_buffer = []
    radio.read(recv_buffer)
    #print(recv_buffer[0]-48)
  
    time.sleep(0.08)
    
    data[i]=recv_buffer[0]-48
    i=i+1
    if i==3:
        print data
        i=0

