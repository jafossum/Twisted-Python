# SSL /TLS Encryption testing

## Sources for creating client server using TLS / SSL encryption and validation

Twisted:
http://twistedmatrix.com/documents/12.0.0/core/howto/ssl.html

Certificates:
https://datacenteroverlords.com/2012/03/01/creating-your-own-ssl-certificate-authority/

## openssl commandline options

Writing and receiving data on SSL socket using openssl s_client

Basic usage without certificate validation:

    $ openssl s_client -cert /home/johnf/Documents/SSH/device.crt -key /home/johnf/Documents/SSH/device.key -connect localhost:8000

Certificate validation:

    $ openssl s_client -connect localhost:8000


## openssl commands:

Creating the root certificate is easy and can be done quickly. Once you do these steps,
you’ll end up with a root SSL certificate that you’ll install on all of your desktops,
and a private key you’ll use to sign the certificates that get installed on your various devices.
Create the Root Key
The first step is to create the private root key which only takes one step.
In the example below, I’m creating a 2048 bit key:

### Create the Root Key:
The first step is to create the private root key which only takes one step.
In the example below, I’m creating a 2048 bit key:

    $ openssl genrsa -out rootCA.key 2048

The standard key sizes today are 1024, 2048, and to a much lesser extent, 4096.
I go with 2048, which is what most people use now.
4096 is usually overkill (and 4096 key length is 5 times more computationally intensive than 2048),
and people are transitioning away from 1024. Important note: Keep this private key very private.
This is the basis of all trust for your certificates, and if someone gets a hold of it,
they can generate certificates that your browser will accept.
You can also create a key that is password protected by adding -des3:

    $ openssl genrsa -des3 -out rootCA.key 2048

You’ll be prompted to give a password, and from then on you’ll be challenged password every time you use the key.
Of course, if you forget the password, you’ll have to do all of this all over again.

### The next step is to self-sign this certificate

    $ openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.pem

This will start an interactive script which will ask you for various bits of information.
Fill it out as you see fit.
Once done, this will create an SSL certificate called rootCA.pem, signed by itself, valid for 1024 days,
and it will act as our root certificate.
The interesting thing about traditional certificate authorities is that root certificate is also self-signed.
But before you can start your own certificate authority,
remember the trick is getting those certs in every browser in the entire world.

### Install Root Certificate Into Workstations
For you laptops/desktops/workstations,
you’ll need to install the root certificate into your trusted certificate repositories

### Create A Certificate (Done Once Per Device)
Every device that you wish to install a trusted certificate will need to go through this process.
First, just like with the root CA step, you’ll need to create a private key (different from the root CA)

    $ openssl genrsa -out device.key 2048

Once the key is created, you’ll generate the certificate signing request.

    $ openssl req -new -key device.key -out device.csr

You’ll be asked various questions (Country, State/Province, etc.). Answer them how you see fit.
The important question to answer though is common-name.

> Common Name (eg, YOUR name) []: 10.0.0.1

Whatever you see in the address field in your browser when you go to your device must be what you put under common name,
even if it’s an IP address.
Yes, even an IP (IPv4 or IPv6) address works under common name.
If it doesn’t match, even a properly signed certificate will not validate correctly and you’ll get the “cannot verify authenticity” error.
Once that’s done, you’ll sign the CSR, which requires the CA root key.

    $ openssl x509 -req -in device.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out device.crt -days 500 -sha256

