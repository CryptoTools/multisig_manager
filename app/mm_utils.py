import json
import random 
import bitcoin

# utility functions/classes for multisig manager
#


# Just a 2-d list to store signature temporarily
# Used in dialogue to craft multisig transactions
class SignatureList(object):

    def __init__(self,num_unspents,num_keys):
        self.num_unspents=num_unspents
        self.num_keys=num_keys
        len_list=num_unspents*num_keys
        self.sig_list=[None]*len_list
    
    def set(self,unspent_i,key_i,signature):
        self.sig_list[unspent_i*self.num_keys +key_i] = signature

    def get(self,unspent_i,key_i):
        return self.sig_list[unspent_i*self.num_keys +key_i]
    
    def get_signatures_as_list(self,unspent_i,list_key_indices):
        out_list_keys=[]

        for key_i in list_key_indices:
            if self.key_is_complete(key_i):
                out_list_keys.append( self.get(unspent_i,key_i) )
            else:
                raise Exception("Key is not complete")
        return out_list_keys

    # return True if we have enough signatures for m of n transaction
    def is_complete(self,m):
        num_complete_signatures=0
        for key_i in range(0,self.num_keys):
            if self.key_is_complete(key_i):
                num_complete_signatures+=1

        if num_complete_signatures >= m:
            return True
        else:
            return False

    # key is complete if we have signatures for every unspent1
    def key_is_complete(self,key_i):
        for unspent_i in range(0, self.num_unspents):
            if self.get(unspent_i,key_i) == None:
                return False
        return True    

def get_unspents(multisig_addr,crypto_type):
    try:
        if crypto_type.lower() == 'bitcoin':
            unspents        = bitcoin.unspent(multisig_addr)
        elif crypto_type.lower() == 'litecoin':
            unspents        = bitcoin.litecoin_unspent(multisig_addr)
        elif crypto_type.lower() == 'dogecoin':
            unspents        = bitcoin.dogecoin_unspent(multisig_addr)
        else:
            return None
        return unspents
    except Exception as e:
        print(str(e))
        return None

