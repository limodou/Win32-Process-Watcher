import gevent
from gevent import monkey
monkey.patch_socket()

import cmd

addr = ('localhost', 6001)

def send_cmd(command):
    socket = gevent.socket.socket()
    socket.connect(addr)
    socket.send(command+'\n')
    print socket.recv(1024)
    socket.close()
    

class ClientCmd(cmd.Cmd):
    """Simple command processor example."""
    
    def do_status(self, line):
        send_cmd('status')
        
    def do_stop(self, line):
        if not line:
            print 'Please give the process name'
        else:
            send_cmd('stop '+line)
    
    def do_start(self, line):
        if not line:
            print 'Please give the process name'
        else:
            send_cmd('start '+line)

    def do_shutdown(self, line):
        send_cmd('shutdown '+line)

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    ClientCmd().cmdloop()

