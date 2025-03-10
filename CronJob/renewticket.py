#env python3
import os,sys
from optparse import OptionParser
from subprocess import call
from getpass import getpass
from time import sleep
import threading

usage='''
    Utility to renew the keytab without typing the pwd.
    It will not be written in any process.
'''

parser=OptionParser(usage=usage)
#parser.add_option("-t","--tmp",help="tmp directory [%default]",default="/tmp/"+os.environ['USER']+"/mydir")
#parser.add_option("-f","--file",help="file name [%default]",default="mynode")
parser.add_option("","--pwd",help="Write Pwd here. Insecure [%default]",default="")
parser.add_option("-v","--verbose",action='store_true',help="Activate debug printouts [%default]",default=False)
parser.add_option("-s","--sleep",type='int',help="sleep [%default]",default=3600)
parser.add_option("-d","--database",type='string',
            help="database option. This will keep track of the active renewal around the world [%default]",
            default=os.environ['HOME']+"/.tickets.txt"
        )
parser.add_option("","--printonly",action='store_true',help="Print only the DB in RO  mode[%default]",default=False)

opts,args=parser.parse_args()


## bash color string
red="\033[01;31m"
green = "\033[01;32m"
yellow = "\033[01;33m"
blue = "\033[01;34m"
pink = "\033[01;35m"
cyan = "\033[01;36m"
white = "\033[00m"
ERROR="ERROR"
WARN="WARNING"
INFO="INFO"

if opts.pwd == "" and not opts.printonly:
    if opts.verbose: print ("-> Password needs to be prompted")
    pwd=getpass("Password:")
else:
    if opts.verbose: print ("-> Password has been given in the options")
    pwd = opts.pwd

def write(file,pwd):
    if opts.verbose: print ("-> Going to write in file",file)
#    print("AAAA")
##    print(pwd)
#    print("BBBB")
#    print(file)
    f = open(file,"a")
#    print("CCC")
#    print("|",pwd,"|")
    f.write(pwd)
    f.close()    
#    print("D")

class Database:
    def __init__(self,name):
        self.name = name
#        self.lockfile = name + '.lock'
        self.host = os.environ['HOSTNAME']
        self.ntries = 3
        self.db={}
        self.locked=False

    def getlock_impl_(self):
        # if already have the lock
        if self.locked: 
            return
        ##
        n=0
        while os.path.isfile(self.lockfile):
            n+=1
            if n>self.ntries:
                print ('Not able to lock db. Exiting', "Check lockfile:",self.lockfile)
                raise OSError
            sleep(3)
        lockhandle =open(self.lockfile, 'a')
        lockhandle.write(self.host)
        lockhandle.close()
        self.locked=True

    def releaselock_impl_(self):
        ## check I have the lock
        if not self.locked: return
        os.remove(self.lockfile)
        self.locked=False

    def cleandb_impl_(self):
        self.db={}

    def readdb_impl_(self):
        ## can also not be locked ... RO ?
        self.cleandb_impl_()

        # if db does not exists, return empty
        if not os.path.isfile(self.name): return 

        dbfile=open(self.name,"r")
        for line in dbfile:
            h=line.split()[0]
            self.db[h]=1
            if len(line.split())> 1:
                self.db[h]=line.split()[1]
        dbfile.close()

    def writedb_impl_(self):
        dbfile=open(self.name,"w")
        for key in self.db:
        # if it is 0, do not write it
            if isinstance(self.db[key], int) and self.db[key] == 0 : continue
        
        # write the key
            dbfile.write(key )
        
        # if it is a string, write addition info
        if isinstance(self.db[key], str): ## str in python 3x
            dbfile.write(" " + self.db[key])
        # new line
            dbfile.write("\n" )
        dbfile.close()


    ###### USER FUNCTION #####    
    def read(self):
