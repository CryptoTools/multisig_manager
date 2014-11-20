import sys

import multisig_sqlite
import mg_utils

import simplecrypt
import pybitcointools
from PyQt4.QtCore import *
from PyQt4.QtGui import *

CRYPTO_TYPES=['Bitcoin','Litecoin','Dogecoin']
MAX_M=10
MAX_N=10


def dialog_getScreenSize():
    screen=QDesktopWidget().screenGeometry()
    return (screen.width(),screen.height())

def dialog_showError(parent,msg):
    QMessageBox.critical(parent,"Error",msg)
    raise Exception(msg)

def dialog_showMessage(parent,msg):
    QMessageBox.about(parent,"Info",msg)

def dialog_init(dialog,window_title,parent=None):
    dialog.setWindowTitle(window_title)
    dialog.layout=QGridLayout()
    dialog.setLayout(dialog.layout)
    dialog.list_of_widgets=[]

def dialog_addWidget(dialog,widget):
    dialog.layout.addWidget(widget)
    dialog.list_of_widgets.append(widget)

def dialog_disableAllWidgets(dialog):
    for widget in dialog.list_of_widgets:
        widget.setEnabled(False)
def dialog_setFixedSize(dialog):
    dialog.resize(0,0)
    dialog.setFixedSize(dialog.size())

def dialog_addScrollArea(dialog,list_of_widgets_in_area):
    scroll_area_layout=QGridLayout()
    scroll_area_widget=QWidget()
    scroll_area=QScrollArea()

    scroll_area_widget.setLayout(scroll_area_layout)
    scroll_area_width=dialog.size().width()
    scroll_area_height=dialog_getScreenSize()[1] -dialog.size().height()-200
    scroll_area.setFixedHeight(scroll_area_height)
    scroll_area.setWidget(scroll_area_widget)
    scroll_area.setWidgetResizable(True)
    for widget in list_of_widgets_in_area:
        scroll_area_layout.addWidget(widget)
        dialog.list_of_widgets.append(widget)
                
    dialog.layout.addWidget(scroll_area)


class CreatePublicKeyDialog(QDialog):
    def __init__(self,crypto_type,parent=None):

        QDialog.__init__(self,parent)
        self.crypto_type=crypto_type
        dialog_init(self,"Create public key".format(self.crypto_type),parent)
        dialog_addWidget(self,QLabel("Would you like to encrypt the private key with a password?")) 
        self.yes_encrypt_button=QPushButton("Yes")
        self.yes_encrypt_button.clicked.connect(self.case_yes_encrypt)
        self.no_encrypt_button=QPushButton("No")
        self.no_encrypt_button.clicked.connect(self.case_no_encrypt)
        dialog_addWidget(self,self.yes_encrypt_button)
        dialog_addWidget(self,self.no_encrypt_button)
        dialog_setFixedSize(self)
    def case_no_encrypt(self):
        dialog_disableAllWidgets(self)
        pub_key=multisig_sqlite.create_key(self.crypto_type)
        dialog_showMessage(self,"Created public key:  "+pub_key)
 
    def case_yes_encrypt(self):
        dialog_disableAllWidgets(self)
        dialog_addWidget(self,QLabel("Enter Password"))
        self.pw_line_edit1=QLineEdit()
        self.pw_line_edit1.setEchoMode(QLineEdit.Password)
        self.pw_line_edit2=QLineEdit()
        self.pw_line_edit2.setEchoMode(QLineEdit.Password)
        dialog_addWidget(self,self.pw_line_edit1)
        dialog_addWidget(self,QLabel("Enter Password Again"))
        dialog_addWidget(self,self.pw_line_edit2)        
        self.submit_pw_button=QPushButton("Submit") 
        self.submit_pw_button.clicked.connect(self.submit_password)
        dialog_addWidget(self,self.submit_pw_button)
    
    def submit_password(self):
        dialog_disableAllWidgets(self)
        if self.pw_line_edit1.text() != self.pw_line_edit2.text():
            dialog_showError(self,"Password does not match")
        else: 
            password=str(self.pw_line_edit1.text())

        if len(password) == 0:
            dialog_showError(self,'Password is empty')
        
        pub_key=multisig_sqlite.create_encrypted_key(self.crypto_type,password) 
        dialog_showMessage(self,"Created public key: "+pub_key)


