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

#17 is start of list, dict, or set
#18 is end of list
#19 is end of dict
#20 is end of set

#lists are encoded as lists with the first element as "L"
#dicts are encoded as lists with the first element as "D", followed by
#key, value, key, value, ...
#sets are encoded exactly as lists, but 

###########################

#this code runs when the module is imported
#it sets the version number, and precomputes the ASCII representation
versionString="1.2" #update this when version changes
version=[] #this is the ASCII version of versionString, with a colon at the end

#version is computed from versionString in the following function

def autorunWhenImported():
    global versionString
    global version
    version=[80,89,76,70] #PYLT
    for x in versionString:
        version.append(ord(x))
    version.append(ord(":"))

autorunWhenImported()

###########################

def returnVersion():
    #this function exsits because I will probably have to use this
    #code in multiple places
    global version
    ou=version[:]
    return ou

def returnVersionString():
    global versionString
    return versionString

###########################

def encode_str(data, ou):
    #data is a string
    #not unicode compatible
    for x in data:
        ou.append(ord(x))

def encode_str_unicode(data, ou):
    #data is a string, potentially with unicode characters
    #normal characters are encoded with ASCII
    #nonstandad characters are encoded by unicode value
    #the value will be split into 6 bit chunks
    #each chunk will be save into a byte
    #all of these bytes will start with a 10
    #except for the last byte which will start with 11
    for x in data:
        ox=ord(x)
        special=True
        if ox<127:
            if ox>31:
                special=False
        #if special is False, then we can just use ASCII encoding
        #if sepcial is True, then we have to do other stuff (unicode, but not UTF8)
        if special==False:
            ou.append(ox)
        elif ox==0:
            ou.append(192) #1100 0000
        else:
            k=[] #store values, here each 6 bits worth, encoded least significant first
            t=ox
            while t!=0:
                k.append(int(t%64))
                t=int(t/64)
            kLen=len(k)
            i=0
            while i<kLen:
                k[i]=k[i]+128 #1000 0000
                i=i+1
            k[0]=k[0]+64 #this will become the last character
            i=kLen-1
            while i>=0:
                ou.append(k[i])
                i=i-1
    #no return necessary

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
        encode_str_unicode(data,ou)
        ou.append(4)
    elif t==list:
        ou.append(17)
        for x in data:
            encode(x,ou)
        ou.append(18)
    elif t==dict:
        ou.append(17)
        for x in data:
            encode(x,ou)
            encode(data[x],ou)
        ou.append(19)
    elif t==set:
        ou.append(17)
        for x in data:
            encode(x,ou)
        ou.append(20)
    else:
        raise ValueError

def encoder(data):
    ou=returnVersion() #get a copy of the ASCII version information
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
    i=0
    dataLen=len(data)
    while i<dataLen:
        key=data[i]
        i=i+1
        value=data[i]
        i=i+1
        ou[key]=value
    return ou

def decode_str_unicode(data):
    #data is a mangled string
    j=[]
    for x in data:
        j.append(ord(x))
    v=0 #stores the value of a character
    s=""
    for x in j:
        if x<128:
            s=s+chr(x)
        else:
            if x>=192: #starts with 11
                v=(v*64)+x-192
                s=s+chr(v)
                v=0
            else: #starts with 10
                v=(v*64)+x-128
    return s

def decoder(data):
    #data is a list of ascii values
    ver=returnVersion() #ver is now a local copy of the version in ASCII numbers
    k=[] #holds all lists
    s="" #holds strings while being processed
    if data[:len(ver)]!=ver: #checks to see if the version in the file is the same as the version here
        #if this is not a good format, inform the user, and
        #include the present version number
        return ["INVALID FILE FORMAT",returnVersionString()]
    i=len(ver) #this is dependent on version marking
    del(ver) #ver is not needed anymore in this function, might as well save space
    dataLen=len(data)
    while i<dataLen:
        x=data[i] #this is left over from when this was a for loop
        if x>20:
            #this was added increase speed, remove this if statement if editing this file
            s=s+chr(x)
        elif x==1: #int
            k[-1].append(int(s))
            s=""
        elif x==2: #float
            k[-1].append(float(s))
            s=""
        elif x==3: #bool
            if s=="T":
                k[-1].append(True)
            elif s=="F":
                k[-1].append(False)
            else:
                raise ValueError
            s=""
        elif x==4: #string
            k[-1].append(decode_str_unicode(s))
            s=""
        elif x==17: #new container
            k.append([])
        elif x==18: #end list
            if len(k)==0:
                return []
            if len(k)==1:
                return k[0]
            #hop list down a level
            k[-2].append(k[-1])
            k.pop()
        elif x==19: #end dict
            k[-2].append(decode_dict(k[-1]))
            k.pop()
        elif x==20: #end set
            k[-2].append(set(k[-1]))
            k.pop()
        else:
            #just add to the stack
            #this bit only gets run if we have a value less than 20 and not a command character
            s=s+chr(x)
        i=i+1 #this loop used to be a for loop, this was added after the conversion
    #it should have returned by now, but just to be sure
    return []

def fromFile(filename):
    infile=open(filename,"rb+")
    da=list(infile.read())
    infile.close()
    ou=decoder(da)
    return ou
