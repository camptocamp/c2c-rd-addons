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
def level_current(level=None):
    if not level:
       level = 1  
    while  1 == 1:
       yield level

levelobj = level_current()
print levelobj.next()

#def levelobj(val=None):
#    return level_current(val)

def check_level(level):
    print levelobj.next()
    level_last = levelobj.next()
    if level == level_last:
        res=genobj.next()
    elif level > level_last:
        res=down()
    else :
        while level < level_last:
            res=up()
            level_last -= 1
    levelobj = level_current(level)
    return res
        

print check_level(1)
print check_level(1)
print check_level(2)




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
