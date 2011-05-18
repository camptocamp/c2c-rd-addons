def numbering(val=None):
    n = 0
    if not val:
       val ='1.'
    yield val
    while 1==1:
       n += 1
       yield val+str(n)+'.'
       
def up():
    val = genobj.next()
    base=val[0:val.rfind('.')-1]    
    cur = base[base.rfind('.')-1:]
    cur1= str(int(cur.rstrip('.'))+1)+'.'
    base=val[0:base.rfind('.')-1]    
    return numbering(base+cur1)
     
def down():
    return numbering(genobj.next())


genobj=numbering()
print genobj.next()
print genobj.next()
genobj=down()
print genobj.next()
print genobj.next()
print genobj.next()
print genobj.next()
genobj=up()
print genobj.next()
print genobj.next()
genobj=up()
print genobj.next()
genobj=up()
genobj=up()
print genobj.next()
print genobj.next()
print genobj.next()
genobj=down()
print genobj.next()
print genobj.next()
print genobj.next()
