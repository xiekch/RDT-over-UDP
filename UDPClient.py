# import sys
import os
from rdtsend import RDTSend
from sys import argv
# rdt1.0->rdt->2.0->rdt3.0 iteration


class Client:
    def __init__(self, addr):
        self.rdtSend = RDTSend(addr)
        self.addr = addr
        self.MSS = 512
        self.bufferSize = 1000

    def getMetaMessage(self, fileName):
        data = {}
        data['fileName'] = fileName.split('/')[-1]
        data['fileSize'] = os.stat(fileName).st_size
        data['modifiedTime'] = os.stat(fileName).st_mtime
        data['createdTime'] = os.stat(fileName).st_ctime
        return data

    def sendFile(self, fileName):
        print('Start of the transmission')
        self.rdtSend.start()

        # try:
        if not os.path.exists(fileName):
            raise Exception('File not finded')

        file = open(fileName, 'rb')
        dataList = []
        metaMessage = self.getMetaMessage(fileName)
        dataList.append(metaMessage)
        finish = False
        while not finish:
            for i in range(self.bufferSize):
                line = file.read(self.MSS)
                if len(line) == 0:
                    finish = True
                    break
                dataList.append(line)
            self.rdtSend.sendData(dataList)
            dataList = []
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
    # ip=input('input the ip of server:')
    # port=input('input the port of server:')
    # fileName=input('input the file name to transfer:')
    client = Client((argv[1], int(argv[2])))
    client.sendFile(argv[3])
    # client.sendFile('./notesOnPRML.pdf')
    # client.sendFile('./big.txt')
