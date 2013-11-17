import os
import datetime

from logging.handlers import RotatingFileHandler

class RotatingFile(RotatingFileHandler):
    def write(self, buf):
        try:
            stream = self.stream
            buf = buf + '\n'
            if (isinstance(buf, unicode) and
                getattr(stream, 'encoding', None)):
                buf = buf.decode(stream.encoding)
                try:
                    stream.write(buf)
                except UnicodeEncodeError:
                    #Printing to terminals sometimes fails. For example,
                    #with an encoding of 'cp1251', the above write will
                    #work if written to a stream opened or wrapped by
                    #the codecs module, but fail when writing to a
                    #terminal even when the codepage is set to cp1251.
                    #An extra encoding step seems to be needed.
                    stream.write((buf).encode(stream.encoding))
            else:
                stream.write(buf)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            import traceback
            traceback.print_exc()

    def fileno(self):
        return self.stream.fileno()
    
    def info(self, msg):
        msg = '[%s] %s' % (str(datetime.datetime.now()), msg)
        self.write(msg)
        
    def _open(self):
        """
        Open the current base file with the (original) mode and encoding.
        Return the resulting stream.
        """
        import codecs
        if self.encoding is None:
            stream = open(self.baseFilename, self.mode)
        else:
            stream = codecs.open(self.baseFilename, self.mode, self.encoding)
        stream.seek(0, os.SEEK_END)
        return stream
    