class SendTransactionDialog(QDialog):
    def __init__(self,crypto_type,parent=None):
        QDialog.__init__(self,parent)
        self.crypto_type=crypto_type
        dialog_init(self,"Send transaction from {} multisignature address".format(self.crypto_type),parent)

        label=QLabel("Select multisignature address to send from")
        self.combo_box=QComboBox()        
        addresses=multisig_sqlite.get_all_multisig_addresses(self.crypto_type)
        for address in addresses:
            self.combo_box.addItem(address[2])

        self.combo_box.activated.connect(self.address_chosen) 
        dialog_addWidget(self,label)
        dialog_addWidget(self,self.combo_box)

    def address_chosen(self):
        address=self.combo_box.currentText()
        dialog_disableAllWidgets(self)
        label=QLabel("Enter destination address")
        dialog_addWidget(self,label)
        self.destination_line_edit=QLineEdit()
        dialog_addWidget(self,self.destination_line_edit)
        label=QLabel("Enter amount to send (satoshis)")
        dialog_addWidget(self,label)
        self.amount_line_edit=QLineEdit()
        dialog_addWidget(self,self.amount_line_edit) 
        self.destination_button=QPushButton("Submit Destination")
        self.destination_button.clicked.connect(self.destination_chosen)
        dialog_addWidget(self,self.destination_button)

    def destination_chosen(self):
        # disable buttons
        dialog_disableAllWidgets(self)

        # get destination and amount
        destination_address = str(self.destination_line_edit.text())
        try:
            amount              = int(str(self.amount_line_edit.text()))
        except ValueError:
            dialog_showError(self,"Amount must be an integer")
        multisig_addr       = str(self.combo_box.currentText())
        try:
            if self.crypto_type == 'Bitcoin':
                unspents        = pybitcointools.unspent(multisig_addr)
            else:
                unspents        = utils.litecoin_unspent(multisig_addr)
        except Exception as e:
            dialog_showError(self,"Failed to get unspent amount from third party API")
        sum_unspents    = sum([unspent['value'] for unspent in unspents])
    
        if amount < 1: #dust? 
            dialog_showError(self,'Amount must be greater than dust') 
        
        if sum_unspents < amount:
            dialog_showError(self,'Not enough unspent amount in addresss, unspent amount is '+str(sum_unspents))

        m,n     = multisig_sqlite.get_m_n_for_multisig_address(multisig_addr)
        tx_fees = 1
        outs    = [{'value':amount-tx_fees,'address':destination_address}]
        ins     = [unspent['output'] for unspent in unspents]
        tx      = pybitcointools.mktx(ins,outs)    

        keys            = multisig_sqlite.get_keys_for_multisig_address(multisig_addr)
        public_keys     = [key['public_key'] for key in keys]
        multisig_script = pybitcointools.mk_multisig_script(public_keys,m)

        num_encrypted_keys  = sum(key['private_key']==None and key['encrypted_private_key']!=None for key in keys)
        num_unknown_keys    = sum(key['private_key']==None and key['encrypted_private_key']==None for key in keys)
        num_known_keys      = len(keys) - num_encrypted_keys - num_unknown_keys
        self.sig_entries    = {} # key = (key index, unspent index) value = (QLabel, QLineEdit)
        self.pass_entries   = {} # key = key index value=(QLabel,QLineEdit)

        self.sig_list=mg_utils.SignatureList(len(unspents),len(keys))
        for key_i in range(0,len(keys)):
            print('keys', keys[key_i] )
            # we need signature
            if keys[key_i]['private_key']==None and keys[key_i]['encrypted_private_key']==None: 
                for unspent_i in range(0,len(unspents)):
                    label       = QLabel('Signature for public key: {}\n For tx: {}'.
                        format(keys[key_i]['public_key'],unspents[unspent_i]))
                    line_edit   = QLineEdit()
            
                    self.sig_entries[(key_i,unspent_i)]=(label,line_edit)
                    
            # we need password for encrypted key
            elif keys[key_i]['private_key']==None and keys[key_i]['encrypted_private_key']!=None:
                label       = QLabel('Password for public key: {}'.format(keys[key_i]['public_key']))
                line_edit   = QLineEdit()
                line_edit.setEchoMode(QLineEdit.Password)

                self.pass_entries[key_i]=(label,line_edit)

            # we can get signature 
            else:
                for unspent_i in range(0,len(unspents)):
                    signature=pybitcointools.multisign(tx,unspent_i,multisig_script,keys[key_i]['private_key'])
                    self.sig_list.set(unspent_i,key_i,signature)
        if self.sig_list.is_complete(m):
            self.apply_signatures(tx,m,multisig_script)
        else:
            dialog=QDialog(self)
            dialog_init(dialog,"Please provide signature or password")
            str_out="At least {} key(s) need to be unlocked to complete transaction".format(m - num_unknown_keys) 
            dialog_addWidget(dialog,QLabel(str_out))
            scroll_area_widgets=[]
            for key,value in self.sig_entries.items():
                scroll_area_widgets.append(QLabel("<b>Signature request</b>"))
                scroll_area_widgets.append(value[0])
                scroll_area_widgets.append(value[1])

            for key,value in self.pass_entries.items():


                scroll_area_widgets.append(QLabel("<b>Password request</b>"))
                scroll_area_widgets.append(value[0])
                scroll_area_widgets.append(value[1])
            dialog_addScrollArea(dialog,scroll_area_widgets)


            self.pass_and_sig_button=QPushButton('Submit')
            self.pass_and_sig_button.clicked.connect(
                lambda clicked,tx=tx,m=m,num_unknown_keys=num_unknown_keys,
                       multisig_script=multisig_script,keys=keys,unspents=unspents: 
                self.get_pass_and_sig(tx,m,num_unknown_keys,multisig_script,keys,unspents))
            dialog_addWidget(dialog,self.pass_and_sig_button)
            dialog.show()

    def get_pass_and_sig(self,tx,m,num_unknown_keys,multisig_script,keys,unspents):

        for key,value in self.sig_entries.items():
            entry=value[1]
            key_i=key[0]
            unspent_i=key[1]
            signature=str(entry.text())
            if len(signature) != 0: 
                self.sig_list.set(unspent_i,key_i,signature)
        for key,value in self.pass_entries.items():
            key_i=key
            entry=value[1]
            password=str(entry.text() )
            if len(password) != 0:
                private_key=multisig_sqlite.decrypt_private_key(keys[key_i]['encrypted_private_key'],password)
                if private_key == False:
                    dialog_showError(self,"Failed to decrypt, wrong password")
                for unspent_i in range(0,len(unspents)):
                    signature=pybitcointools.multisign(tx,unspent_i,multisig_script,private_key)
                    self.sig_list.set(unspent_i,key_i,signature)
                
        if self.sig_list.is_complete(m):
            dialog_disableAllWidgets(self)
            self.apply_signatures(tx,m,multisig_script)
        else:
            dialog_showError(self,"Not enough password/signatre was provided. Requires at least {}".format(m-num_unknown_keys))

    def apply_signatures(self,tx,m,multisig_script):
        if not self.sig_list.is_complete(m):
            dialog_showError(self,"Not enough signatures")

        for unspent_i in range(0,self.sig_list.num_unspents):
            cur_sig_list=self.sig_list.get_signatures_as_list(unspent_i)
            tx=pybitcointools.apply_multisignatures(tx,unspent_i,multisig_script,cur_sig_list)
        dialog_showMessage(self,tx)
        return tx 

