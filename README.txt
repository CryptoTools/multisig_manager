Multisig GUI is a GUI based python tool for working with multisignature addresses in Bitcoin (it also works with
Litecoin, as it uses the same exact method for p2sh multisignature transactions). It can create and keep track 
of multisignature addresses, send coins from a multisignature address, and create signatures for authorizing 
sends from multisignature addresses. 

It does not download/process the blockchain directly, instead it uses third party API's (currently using
blockchain.info) to query the blockchain data required to create transactions, keep track of account balances,
and push transactions out to the network. All created cryptographic public/private keys are stored on disk using 
Sqlite. 

The software is experimental, and is intended for advanced users only. 


Dependencies : 
PyQT 4
PyCrypt 2.6.1
pybitcointools library by Vitalik Buterin: https://github.com/vbuterin/pybitcointools
simplecrypt by Andrew Cook :https://github.com/andrewcooke/simple-crypt


Written and tested for Python 2.7 running under Ubuntu Linux 12.07

