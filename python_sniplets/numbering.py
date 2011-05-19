def numbering(base=None,num=None):
    if not base:
       base =''
    if num:
       num = int(num.rstrip('.'))
    else:
       num = 0
    while 1==1:
       num += 1
       yield base+str(num)+'.'
       
def new_level(param):
    global genobj
    val = genobj.next()
    base= val[0:val.rfind('.')-1]
    if param == 'up':
       num=  base[base.rfind('.')-1:].rstrip('.')
       base= base[0:base.rfind('.')-1]
       genobj=numbering(base,num)
    elif param == 'down':
       num=  val[val.rfind('.')-1:].rstrip('.')
       num = str(int(num)-1)
       genobj=numbering(base+num+'.')
    return genobj.next()

genobj=numbering()

def level_current(level=None):
    if not level:
       level = 1  
    while  1 == 1:
       yield level

levelobj = level_current()

def get_structure(level):
    global levelobj
    level_last = levelobj.next()
    if level == level_last:
        res=genobj.next()
    elif level > level_last:
        res=new_level('down')
    else :
        while level < level_last:
            res=new_level('up')
            level_last -= 1
    levelobj = level_current(level)
    return res
        
# test data
print 'l 1:',get_structure(1)
print 'l 1:',get_structure(1)
print 'l 2:',get_structure(2),'down'
print 'l 2:',get_structure(2)
print 'l 2:',get_structure(2)
print 'l 3:',get_structure(3),'down'
print 'l 3:',get_structure(3)
print 'l 3:',get_structure(3)
print 'l 4:',get_structure(4),'down'
print 'l 3:',get_structure(3),'up'
print 'l 1:',get_structure(1),'up'
print 'l 2:',get_structure(2),'down'




