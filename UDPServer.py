# import sys
import os
import socket
import time
import math
import pickle

# rdt1.0->rdt->2.0->rdt3.0 iteration

class Packet:
    
    def __init__(self, seqNum,ackNum,data,**kwargs):
        self.packet={}
        self.packet['seqNum']=seqNum
        self.packet['ackNum']=ackNum
        self.packet['data']=data
        for k,v in kwargs.items():
            self.packet[k]=v

    def serialize(self):
        return pickle.dumps(self.packet)

# p2p
class UDP:
    def __init__(self, addr,sendAddr):
        self.addr=addr
        self.sendAddr=sendAddr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.congWin=1
        self.threshold=100
        self.MSS=500
        self.seqNum=0
        self.ackNum=0
        print('Running at port: '+str(self.addr[1]))
        print('Send to '+str(self.sendAddr[0])+' at port '+str(self.sendAddr[1]))

    def receive(self):
        pass

    def receiveFile(self):
        pass

    def getMetaMessage(self,fileName):
        data={}
        data['fileName']=fileName
        data['fileSize']=os.stat(fileName).st_size
        data['modifiedTime']=os.stat(fileName).st_mtime
        data['createdTime']=os.stat(fileName).st_ctime
        return data

    # resend times <5
    def send(self,socket,dataList):
        for data in dataList:
            time.sleep(0.001)

            if self.seqNum==0:
                packet=Packet(self.seqNum,self.ackNum,data,Syn=True,Fin=False)
            elif len(data)==0:
                packet=Packet(self.seqNum,self.ackNum,data,Syn=False,Fin=True)
                print('End of the transmission')
            else:
                packet=Packet(self.seqNum,self.ackNum,data,Syn=False,Fin=False)
            pkt=packet.serialize()
            socket.sendto(pkt,self.sendAddr)
            self.seqNum+=len(pkt)
        

    def sendFile(self,fileName):
        self.seqNum=self.ackNum=0
        if not os.path.exists(fileName):
            print('File not finded')
            return
        
        sendSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
                    
        file.close()


if __name__ == '__main__':
    server = UDP(('localhost', 8000),('172.18.109.30',8080))
    server.sendFile('test.py')#('./notesOnPRML.pdf')
