
def numbering(flag,val=None):
       
   if not val and flag == 'init' :
      val = '1.'
   elif flag == 'next':
      v = val.rsplit('.')
      s = v[-2] 
      b = val.rstrip('.')
      b = b.rstrip(s)
      val = b+str(int(s)+1)+'.'

   elif flag == 'down':
      val = val + '1.'

   elif flag == 'up':
      v = val.rsplit('.')
      s = v[-2]
      b = val.rstrip('.')
      val = b.rstrip(s)
      val = numbering('next',val)

   return val

val = numbering('init')
print 'init',val
val = numbering('next',val)
print 'next',val
val = numbering('down',val)
print 'down',val
val = numbering('next',val)
print 'next',val
val = numbering('down',val)
print 'down',val
val = numbering('next',val)
print 'next',val
val = numbering('next',val)
print 'next',val
val = numbering('down',val)
print 'down',val
val = numbering('next',val)
print 'next',val
val = numbering('up',val)
print 'up  ',val
val = numbering('next',val)
print 'next',val
val = numbering('down',val)
print 'down',val
val = numbering('down',val)
print 'down',val
val = numbering('next',val)
print 'next',val
val = numbering('up',val)
print 'up  ',val
val = numbering('up',val)
print 'up  ',val
val = numbering('next',val)
print 'next',val
val = numbering('next',val)
print 'next',val
val = numbering('next',val)
print 'next',val
val = numbering('next',val)
print 'next',val
val = numbering('next',val)
print 'next',val
val = numbering('down',val)
print 'down',val
