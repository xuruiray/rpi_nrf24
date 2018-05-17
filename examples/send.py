#!/usr/bin/python
# -*- coding: utf-8 -*-

from nrf24 import NRF24
import time

pipes = [[0x34, 0x43, 0x10, 0x10, 0x01], [0x34, 0x43, 0x10, 0x10, 0x01]]

radio = NRF24()
radio.begin(0, 0, 22, 18) #Set CE and IRQ pins

radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x28)

radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MAX)

radio.openWritingPipe(pipes[1])
radio.openReadingPipe(0, pipes[0])

#radio.startListening()
#radio.stopListening()

radio.printDetails()

while True:
    radio.write("PING")

