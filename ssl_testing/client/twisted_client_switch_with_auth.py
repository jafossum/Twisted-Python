# ############## SWITH TO SSL ON TOKEN
from OpenSSL import SSL
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

class ClientTLSContext(ssl.ClientContextFactory):
    isClient = 1
    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('../certs/device.crt')
        ctx.use_privatekey_file('../certs/device.key')

        return ctx

class TLSClient(LineReceiver):
    pretext = [
        "first line",
        "last thing before TLS starts",
        "STARTTLS"]

    posttext = [
        "first thing after TLS started",
        "last thing ever"]

    def connectionMade(self):
        for l in self.pretext:
            self.sendLine(l)

    def lineReceived(self, line):
        print "received: " + line
        if line == "READY":
            ctx = ClientTLSContext()
            self.transport.startTLS(ctx, self.factory)
            for l in self.posttext:
                self.sendLine(l)
            self.transport.loseConnection()

class TLSClientFactory(ClientFactory):
    protocol = TLSClient

    def clientConnectionFailed(self, connector, reason):
        print "connection failed: ", reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "connection lost: ", reason.getErrorMessage()
        reactor.stop()

if __name__ == "__main__":
    factory = TLSClientFactory()
    reactor.connectTCP('localhost', 8000, factory)
    reactor.run()
