import datetime
import sqlite3 
import pybitcointools 
import simplecrypt

SQLITE_FILENAME='multisig_gui.db'

# set up sqlite
conn=sqlite3.connect(SQLITE_FILENAME,detect_types=sqlite3.PARSE_DECLTYPES)#after converting to server mode, remove check_same_thread=False
conn.text_factory=str
c=conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS crypto_key \
          (crypto_key_id INTEGER PRIMARY KEY,crypto,public_key,private_key,encrypted_private_key,timestamp)')
c.execute('CREATE TABLE IF NOT EXISTS multisig_addr(multisig_addr_id INTEGER PRIMARY KEY,crypto,address,m,n,timestamp)')
c.execute('CREATE TABLE IF NOT EXISTS multisig_own(crypto_key_id INTEGER,multisig_addr_id INTEGER)')
conn.commit()

def get_m_n_for_multisig_address(multisig_address):
    c.execute('SELECT * FROM multisig_addr WHERE address = ?',(multisig_address,))
    row=c.fetchone()
    return (row[3],row[4])


# get all public key used to create the multisig address
def get_keys_for_multisig_address(multisig_address):
    c.execute('SELECT * FROM multisig_addr WHERE address = ?',(multisig_address,))
    row=c.fetchone()
    multisig_addr_id=row[0]

    text_str='SELECT crypto_key_id FROM multisig_own WHERE multisig_addr_id = ?',(multisig_addr_id,)
    c.execute(text_str)
    crypto_key_ids = c.fetchall()
    list_keys=[]
    for id in crypto_key_ids:
        c.execute('SELECT * FROM crypto_key WHERE crypto_key_id = ?',(id[0],))
        row=c.fetchone()
        public_key=row[2] 
        private_key=row[3]
        if private_key==0:
            private_key=None
        encrypted_private_key=row[4]
        if encrypted_private_key==0:
            encrypted_private_key=None
        list_keys.append({'public_key':public_key,'private_key':private_key,'encrypted_private_key':encrypted_private_key})
    return list_keys

# get all crypto keys as rows
def get_all_crypto_keys(crypto=None):
    if crypto == None:
        c.execute('SELECT * FROM crypto_key')
    else:
        c.execute('SELECT * FROM crypto_key WHERE crypto = ?',(crypto,))
    return c.fetchall()

# get all multisig addresses as rows
def get_all_multisig_addresses(crypto=None):
    if crypto == None:
        c.execute('SELECT * FROM multisig_addr')
    else:
        c.execute('SELECT * FROM multisig_addr WHERE crypto = ?',(crypto,))
    return c.fetchall() 

# create multisig address
def create_multisig_address(crypto,m,n,pub_key_list):
    if n!=len(pub_key_list):
        raise Exception('n is not the same as length of pub_key_list') 

    crypto_key_id_list=[]
    for pub_key in pub_key_list:
        c.execute('SELECT * FROM crypto_key WHERE public_key = ?',(pub_key,))
        rows=c.fetchall()
        # create crypto_key entry if public key is not found in database
        if len(rows) ==0:
            c.execute('INSERT INTO crypto_key(crypto,public_key,private_key,encrypted_private_key,timestamp) VALUES(?,?,?,?,?)',
                      (crypto,pub_key,0,0,datetime.datetime.now()))
            crypto_key_id_list.append(c.lastrowid)
            conn.commit()
        else:           
            crypto_key_id_list.append(rows[0][0])
    script=pybitcointools.mk_multisig_script(pub_key_list,m)
    address=pybitcointools.scriptaddr(script)
    
    c.execute('INSERT INTO multisig_addr(crypto,address,m,n,timestamp) VALUES(?,?,?,?,?)',
              (crypto,address,m,n,datetime.datetime.now()))
    multisig_addr_id=c.lastrowid 
    conn.commit() 
    #now we need to create multisig_own 
    for crypto_key_id in crypto_key_id_list: 
        c.execute('INSERT INTO multisig_own(crypto_key_id,multisig_addr_id) VALUES(?,?)'
            ,(crypto_key_id,multisig_addr_id))
        conn.commit()

    return address  

# create private/public key pair
def create_key(crypto):
    private_key = pybitcointools.random_key()
    public_key  = pybitcointools.privtopub(private_key)    
    c.execute('INSERT INTO crypto_key (crypto,public_key,private_key,encrypted_private_key,timestamp) VALUES(?,?,?,?,?)',
        (crypto,public_key,private_key,0,datetime.datetime.now()))
    conn.commit()
    return public_key


# create private/public key pair
def create_encrypted_key(crypto,password):
    private_key = pybitcointools.random_key()
    public_key  = pybitcointools.privtopub(private_key)    
    # encrypt private key here
    encrypted_private_key=simplecrypt.encrypt(password=password,data=private_key)
    c.execute('INSERT INTO crypto_key (crypto,public_key,private_key,encrypted_private_key,timestamp) VALUES(?,?,?,?,?)',
        (crypto,public_key,0,encrypted_private_key,datetime.datetime.now()))
    conn.commit()
    return public_key

# will return False if password is incorrect
def decrypt_private_key(encrypted_private_key,password):
    try:
        priv_key=simplecrypt.decrypt(password=password,data=encrypted_private_key)
    except simplecrypt.DecryptionException:
        return False 
    return priv_key    
        