#        self.getlock_impl_()
        self.readdb_impl_()

    def readro(self):
        self.readdb_impl_()

    def addme(self):
        self.db[ self.host ] = 1

    def removeme(self):
        if self.host in self.db:
            del self.db[self.host]

    def ispresent(self,key):
        if key in self.db: return True
        return False

    def value(self,key):
        if key in self.db: return self.db[key]
        return None

    def amipresent(self):
        return self.ispresent(self.host)

    def myvalue(self):
        return self.value(self.host)

    def write(self):
        if not self.locked: 
            raise "Error. In order to write the db, it should be locked."
        self.writedb_impl_()
        self.releaselock_impl_()
    
    def release(self):
        self.releaselock_impl_()

    def printdb(self):
        print ("------ DATABASE ----")
        print ("name:",self.name)
        print ("lock:",self.locked)
        print ("keys:")
        for key in self.db:
            print ("    ",key, end ='')
            if self.db[key] ==1:
                print ("")
            else:
                print (self.db[key])
        print ("--------------------")

    def cmd_checks_impl_(self):
        '''Return True if cmd needs to be run'''
        if not self.amipresent(): return False
        if self.myvalue() == 1: return  False
        if not self.myvalue().startswith("cmd:") and not self.myvalue().startswith("kill"): return False
        return True

    def exec_impl_(self):
        if not self.cmd_checks_impl_(): return
        if self.myvalue().replace('~',' ').startswith("kill"):
            print ("-> Emulating Keyboard interrupt")
            raise KeyboardInterrupt
        cmd=self.myvalue().replace('~',' ').replace('cmd:','').replace('rm',' ')
        print ("-> Calling cmd",cmd)
        st=call(cmd,shell=True)
        self.db[self.host]="status:%d"%st
        print ("*  Exit with status",st)
        return st

    def execute(self):
        # list of checks
        if not self.cmd_checks_impl_(): return
            # I should run, but in order to do it I need to be in rw mode
        waslocked=self.locked

        if not self.locked:
            self.read() ## full read
        #this will check again the db conditions, because db has been reread
        st=self.exec_impl_() 
        self.write()
        if not waslocked: self.release()
        return

#db=Database(opts.database)

#if opts.printonly:
#        db.readro()
#        db.printdb()
#        exit(0)

#db.read()
#print(db)
#if db.amipresent() : 
#    print ("I am already in the DB. Probably something is already running ...")
#    db.release()
#    exit(0)

#db.addme()
#db.write()


try:
  while True:
    threads=[]
    ## check that dir ends with "/"
#    dir=opts.tmp
#    if dir[-1] != "/": dir+="/"

#    cmd="mkdir " + dir +"; chmod 700 " + dir
#    print(cmd)
#    call(cmd,shell=True)

#    file=dir + opts.file

#    if opts.verbose:
#         print ("---- NEW RUN ---")
#         print ("file=",file)

    ## check if some command have been written and if it is so execute, updating the db
#    db.readro()
#    db.execute()

#    #1) Clean file
#    if opts.verbose: print ("->Going to remove file",file)
#    cmd="rm -v "+ file + " 2>&1 >/dev/null"
#    print(cmd)
#    call(cmd,shell=True)

#    #2) Create a fifo
#    if opts.verbose: print ("-> Going to create fifo in file",file)
#    cmd="mkfifo " + file
#    print(cmd)
#    st=call(cmd,shell=True)
#    if st !=0:
#        print (red+ERROR+":"+white + "Unable to create the fifo in "+ file)

#    #3) Write on the fifo and close it
#    t=threading.Thread(target=write, args= (file,pwd)  )
##    write(file, pwd)
#    t.start()
#    threads.append( t )

    #4) Kinit
    if opts.verbose: print ("-> Going to execute kinit")
#    cmd="cat "+ file +" | kinit "
    cmd="echo "+ pwd +" | kinit "
    #print(cmd)
    st=call(cmd,shell=True)
    print("st=",st)
    if st !=0:
        print (red+ERROR+":"+white + "Unable to get keytab")
    else:
        print (green+"OK:" + white + " keytab correctly aquired")

#    #5) Join 
#    if opts.verbose: print ("-> Make sure threads ended")
#    for t in threads:
#        t.join()
#    threads=[] 
   
#    #6) Rm Fifo
#    if opts.verbose: print ("-> Going to remove fifo")
#    cmd="rm -v "+ file
#    print(cmd)
#    st=call(cmd,shell=True)
#    if st !=0:
#        print (red+ERROR+":"+white + "Unable to remove fifo:", file)
#        print (pink+WARN+":"+white + "it is possible that the pwd is still in the fifo. Please check!")

    #7) Sleep
    if opts.verbose: 
        time=opts.sleep
        seconds=time
        s="%ds "%seconds
        h=""
        m=""
        minutes=0
        if seconds>60:
            minutes=time/60
            seconds=time - 60*minutes
            m="%dm "%minutes
            s="%ds "%seconds
        if minutes>60:
            hours=minutes/60
            minutes=minuts - hours*60
            m="%dm "%minutes
            h="%dh "%hours
        print ("-> Going to sleep for "+h  + m + s)
    sleep(opts.sleep)

except KeyboardInterrupt: 
    pass

db.read()
db.removeme()
db.write()
db.printdb()

