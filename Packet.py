import pickle

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
            # self.getChecksum()

    def serialize(self):
        return pickle.dumps(self.packet)

    def __str__(self):
        return str(self.packet)
