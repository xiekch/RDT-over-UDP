import pickle

class Packet:
    def __init__(self, data,**kwargs):
        if not kwargs:
            self.packet=data
        else:
            self.packet={}
            for k,v in kwargs.items():
                self.packet[k]=v
            self.packet['data']=data

    def serialize(self):
        return pickle.dumps(self.packet)

    def __str__(self):
        return str(self.packet)
