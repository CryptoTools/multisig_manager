#!/bin/bash
# download and install required packages for multisig manager 

git clone https://github.com/andrewcooke/simple-crypt
(cd simple-crypt; python setup.py install)
git clone https://github.com/kaykurokawa/pybitcointools
(cd pybitcointools; python setup.py install)
git clone https://github.com/kaykurokawa/kcryptotools
(cd kcryptotools; python setup.py install)
pip install pycrypto 
sudo apt-get install python-qt4
