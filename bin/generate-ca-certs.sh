#!/bin/bash
 
SPLUNK_HOME=/opt/splunk
CAPK=myCAPrivateKey.key
CACERTCSR=myCACertificate.csr
CACERTPEM=myCACertificate.pem
 
$SPLUNK_HOME/bin/splunk cmd openssl genrsa -aes256 -out $CAPK 2048
$SPLUNK_HOME/bin/splunk cmd openssl req -new -key $CAPK -out $CACERTCSR
$SPLUNK_HOME/bin/splunk cmd openssl x509 -req -in $CACERTCSR -sha512 -signkey $CAPK -CAcreateserial -out $CACERTPEM -days 1095
