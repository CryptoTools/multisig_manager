#!/bin/bash
# download and install required packages

git clone https://github.com/andrewcooke/simple-crypt
(cd simple-crypt; python setup.py install)
git clone https://github.com/kaykurokawa/pybitcointools
(cd pybitcointools; python setup.py install)
git clone https://github.com/kaykurokawa/kcryptotools
(cd kcryptotools; python setup.py install)
pip install pycrypto  
