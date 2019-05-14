import socket
import time
import pickle
# from packet imort *

class Packet:
    def __init__(self, data,**kwargs):
        if not kwargs:
            self.packet=data
        else:
            self.packet={}
            # self.packet['checksum']=0
            for k,v in kwargs.items():
                self.packet[k]=v
            self.packet['data']=data
            # self.packet['checksum']=self.getChecksum()


    def serialize(self):
        return pickle.dumps(self.packet)

    def __str__(self):
        return str(self.packet)

class UDPServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.MSS=10000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.windowSize=100
        print('Running at port: '+str(self.port))

    def receive(self):
        dataList={}
        sendSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            rawData,addr=self.socket.recvfrom(200+self.MSS)
            packet=pickle.loads(rawData)

            # print(packet['seqNum'])
            # print('pkt:\n'+str(packet))
            
            # print(rawData)
            if packet['seqNum'] <self.ackNum:
                self.sendAck(sendSocket,addr)
                continue
            else:
                dataList[packet['seqNum']]=packet['data']
                if packet['seqNum'] >self.ackNum:
                    self.sendAck(sendSocket,addr)
                else:
                    self.ackNum+=len(pickle.dumps(packet['data']))
                    while self.ackNum in dataList:
                        self.ackNum+=len(pickle.dumps(dataList[self.ackNum]))
                    self.sendAck(sendSocket,addr)

            if packet['Syn']==True:
                return (dataList[0],1)
            elif packet['Fin']==True:
                self.sendAck(sendSocket,addr)
                #what if it loss?
                return (dataList.values(),-1)
            elif len(dataList)>=self.windowSize:
                # for k in dataList.keys():
                # RuntimeError: dictionary changed size during iteration
                for k in list(dataList.keys()):
                    if k>self.ackNum:
                        dataList.pop(k)
                return (dataList.values(),0)


    def receiveFile(self):
        self.ackNum=self.seqNum=0
        finish=False
        file=None
        while not finish:
            dataList,flag=self.receive()
            if flag==1:
                file=open(dataList['fileName'],'wb')
            elif flag==0:
                if not file:
                    raise Exception('file error')
                    finish=True
                for data in dataList:
                    file.write(data)
            elif flag==-1:
                if not file:
                    raise Exception('file error')
                    finish=True
                for data in dataList:
                    file.write(data)
                finish=True

        if not file:
            raise Exception('file error')
            finish=True
        file.flush()
        file.close()
        print('End of the transmission')

    def sendAck(self,socket,addr):
        packet=Packet(b'',seqNum=self.seqNum,ackNum=self.ackNum,Syn=False,Fin=False)
        pkt=packet.serialize()
        # print('ack:\n'+str(packet))
        socket.sendto(pkt,addr)

if __name__ == '__main__':
    server = UDPServer('172.18.109.30', 8080)
    server.receiveFile();
