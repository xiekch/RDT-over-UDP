import socket as st
import pickle
from packet import Packet
import time
import math


class RDTRecv:

    def __init__(self, addr):
        self.recvAddr = addr
        self.MSS = 500
        self.seqNum = 0
        self.ackNum = 0
        self.started=False
        self.windowSize = 2000

    def listen(self):
        self.recvSocket = st.socket(st.AF_INET, st.SOCK_DGRAM)
        self.recvSocket.bind(self.recvAddr)
        print('Running at %s:%s' % self.recvAddr)

    def close(self):
        if hasattr(self, 'recvSocket'):
            self.recvSocket.close()
        print('End of receiver')

    def start(self):
        self.seqNum = 0
        self.ackNum = 1
        self.started = True

    def end(self):
        self.started = False

    def receiveData(self):
        dataList = []
        packetList = self.receivePacket()
        for packet in packetList:
            dataList.append(packet['data'])
        return (dataList, self.started)

    def receivePacket(self):
        packetDict = {}
        finish = False
        flag = 0
        while not finish:
            rawData, addr = self.recvSocket.recvfrom(200+self.MSS)
            packet = pickle.loads(rawData)

            # print(packet['seqNum'])
            # print('pkt:\n'+str(packet))
            if not self.started:
                if packet['Syn'] == True:
                    self.start()
            else:
                if packet['seqNum'] >= self.ackNum and packet['seqNum'] not in packetDict:
                    packetDict[packet['seqNum']] = packet
                if packet['seqNum'] == self.ackNum:
                    #error
                    while self.ackNum in packetDict:
                        packet = packetDict[self.ackNum]
                        self.ackNum += len(pickle.dumps(packet['data']))
                        # print(str(self.ackNum))
                        if packet['Fin'] == True:
                            self.end()
                            finish = True
                            break

            # what if it loss?
            self.sendAck(addr)
            if len(packetDict) >= self.windowSize:
                finish = True

        # for k in dataList.keys():
        # RuntimeError: dictionary changed size during iteration
        for k in list(packetDict.keys()):
            if k > self.ackNum:
                packetDict.pop(k)
        return packetDict.values()

    def sendAck(self, addr):
        packet = Packet(b'', seqNum=self.seqNum,
                        ackNum=self.ackNum, Syn=False, Fin=False)
        pkt = packet.serialize()
        # print('ack:\n'+str(packet))
        self.recvSocket.sendto(pkt, addr)
