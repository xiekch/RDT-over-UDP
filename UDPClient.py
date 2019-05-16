# import sys
import os
import socket as st
import time
import math
import pickle
from packet import Packet
from rdtsend import RDTSend
# rdt1.0->rdt->2.0->rdt3.0 iteration

# p2p
class Client:
    def __init__(self, addr):
        self.rdtSend=RDTSend(addr)
        self.addr=addr
        self.MSS=512
        self.bufferSize=1000
        
    def getMetaMessage(self,fileName):
        data={}
        data['fileName']=fileName
        data['fileSize']=os.stat(fileName).st_size
        data['modifiedTime']=os.stat(fileName).st_mtime
        data['createdTime']=os.stat(fileName).st_ctime
        return data

    def sendFile(self,fileName):
        print('Start of the transmission')
        self.rdtSend.start()

        # try:
        if not os.path.exists(fileName):
            raise Exception('File not finded')          
        
        file=open(fileName,'rb')
        metaMessage=self.getMetaMessage(fileName)

        self.rdtSend.sendData([metaMessage])
        finish=False
        while not finish:
            dataList=[]
            for i in range(self.bufferSize):
                line=file.read(self.MSS)
                if len(line)==0:
                    finish=True
                    break
                dataList.append(line)
            self.rdtSend.sendData(dataList)
        self.rdtSend.end()

        # except Exception as e:
        #     print('Exception: '+str(e))
        #     return False
        # else:
        print('End of the transmission')
        # finally:
        if file:
            file.close()


if __name__ == '__main__':
    client = Client(('172.18.109.30',8080))
    # client.sendFile('./test.py')
    client.sendFile('./test.pdf')
    # client.sendFile('./notesOnPRML.pdf')
    # client.sendFile('./big.txt')