class CreateMultiSigDialog(QDialog):
    def __init__(self,crypto_type,parent=None):
        QDialog.__init__(self,parent)
        self.crypto_type=crypto_type
        dialog_init(self,"Create Multisignature address",parent)
        
        m_label=QLabel()
        m_label.setText("m (required signatures)")
        self.m_input=QLineEdit()

        n_label=QLabel()
        n_label.setText("n (total signatures)")
        self.n_input=QLineEdit()

        self.m_of_n_submit_button=QPushButton("Submit")
        self.m_of_n_submit_button.clicked.connect(self.process_m_of_n)

        dialog_addWidget(self,QLabel("<b>Create m of n multisignature address</b>"))   
        dialog_addWidget(self,m_label)
        dialog_addWidget(self,self.m_input)

        dialog_addWidget(self,n_label)
        dialog_addWidget(self,self.n_input)        
        dialog_addWidget(self,self.m_of_n_submit_button)

        dialog_setFixedSize(self)

    def process_m_of_n(self):
        m=self.m_input.text()
        n=self.n_input.text()
        int_m=int(m)
        int_n=int(n)
        if int_m > MAX_M:
            error_msg='m is too large, maximum is:'+str(MAX_M)
            dialog_showError(self,error_msg)
        if int_n >MAX_N:
            error_msg='n is too large, maximum is:'+str(MAX_N)
            dialog_showError(self,error_msg)
        if int_m>int_n:
            error_msg='m:{} cannot be larger than n:{}'.format(int_m,int_n)
            dialog_showError(self,error_msg)
        self.m=int_m
        self.n=int_n
        dialog_disableAllWidgets(self)


        self.entry_button_list=[]
        self.scroll_area_widgets=[]
        for i in range(0,int_n):
            label=QLabel('Enter public key '+str(i+1))
            entry=QLineEdit()
            button=QPushButton("Select from created key ")
            button.clicked.connect(lambda clicked,index=i: self.show_key_list(index))
            self.scroll_area_widgets.append(label)
            self.scroll_area_widgets.append(entry)
            self.scroll_area_widgets.append(button)

            #dialog_addWidget(self,label)
            #dialog_addWidget(self,entry)
            #dialog_addWidget(self,button)
            self.entry_button_list.append((entry,button))
        self.submit_button=QPushButton(text='Submit')
        self.submit_button.clicked.connect(self.create_multisig_address)
        #self.scroll_area_widgets.append(self.submit_button)

        dialog_addScrollArea(self,self.scroll_area_widgets) 
        dialog_addWidget(self,self.submit_button)
 
    def show_key_list(self,entry_index):
        self.list_pubkey_dialog=ListPubKeyDialog(self.crypto_type,True)
        self.list_pubkey_dialog.show()
        pub_key_index=0
        for button in self.list_pubkey_dialog.select_button_list:
            button.clicked.connect(
                lambda clicked,entry_index=entry_index,pub_key_index=pub_key_index: self.select_key(entry_index,pub_key_index))
            pub_key_index+=1

    def select_key(self,entry_index,pub_key_index):
        pub_key=self.list_pubkey_dialog.pub_key_list[pub_key_index]
        self.entry_button_list[entry_index][0].setReadOnly(True)
        self.entry_button_list[entry_index][0].setText(pub_key)
        self.entry_button_list[entry_index][0].setEnabled(False)
        self.entry_button_list[entry_index][1].setEnabled(False)
        self.list_pubkey_dialog.close()

    def create_multisig_address(self):
        pub_key_list=[str(entry[0].text()) for entry in self.entry_button_list]         
        address= multisig_sqlite.create_multisig_address(self.crypto_type,self.m,self.n,pub_key_list)        
        dialog_showMessage(self,"Multisig address created: "+address)
        dialog_disableAllWidgets(self)

