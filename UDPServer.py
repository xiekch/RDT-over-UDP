# import sys
import os
import socket as st
import time
import math
import pickle
from packet import *
# rdt1.0->rdt->2.0->rdt3.0 iteration

# p2p
class UDP:
    def __init__(self, addr,sendAddr):
        self.addr=addr
        self.sendAddr=sendAddr
        self.socket = st.socket(st.AF_INET, st.SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.timeout=1
        self.congWin=1
        self.threshold=100
        self.MSS=500
        self.seqNum=0
        self.ackNum=0
        self.sendAck=0
        self.sendWin=2000
        self.maxTimeout=4
        print('Running at port: '+str(self.addr[1]))
        print('Send to '+str(self.sendAddr[0])+' at port '+str(self.sendAddr[1]))

    def getMetaMessage(self,fileName):
        data={}
        data['fileName']=fileName
        data['fileSize']=os.stat(fileName).st_size
        data['modifiedTime']=os.stat(fileName).st_mtime
        data['createdTime']=os.stat(fileName).st_ctime
        return data

    def receiveAck(self,socket):
        rawData,addr=socket.recvfrom(200+self.MSS)
        packet=pickle.loads(rawData)
        # print('ack'+str(packet))
        return packet['ackNum']

    def receiveFile(self):
        pass

    # resend times <5
    def send(self,socket,dataList):
        packetList={}
        startTime=time.time()
        for data in dataList:
            # time.sleep(0.001)
            # print(self.seqNum)

            if self.seqNum==0:
                packet=Packet(data,seqNum=self.seqNum,ackNum=self.ackNum,Syn=True,Fin=False)
            elif len(data)==0:
                packet=Packet(data,seqNum=self.seqNum,ackNum=self.ackNum,Syn=False,Fin=True)
            else:
                packet=Packet(data,seqNum=self.seqNum,ackNum=self.ackNum,Syn=False,Fin=False)
            pkt=packet.serialize()
            # print('pkt:\n'+str(packet))
            socket.sendto(pkt,self.sendAddr)
            packetList[packet.packet['seqNum']]=pkt
            self.seqNum+=len(pickle.dumps(packet.packet['data']))

        # print('send '+str(self.seqNum))
        ackFinish=False
        resendTimes=0
        duplicateTimes=0
        while not ackFinish:
            try:
                socket.settimeout(self.timeout)
                ackNum=self.receiveAck(socket)
                # print('ack:\n '+str(ackNum))
                if ackNum==self.seqNum:
                    self.sendAck=ackNum
                    ackFinish=True
                elif ackNum>self.sendAck:
                    self.sendAck=ackNum
                    duplicateTimes=0
                    resendTimes=0
                elif ackNum==self.sendAck:
                    duplicateTimes+=1
                    if duplicateTimes==3:
                        raise Exception

            except Exception as e:
                resendTimes+=1
                print('resend '+str(self.sendAck)+' at '+str(resendTimes)+' times')
                print('timeout '+str(self.timeout)+'sec')
                # print(str(packetList))
                if resendTimes>=5:
                    raise Exception('resend times >= 5')
                    
                socket.sendto(packetList[self.sendAck],self.sendAddr)
                self.updataCongWin(True)
                self.updataTimeout(True)
                
        endTime=time.time()
        rtt=endTime-startTime
        self.updataCongWin(resendTimes!=0)
        self.updataTimeout(resendTimes!=0,rtt)
        return True
        

    def sendFile(self,fileName):
        self.seqNum=self.ackNum=0
        try:
            if not os.path.exists(fileName):
                raise Exception('File not finded')          
            
            sendSocket=st.socket(st.AF_INET, st.SOCK_DGRAM)
            file=open(fileName,'rb')
            metaMessage=self.getMetaMessage(fileName)
            self.send(sendSocket,[metaMessage])

            finish=False
            while not finish:
                dataList=[]
                for i in range(self.congWin):
                    line=file.read(self.MSS)
                    dataList.append(line)
                    if len(line)==0:
                        finish=True
                        break
                self.send(sendSocket,dataList)
        except Exception as e:
            print('Exception: '+str(e))
            return False
        else:
            print('End of the transmission')
            return True
        finally:
            if file:
                file.close()


    def updataTimeout(self,resend,rtt=1):
        if resend==True:
            if self.timeout<self.maxTimeout:
                self.timeout*=2
        else:
            self.timeout=0.85*self.timeout+0.15*rtt+0.2*rtt
        

    def updataCongWin(self,resend):
        if resend==True:
            self.threshold=math.ceil(0.5*self.congWin)
            self.congWin=1
        elif self.congWin<self.sendWin:
            if self.congWin>=self.threshold:
                self.congWin+=1
            else:
                self.congWin*=2
        

def test(server,fileName):
    server.sendFile(fileName)

if __name__ == '__main__':
    server = UDP(('172.18.109.30', 8001),('172.18.109.30',8080))
    # server.sendFile('./test.py')
    server.sendFile('./test.pdf')
    # server.sendFile('./notesOnPRML.pdf')
    # server.sendFile('./big.txt')