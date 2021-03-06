import os
import urllib.request
import random

class installVpnAC():

    configurl_files_url_AES_UDP = 'https://vpn.ac/ovpn/AES-256-UDP.zip'
    configurl_files_url_AES_TCP = 'https://vpn.ac/ovpn/AES-256-TCP.zip'

    c_logdir = os.path.dirname(os.path.realpath(__file__)) + '/vpnac_log'
    c_vpn_config_dir = os.path.dirname(os.path.realpath(__file__)) + '/vpnac_openvpn_config_files'
    c_userpass_dir = os.path.dirname(os.path.realpath(__file__)) + '/vpnac_open_vpn_userpass'

    c_config_AES256TCP_folder_name = 'AES-256-TCP'
    c_config_AES256UDP_folder_name = 'AES-256-UDP'

    userpass_file_name = 'user.txt'

    vpnusern_ = 'vpn63768491'
    vpnpassw_ = 'Test_12345'


    def __init__(self,openvpn_user, openvpn_passw):

        self.vpnusern_ = openvpn_user
        self.vpnpassw_ = openvpn_passw
        pass


    def startVpn(self, UDP = False):

        self.download_config_files(UDP)
        c_dir = self.c_vpn_config_dir + '/' + self.c_config_AES256TCP_folder_name
        if UDP:
            c_dir = self.c_vpn_config_dir + '/' + self.c_config_AES256UDP_folder_name
            pass

        file_list = os.popen('ls ' + c_dir + '/').read()

        options = file_list.splitlines()
        random_country = random.randint(0,len(options))
        random_vpn = options[random_country]
        file_ = c_dir + '/' + random_vpn
        userpassfile = self.c_userpass_dir + '/' + self.userpass_file_name
        print(userpassfile)
        startvpn_cm = 'openvpn --config ' + file_ + ' --script-security 2 --dhcp-option DNS 8.8.8.8 --up /etc/openvpn/update-resolv-conf --down /etc/openvpn/update-resolv-conf --auth-user-pass ' + userpassfile
        print(startvpn_cm)
        output = os.popen(startvpn_cm).read()
        print(output)

    def download_config_files(self, UDP = False):

        #variable for storing some log information
        logging_info = "\n----------\n\n"

        #create config dir if they dont exist already
        if os.path.isdir(self.c_logdir) == False:
            os.popen('mkdir ' + self.c_logdir).read()
            pass
        if os.path.isdir(self.c_vpn_config_dir) == False:
            os.popen('mkdir ' + self.c_vpn_config_dir).read()
            pass
        if os.path.isdir(self.c_userpass_dir) == False:
            os.popen('mkdir ' + self.c_userpass_dir).read()
            pass

        #full file path and file name to which we will save the vpn config zip file
        file_test = os.path.dirname(os.path.realpath(__file__)) + '/vpnacconfig.zip'


        #the name of the folder that the zip file for the specified protocol wil extract
        foldername = self.c_config_AES256TCP_folder_name

        # downoad the correct config zip file for the specified protocol
        if(UDP == True):
            foldername = self.c_config_AES256UDP_folder_name
            urllib.request.urlretrieve(self.configurl_files_url_AES_UDP, file_test)
            pass
        else:
            urllib.request.urlretrieve(self.configurl_files_url_AES_TCP, file_test)
            pass

        #install zip program in case not installed
        logging_info += os.popen('apt-get install zip').read()

        # install openvpn program in case not installed
        logging_info += os.popen('apt-get install openvpn').read()

        #unzip the openvpn config files to the config openvpn dir
        unzip_command = 'unzip -o ' + file_test + ' -d ' + self.c_vpn_config_dir + '/'
        logging_info += os.popen(unzip_command).read()

        #dir containing the vpn files for the specified protocol (UDP or TCP)
        config_file_dir = self.c_vpn_config_dir + '/' + foldername

        #remove the zip file after it has been unzipped to the config dir (zip file no longer needed)
        logging_info += os.popen('rm ' + file_test).read()


        #save user info required for vpn
        contents = self.vpnusern_ + "\n" + self.vpnpassw_
        filedir = self.c_userpass_dir + '/' + self.userpass_file_name
        print(filedir)
        self.saveTofile(contents,filedir)


        pass

    def saveTofile(self, file_contents, full_file_path):
        tempfile = open(full_file_path, 'w')
        tempfile.write(file_contents)
        tempfile.close()
        pass

#Example installation
#if __name__ == '__main__':
#    vpnac = installVpnAC('vpn63768491','Test_12345')
#    vpnac.startVpn()