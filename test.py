class One:
    def __str__(self):
        return 'super().__str__()'

one={}
one['a']=1
one['b']=2
print(str(one))