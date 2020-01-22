#!/bin/bash
  
SPLUNK_HOME=/opt/splunk
CAPK=myCAPrivateKey.key
CACERTPEM=myCACertificate.pem
SERVERPK=myServerPrivateKey.key
SERVERCERTCSR=myServerCertificate.csr
SERVERCERTPEM=myServerCertificate.pem
SERVERSINGLEPEM=myNewServerCertificate.pem
  
$SPLUNK_HOME/bin/splunk cmd openssl genrsa -aes256 -out $SERVERPK 2048
# (optional) Remove password for Splunkweb
read -p "Remove password for Splunk-Web? y/n: " yn
if [ "$yn" == "y" ]; then
  $SPLUNK_HOME/bin/splunk cmd openssl rsa -in $SERVERPK -out $SERVERPK
  $SPLUNK_HOME/bin/splunk cmd openssl rsa -in $SERVERPK -text
fi
 
$SPLUNK_HOME/bin/splunk cmd openssl req -new -key $SERVERPK -out $SERVERCERTCSR
$SPLUNK_HOME/bin/splunk cmd openssl x509 -req -in $SERVERCERTCSR -SHA256 -CA $CACERTPEM -CAkey $CAPK -CAcreateserial -out $SERVERCERTPEM -days 1095
 
cat $SERVERCERTPEM $SERVERPK $CACERTPEM > $SERVERSINGLEPEM
