import socket as st
import pickle
from packet import Packet
import time
import math
import threading


class RDTSend:

    def __init__(self, addr):
        self.sendAddr = addr
        self.sendSocket = st.socket(st.AF_INET, st.SOCK_DGRAM)
        self.timeout = 1
        self.congWin = 1
        self.threshold = 100
        self.MSS = 512
        self.seqNum = 0
        self.ackNum = 0
        self.sendAckNum = 0
        self.windowSize = 1000
        self.maxTimeout = 4
        self.started = False
        self.resendTimes=0

    def start(self):
        self.started = True
        self.seqNum = self.ackNum = self.sendAckNum = 0
        print('Send to %s:%s' % self.sendAddr)
        threading.Thread(target=self.count).start()
        packet = Packet(b'', seqNum=self.seqNum,
                        ackNum=self.ackNum, Syn=True, Fin=False)
        self.seqNum += 1
        self.rdtSend({0: packet})

    def end(self):
        packet = Packet(b'', seqNum=self.seqNum,
                        ackNum=self.ackNum, Syn=False, Fin=True)
        self.started = False
        self.seqNum += len(pickle.dumps(packet.packet['data']))
        self.rdtSend({packet.packet['seqNum']: packet})

    def close(self):
        self.started = False
        if hasattr(self, 'sendSocket'):
            self.sendSocket.close()
        print('End of sender')

    def sendPacket(self, packetList):
        for packet in packetList:
            self.sendSocket.sendto(packet.serialize(), self.sendAddr)

    def rdtSend(self, packetDict):
        startTime = time.time()
        self.sendPacket([p for p in packetDict.values()])
        self.waitForAck(packetDict, startTime)

    # resend times <5
    def sendData(self, dataList):
        packetDict = {}
        for i in range(len(dataList)):
            data = dataList[i]
            packet = Packet(data, seqNum=self.seqNum,
                            ackNum=self.ackNum, Syn=False, Fin=False)
            self.seqNum += len(pickle.dumps(packet.packet['data']))
            # print('pkt:\n'+str(packet))
            packetDict[packet.packet['seqNum']] = packet
            if (i+1) % self.congWin == 0:
                self.rdtSend(packetDict)
                packetDict = {}
        if packetDict:
            self.rdtSend(packetDict)

    def waitForAck(self, packetDict, startTime):
        # print('send '+str(self.seqNum))
        ackFinish = False
        resendTimes = 0
        duplicateTimes = 0
        timeout = False
        while not ackFinish:
            try:
                self.sendSocket.settimeout(self.timeout)
                ackNum = self.receiveAck()
                # print('ack:\n '+str(ackNum))
                if ackNum == self.seqNum:
                    self.sendAckNum = ackNum
                    ackFinish = True
                elif ackNum > self.sendAckNum:
                    self.sendAckNum = ackNum
                    duplicateTimes = 0
                    resendTimes = 0
                    timeout=False
                elif ackNum == self.sendAckNum:
                    duplicateTimes += 1
                    if duplicateTimes == 3:
                        raise Exception

            except Exception as e:
                self.resendTimes+=1
                if isinstance(e, st.timeout):
                    # print('timeout')
                    timeout = True
                # print(str(self.seqNum))
                resendTimes += 1
                # print('resend %d at %d times' % (self.sendAckNum, resendTimes))
                # print('timeout '+str(self.timeout)+'sec')
                if resendTimes >= 5:
                    if not self.started:
                        ackFinish = True
                        return True
                    else:
                        self.started = False
                        raise Exception('resend times >= 5')
                self.sendPacket([packetDict[self.sendAckNum]])
                self.updataCongWin(True, timeout)
                self.updataTimeout(True)
        
        endTime = time.time()
        rtt = endTime-startTime
        self.updataCongWin(resendTimes != 0, timeout)
        self.updataTimeout(resendTimes != 0, rtt)
        return True

    def receiveAck(self):
        rawData, addr = self.sendSocket.recvfrom(200+self.MSS)
        packet = pickle.loads(rawData)
        return packet['ackNum']

    def updataTimeout(self, resend, rtt=1):
        if resend == True:
            if self.timeout < self.maxTimeout:
                self.timeout *= 2
        else:
            self.timeout = 0.9*self.timeout+0.1*rtt+0.3*rtt

    def updataCongWin(self, resend, timeout):
        if resend == True:
            self.threshold = math.ceil(0.5*self.congWin)
            if timeout == True:
                self.congWin = 1
            else:
                self.congWin = self.threshold
        elif self.congWin < self.windowSize:
            if self.congWin >= self.threshold:
                self.congWin += 1
            else:
                self.congWin *= 2

    def count(self):
        while True:
            last = self.seqNum
            self.resendTimes=0
            time.sleep(0.5)
            if self.started:
                print('sending rate: %dKB/s' % ((self.seqNum-last)*2/(1024)))
                print('resend ratio: %.3f%%'%((self.resendTimes*self.MSS*100)/(self.seqNum-last)))
            else:
                break
