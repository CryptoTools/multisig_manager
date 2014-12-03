About: 

Multisig Manager is a light weight GUI based python tool for working with multisignature addresses in Bitcoin, Litecoin, and Dogecoin. It can create and keep track of multisignature addresses, send coins from a multisignature address, and create signatures for authorizing sends from multisignature addresses. 

It does not download/process the blockchain directly, instead it relies on third party API's (currently using blockchain.info,dogecoin.info, and litecoin.toshi.io) to query the blockchain data required to craft transactions and keep track of account balances. This makes MultisigManager a very light weight application compared to something like Bitcoin-Qt, but it does rely on the availability of these third party services for full functionality. 

All created cryptographic public/private keys are stored on disk using Sqlite with an option to encrypt the private key using a password.  

The software is experimental and in alpha stage. Do not use this software for any purpose other than testing. It is intended for advanced users only. 

Dependencies : 

PyQT 4
PyCrypt 2.6.1
simplecrypt by Andrew Cook (  https://github.com/andrewcooke/simple-crypt )
pybitcointools library by Vitalik Buterin ( https://github.com/vbuterin/pybitcointools )
kcryptotools by Umpei Kay Kurokawa ( https://github.com/kaykurokawa/kcryptotools )

Written and tested for Python 2.7 running under Ubuntu Linux 14.04