class DecryptPrivKeyDialog(QDialog):
    def __init__(self,crypto_type,encrypted_private_key,parent=None):
        QDialog.__init__(self,parent)
        self.crypto_type=crypto_type
        self.encrypted_private_key=encrypted_private_key
        
        self.setWindowTitle("Decrypt Private Key") 
        layout=QGridLayout()

        layout.addWidget(QLabel("Enter password"))
        self.pass_line_edit=QLineEdit()
        self.pass_line_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_line_edit)
    
        self.submit_button=QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_pass )
        layout.addWidget(self.submit_button)
        
        self.setLayout(layout)

    def submit_pass(self):
        password=str(self.pass_line_edit.text())
        private_key=multisig_sqlite.decrypt_private_key(self.encrypted_private_key,password)
        if private_key == False:
            dialog_showError(self,"Failed to decrypt, wrong password") 
        else:
            dialog_showMessage(self,"Decrypted private key: "+private_key)

class ListPubKeyDialog(QDialog):

    def __init__(self,crypto_type,include_select_button,parent=None):
        QDialog.__init__(self,parent)
        self.crypto_type=crypto_type
        self.include_select_button=include_select_button
        self.select_button_list=[]
        self.pub_key_list=[]

        dialog_init(self,"List {} Public Keys".format(self.crypto_type),parent)

        crypto_keys=multisig_sqlite.get_all_crypto_keys(crypto_type)
        self.table=QTableWidget()
        self.table.setRowCount(len(crypto_keys))
        if self.include_select_button==True:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderItem(0,QTableWidgetItem('Select'))
            self.table.setHorizontalHeaderItem(1,QTableWidgetItem('Public Key'))
            self.table.setHorizontalHeaderItem(2,QTableWidgetItem('Private Key'))
            self.table.setHorizontalHeaderItem(3,QTableWidgetItem('Creation Time'))
        else:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderItem(0,QTableWidgetItem('Public Key'))
            self.table.setHorizontalHeaderItem(1,QTableWidgetItem('Private Key'))
            self.table.setHorizontalHeaderItem(2,QTableWidgetItem('Creation Time'))
        row_index=0
        for row in crypto_keys:            
            crypto=row[1]
            pub_key=row[2]
            self.pub_key_list.append(pub_key)
            priv_key=row[3]
            encrypted_priv_key=row[4]
            timestamp=row[5]
            priv_key_is_encrypted = (priv_key ==0 and encrypted_priv_key != 0)
            if priv_key == 0 and encrypted_priv_key == 0:
                priv_key='Private key unknown'
            elif priv_key_is_encrypted:
                priv_key=QPushButton('Click to decrypt encrypted private key')
                priv_key.clicked.connect(lambda clicked,encrypted_priv_key=encrypted_priv_key : 
                    self._decrypt_private_key(encrypted_priv_key) )
            if self.include_select_button==True:
                button=QPushButton("Select")
                self.select_button_list.append(button)
                self.table.setCellWidget(row_index,0,button)
                self._setItem(row_index,1,pub_key)
                if priv_key_is_encrypted:
                    self.table.setCellWidget(row_index,2,priv_key)
                else:
                    self._setItem(row_index,2,priv_key)
                self._setItem(row_index,3,timestamp)
            else:
                self._setItem(row_index,0,pub_key)
                if priv_key_is_encrypted:
                    self.table.setCellWidget(row_index,1,priv_key)
                else:
                    self._setItem(row_index,1,priv_key)
                self._setItem(row_index,2,timestamp)
            
            row_index+=1
        if self.include_select_button == True:

            self.table.resizeColumnToContents(0)
            self.table.resizeColumnToContents(2)
            self.table.resizeColumnToContents(3)
        else: 
            self.table.resizeColumnToContents(1)
            self.table.resizeColumnToContents(2)

        dialog_addWidget(self,self.table)
 

    def _setItem(self,row_i,col_i,item):
        elem=QTableWidgetItem(item)
        elem.setFlags(Qt.ItemIsEnabled)       
        self.table.setItem(row_i,col_i,elem)

    def _decrypt_private_key(self,encrypted_private_key):
        self.dialog=DecryptPrivKeyDialog(self.crypto_type,encrypted_private_key)
        self.dialog.show()

