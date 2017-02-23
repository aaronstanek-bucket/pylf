#Aaron Stanek
#2017

#usage notes
#publics are toFile(filename,dataStructure) and fromFile(filename)
#filename is a string, dataStructure is a list that will be explained later
#fromFile returns a dataStructure

#dataStructures are lists that can contain int, float, bool, str, list, dict, set
#any list, dict, set may only also contain these things

#1 is int
#2 is float
#3 is bool
#4 is string

#17 is start of list
#18 is end of list

#lists are encoded as lists with the first element as "L"
#dicts are encoded as lists with the first element as "D", followed by
#key, value, key, value, ...
#sets are encoded exactly as lists, but 

def encode_str(data, ou):
    #data is a string
    #not unicode compatible
    for x in data:
        ou.append(ord(x))

def encode(data, ou):
    #data is a list, int, float, bool, string
    t=type(data)
    if t==int:
        encode_str(str(data),ou)
        ou.append(1)
    elif t==float:
        encode_str(str(data),ou)
        ou.append(2)
    elif t==bool:
        if data==True:
            encode_str("T",ou)
        else:
            encode_str("F",ou)
        ou.append(3)
    elif t==str:
        encode_str(data,ou)
        ou.append(4)
    elif t==list:
        ou.append(17)
        encode("L",ou)
        for x in data:
            encode(x,ou)
        ou.append(18)
    elif t==dict:
        ou.append(17)
        encode("D",ou)
        for x in data:
            encode(x,ou)
            encode(data[x],ou)
        ou.append(18)
    elif t==set:
        ou.append(17)
        encode("S",ou)
        for x in data:
            encode(x,ou)
        ou.append(18)
    else:
        raise ValueError

def encoder(data):
    ou=[]
    encode(data,ou)
    return ou

def toFile(filename, data):
    ou=encoder(data)
    outfile=open(filename,"w")
    outfile.close()
    outfile=open(filename,"rb+")
    outfile.truncate(0)
    outfile.seek(0,0)
    outfile.write(bytes(ou))

def decode_dict(data):
    #data is a list
    ou={}
    i=1
    dataLen=len(data)
    mode=0
    key=""
    value=""
    while i<dataLen:
        if mode==0:
            #this is a key
            key=data[i]
            mode=1
        else:
            #this is a value
            value=data[i]
            ou[key]=value
            mode=0
        i=i+1
    return ou

def decoder(data):
    #data is a list of ascii values
    k=[] #holds all lists
    s="" #holds strings while being processed
    for x in data:
        if x==17:
            k.append([])
        elif x==18:
            if len(k)==0:
                return []
            elif len(k)==1:
                return k[0][1:] #we want to chop off the first element
            else:
                j=k[-1][0]
                #j should be a string, L, D, S
                if j=="L":
                    k[-2].append(k[-1][1:]) #we want to chop off the first element
                elif j=="D":
                    k[-1]=decode_dict(k[-1])
                    k[-2].append(k[-1])
                elif j=="S":
                    k[-1]=set(k[-1][1:]) #again, chop off first element
                    k[-2].append(k[-1])
                else:
                    raise ValueError
                k.pop()
                del(j)
        elif x==1:
            k[-1].append(int(s))
            s=""
        elif x==2:
            k[-1].append(float(s))
            s=""
        elif x==3:
            if s=="T":
                k[-1].append(True)
            elif s=="F":
                k[-1].append(False)
            else:
                raise ValueError
            s=""
        elif x==4:
            k[-1].append(s)
            s=""
        else:
            #just add to the stack
            s=s+chr(x)
    #it should have returned by now, but just to be sure
    return []

def fromFile(filename):
    infile=open(filename,"rb+")
    da=list(infile.read())
    infile.close()
    ou=decoder(da)
    return ou
