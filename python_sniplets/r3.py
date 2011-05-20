class chapter_server :

    @classmethod
    def __init__(self):
        self.stack = [0]

    @classmethod
    def get_structure(self, level):
        while len (self.stack) < level: 
            self.stack.append(0)
        while len (self.stack) > level: 
            self.stack = self.stack[:level]
        self.stack[len (self.stack)-1] += 1
        return ".".join("%s" % s for s in self.stack) + "."
# end class chapter_server

# initialization
chapter_server() # put this in report initialization

# test data
print 'l 1:',chapter_server.get_structure(1)
print 'l 1:',chapter_server.get_structure(1)
print 'l 2:',chapter_server.get_structure(2),'down'
print 'l 2:',chapter_server.get_structure(2)
print 'l 2:',chapter_server.get_structure(2)
print 'l 3:',chapter_server.get_structure(3),'down'
print 'l 3:',chapter_server.get_structure(3)
print 'l 3:',chapter_server.get_structure(3)
print 'l 4:',chapter_server.get_structure(4),'down'
print 'l 3:',chapter_server.get_structure(3),'up'
print 'l 1:',chapter_server.get_structure(1),'up'
print 'l 2:',chapter_server.get_structure(2),'down'