class ListMultiSigDialog(QDialog):
    def __init__(self,crypto_type,parent=None):
        QDialog.__init__(self,parent)
        self.crypto_type=crypto_type
        
        dialog_init(self,"List Multisig Addresses",parent)

        self.table=QTableWidget()
        multisig_addresses=multisig_sqlite.get_all_multisig_addresses(self.crypto_type)
        row_count=len(multisig_addresses)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(MAX_N+3)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setHorizontalHeaderItem(0,QTableWidgetItem('Address'))
        self.table.setHorizontalHeaderItem(1,QTableWidgetItem('M of N'))
        self.table.setHorizontalHeaderItem(2,QTableWidgetItem('Creation Time'))
        for i in range(3,MAX_N+3):
            self.table.setHorizontalHeaderItem(i,QTableWidgetItem('Public Key '+str(i-2)))

        row_index=0
        for row in multisig_addresses:
            col_index=0
            id          = row[0]
            crypto      = row[1]
            addr        = row[2]
            m           = row[3]
            n           = row[4]
            timestamp   = row[5]
            m_of_n_str  = str(m)+' of '+str(n)

            self._setItem(row_index,col_index,addr)
            col_index+=1
            self._setItem(row_index,col_index,m_of_n_str)
            col_index+=1
            self._setItem(row_index,col_index,timestamp)
            for key in multisig_sqlite.get_keys_for_multisig_address(addr):
                col_index+=1 
                self._setItem(row_index,col_index,key['public_key'])
            
            row_index+=1
           
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)

        dialog_addWidget(self,self.table)
    
    def _setItem(self,row_i,col_i,item):
        elem=QTableWidgetItem(item)
        elem.setFlags(Qt.ItemIsEnabled)
        self.table.setItem(row_i,col_i,elem)

class MyForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Multisig GUI")

        qwidget=QWidget()           
        self.layout=QGridLayout()
        qwidget.setLayout(self.layout) 

        
        self.layout.addWidget(QLabel("Select Crypto"))
        self.coin_select_combo_box=QComboBox()
        for crypto in CRYPTO_TYPES:
            self.coin_select_combo_box.addItem(crypto)
        self.layout.addWidget(self.coin_select_combo_box)

        self.layout.addWidget(QLabel("Tasks"))

        self.createPubKeyButton=QPushButton('Create Public Key')
        self.layout.addWidget(self.createPubKeyButton)
        self.listPubKeyButton=QPushButton('List Public Key')
        self.layout.addWidget(self.listPubKeyButton)
        self.createMultisigButton=QPushButton('Create Multisignature Address')
        self.layout.addWidget(self.createMultisigButton)
        self.listMultisigButton=QPushButton('List Multisignature Address')
        self.layout.addWidget(self.listMultisigButton)
        self.sendTransactionButton=QPushButton('Send Transaction From Multisig Address')
        self.layout.addWidget(self.sendTransactionButton)
        self.sentTransactionButton=QPushButton('Sign Transaction From Multisig Address') 
       
        self.setCentralWidget(qwidget)

        self.connect(self.createPubKeyButton,SIGNAL("clicked()"),self.createPubKey)
        self.connect(self.listPubKeyButton,SIGNAL("clicked()"),self.listPubKey)
        self.connect(self.createMultisigButton,SIGNAL("clicked()"),self.createMultisig)
        self.connect(self.listMultisigButton,SIGNAL("clicked()"),self.listMultisig)
        self.connect(self.sendTransactionButton,SIGNAL("clicked()"),self.sendTransaction)
        
        self.resize(0,0)
        self.setFixedSize(self.size())

    def _getSelectedCrypto(self):
        return str(self.coin_select_combo_box.currentText())
    
    def createPubKey(self):
        self.create_pubkey_dialog=CreatePublicKeyDialog(self._getSelectedCrypto())
        self.create_pubkey_dialog.show()

    def listPubKey(self):
        self.list_pubkey_dialog=ListPubKeyDialog(self._getSelectedCrypto(),False)
        self.list_pubkey_dialog.show()

    def createMultisig(self):
        self.create=CreateMultiSigDialog(self._getSelectedCrypto())
        self.create.show()

    def listMultisig(self):
        self.list_multisig_dialog=ListMultiSigDialog(self._getSelectedCrypto())
        self.list_multisig_dialog.show()

    def sendTransaction(self):
        self.send_dialog=SendTransactionDialog(self._getSelectedCrypto())
        self.send_dialog.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
