import sys
import gevent
from gevent.server import StreamServer
from gevent.subprocess import Popen, call
from sorteddict import SortedDict
from logfile import RotatingFile

shutdown = False
manager = None

def set_shutdown(flag):
    global shutdown
    shutdown = flag
    
class Command(object):
    def __init__(self, name, command, **kwargs):
        self.name = name
        self.command = command
        self.log = None
        self.stop = False
        self.process = None
        for k, v in kwargs.items():
            setattr(self, k, v)
        
    def is_ok(self):
        return self.process and self.process.poll() is None
    
    def do_start(self):
        if not self.log:
            self.log = RotatingFile(self.logfile,
                maxBytes=self.logfile_maxbytes, 
                backupCount=self.logfile_backups)
            
        if self.is_ok():
            msg = self.name + ' has already been started'
        else:
            self.log.info('start '+self.name)
            self.process = Popen(self.command, stdout=self.log, stderr=self.log, shell=True, cwd=self.cwd)
            self.stop = False
            msg = self.name + ' started'
        return msg
    
    def do_stop(self):
        if self.is_ok():
            self.log.info('stop '+self.name)
            self.stop = True
            call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            self.process = None
            msg = self.name + ' stopped'
        else:
            msg = self.name + ' has already stopped'
        return msg
    
    def do_status(self):
        if self.is_ok():
            status = 'RUNNING'
        else:
            status = 'STOPPED'
        msg = '%-20s %s' % (self.name, status)
        return msg
        
def monitor():
    while 1:
        if shutdown:
            manager.shutdown()
            return
            
        manager.check()
        
        gevent.sleep(0.5)
        
class CommandsManager(object):
    def __init__(self, Ini):
        self.commands = SortedDict()
        
        for k, v in Ini.items():
            if k.startswith('program:'):
                kwargs = {}
                kwargs['name'] = name = k[8:]
                kwargs['command'] = v.command
                kwargs['cwd'] = v.get('directory', None)
                kwargs['logfile'] = v.get('logfile', name+'.log')
                kwargs['logfile_maxbytes'] = v.get('logfile_maxbytes', 50*1024*1024)
                kwargs['logfile_backups'] = v.get('logfile_backups', 10)
                self.commands[name] = Command(**kwargs)
                
    def start(self, command=None):
        if not command:
            for k, command in self.commands.items():
                command.do_start()
        else:
            cmd = self.commands.get(command, '')
            if not cmd:
                msg = "Program %s is not found" % command
            else:
                msg = cmd.do_start()
            return msg
            
    def stop(self, command):
        cmd = self.commands.get(command, '')
        if not cmd:
            msg = "Program %s is not found" % command
        else:
            msg = cmd.do_stop()
        return msg

    def shutdown(self):
        for k, command in self.commands.items():
            command.do_stop()
        msg = 'shutdown successful'
        return msg
    
    def status(self):
        s = []
        for k, command in self.commands.items():
            s.append(command.do_status())
        return '\n'.join(s)

    def check(self):
        for k, p in self.commands.items():
            if not p.stop and not p.is_ok():
                p.do_start()
        
def CommandsHandler(socket, address):
    # using a makefile because we want to use readline()
    command = socket.recv(1024)
    cmds = command.split()
    cmd = cmds[0]
    if len(cmds) > 1:
        args = cmds[1:]
    else:
        args = ()
    
    func = getattr(manager, cmd, None)
    if not func:
        socket.send('Command %s is not supported' % cmd)
        return
    result = func(*args)
    socket.send(result)
    if cmd == 'shutdown':
        sys.exit(0)
            
def main():
    global manager
    
    import pyini
    Ini = pyini.Ini('watcher.ini')
    
    manager = CommandsManager(Ini)
    manager.start()
    gevent.spawn(monitor)
    server = StreamServer((Ini.server.host, Ini.server.port), CommandsHandler)
    server.serve_forever()
            
if __name__ == '__main__':
    main()