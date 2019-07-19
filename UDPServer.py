from rdtrecv import RDTRecv
from sys import argv


class Server:
    def __init__(self, addr):
        self.rdtRecv = RDTRecv(addr)
        self.addr = addr

    def receiveFile(self, fileLocation):
        print('Start of the transmission')

        started = True
        file = None
        while started:
            dataList, started = self.rdtRecv.receiveData()
            if not file:
                for k, v in dataList[0].items():
                    print('%s: %s' % (k, v))
                file = open(fileLocation+dataList[0]['fileName'], 'wb')
                for data in dataList[1:]:
                    file.write(data)
            else:
                for data in dataList:
                    file.write(data)
        file.flush()
        file.close()
        print('End of the transmission')


if __name__ == '__main__':
    # ip=input('input the ip of server: ')
    # port=int(input('input the port of server: '))
    server = Server((argv[1], int(argv[2])))
    server.receiveFile(argv[3])
