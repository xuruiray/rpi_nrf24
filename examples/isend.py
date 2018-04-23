#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example program to send packets to the radio
#
# João Paulo Barraca <jpbarraca@gmail.com>
#

from nrf24 import NRF24
import time

pipes = [[0x34, 0x43, 0x10, 0x10, 0x01], [0x34, 0x43, 0x10, 0x10, 0x01]]

radio = NRF24()
radio.begin(0, 0, 25, 24) #Set CE and IRQ pins

radio.init_in_my_way()
radio.setPayloadSize(32)
radio.openWritingPipe(pipes[1])
radio.openReadingPipe(0, pipes[0])

#radio.startListening()
#radio.stopListening()

radio.printDetails()

while True:
    radio.write("01234567890123456789012345678901")
    radio.printDetails()

