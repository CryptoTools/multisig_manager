About: 

Multisig Manager is a GUI based python program for working with multisignature transactions in Bitcoin, Litecoin, and Dogecoin. It can create and keep track of multisignature addresses, send coins from a multisignature address, and create signatures for authorizing sends from multisignature addresses.

I created this software in order to fill 4 basic needs that have not yet been filled by the currently available solutions.

a) It is for multisig transactions only. The "wallet" abstraction was not created with multisig in mind, so it can be cumbersome from a user interface viewpoint for a wallet application to handle multisig transactions.

b) It is lightweight (does not need to store or sync with the blockchain). Multisig Manager does not download/process the blockchain directly, instead it relies on third party API's to query the blockchain data required to craft transactions and keep track of account balances. This makes MultisigManager a very light weight application compared to something like Bitcoin-Qt, but it does rely on the availability of these third party services for full functionality.

d) Has local private key storage. This is a better solution for users that want more control over their keys compared to web based multisignature solutions. All created cryptographic public/private keys in Multisig Manager are stored on disk using Sqlite with an option to encrypt the private key using a password.

e) Can be ported to Bitcoin derived alt coins easily, as many altcoins lack user friendly methods of working with multisig transactions.

The software is experimental and in alpha stage. Do not use this software for any purpose other than testing. It is intended for advanced users only.


Dependencies : 

PyQT 4
PyCrypt 2.6.1
simplecrypt by Andrew Cook (https://github.com/andrewcooke/simple-crypt )
Forked pybitcointools library. Original pybitcointools by Vitalik Buterin  (https://github.com/kaykurokawa/pybitcointools)
kcryptotools by Umpei Kay Kurokawa ( https://github.com/kaykurokawa/kcryptotools )

Written and tested for Python 2.7 running under Ubuntu Linux 14.04.

Installation: 

Run install.sh to download and install dependencies. 
 
