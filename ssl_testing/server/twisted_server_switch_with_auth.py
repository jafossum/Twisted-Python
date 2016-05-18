# ############## SWITH TO SSL ON TOKEN
from OpenSSL import SSL
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver

def verifyCallback(connection, x509, errnum, errdepth, ok):
    if not ok:
        print 'invalid cert from subject:', x509.get_subject()
        return False
    else:
        print "Certs are fine"
    return True

class TLSServer(LineReceiver):
    def lineReceived(self, line):
        print "received: " + line

        if line == "STARTTLS":
            print "-- Switching to TLS"
            self.sendLine('READY')
            myContextFactory = ssl.DefaultOpenSSLContextFactory(privateKeyFileName="../certs/server.key",
                                                                certificateFileName="../certs/server.crt")

            myContextFactory.getContext().set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verifyCallback)

            # Since we have self-signed certs we have to explicitly
            # tell the server to trust them.
            myContextFactory.getContext().load_verify_locations("../certs/rootCA.pem")

            self.transport.startTLS(myContextFactory, self.factory)

        self.sendLine(line)


class ServerTLSContext(ssl.DefaultOpenSSLContextFactory):
    def __init__(self, *args, **kw):
        ssl.DefaultOpenSSLContextFactory.__init__(self, *args, **kw)

if __name__ == '__main__':
    factory = ServerFactory()
    factory.protocol = TLSServer
    reactor.listenTCP(8000, factory)
    reactor.run()
