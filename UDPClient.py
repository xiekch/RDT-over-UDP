import socket
import time
import json


class UDPServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.MSS=10000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        print('Running at port: '+str(self.port))

    def receive(self):
        rawData,addr=self.socket.recvfrom(200+self.MSS)
        self.ackNum+=len(rawData)
        packet=json.loads(rawData.decode())
        # print(rawData)
        data=packet['data']
        if packet['Syn']==True:
            return (data,1)
        elif packet['Fin']==True:
            return (data,-1)
        else:
            return (data,0)

    def receiveFile(self):
        self.ackNum=self.seqNum=0
        finish=False
        while not finish:
            data,flag=self.receive()
            # print(flag)
            
            if flag==1:
                file=open(data['fileName'],'wb')                
            elif flag==0:
                file.write(data.encode('ISO-8859-1'))
            elif flag==-1:
                file.flush()
                finish=True

        file.close()
        print('End of the transmission')

if __name__ == '__main__':
    server = UDPServer('172.18.109.30', 8080)
    server.receiveFile();
