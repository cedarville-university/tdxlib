import configparser
import tdxlib.tdx_constants
import getpass
import os


default_config = tdxlib.tdx_constants.default_config


class TDXConfig:
    def __init__(self, filename: str = None, config: dict = None):
        self.filename = filename
        self.config = configparser.ConfigParser()
        self.api_url = None
        self.token = None
        self.token_exp = None
        self.timezone = None
        self.log_level = None
        self.caching = True
        self.sandbox = True
        self.username = None
        self.password = None
        self.org_name = None
        self.auth_type = None
        self.ticket_app_id = None
        self.asset_app_id = None
        self.full_host = None
        self.load_config_from_env()
        if config:
            self.set_config_from_dict(config)
        self.load_config_from_file(filename)
        if not self.config_complete():
            self.run_setup_wizard()
        self.config_to_attributes()
        self.setup_from_attributes()

    def config_complete(self):
        if not self.get_value('org_name') and not self.get_value('orgname') and not self.get_value('full_host'):
            return False
        if self.get_value('authType') == 'password' and \
                (not self.get_value('username')):
            return False
        return True

    def set_config_from_dict(self, config: dict):
        if 'TDX API Settings' in config.keys():
            self.config['TDX API Settings'] = config['TDX API Settings']
        else:
            self.config['TDX API Settings'] = config

    def load_config_from_file(self, filename: str):
        # Read in configuration
        if filename is None:
            filename = tdxlib.tdx_constants.default_filename
        self.config.read(filename)
        return

    def load_config_from_env(self):
        self.config.add_section('TDX API Settings')
        tdx_vars = {k:v for k,v in os.environ.items() if 'TDXLIB' in k}
        for i in tdxlib.tdx_constants.config_keys.keys():
            environ_key = f'TDXLIB_{i.upper()}'
            if environ_key in tdx_vars.keys() and tdx_vars[environ_key]:
                self.config.set('TDX API Settings', i, tdx_vars[environ_key])

    def get_value(self, key: str, default=None):
        if key and 'TDX API Settings' in self.config.keys():
            if self.config['TDX API Settings'] and key in self.config['TDX API Settings'].keys():
                t = tdxlib.tdx_constants.config_keys[key]
                if t is str:
                    return self.config['TDX API Settings'].get(key)
                if t is bool:
                    return self.config['TDX API Settings'].getboolean(key)
                if t is int:
                    return self.config['TDX API Settings'].getint(key)
                if t is float:
                    return self.config['TDX API Settings'].getfloat(key)
            else:
                if key in default_config.keys():
                    return default_config[key]
        return default

    def config_to_attributes(self):
        # Read settings in, respecting backwards compatibility
        self.org_name = self.get_value('org_name')
        if not self.org_name:
            self.org_name = self.get_value('orgname')
        self.sandbox = self.get_value('sandbox', bool)
        self.auth_type = self.get_value('auth_type')
        if not self.auth_type:
            self.auth_type = self.get_value('authType')
        if not self.auth_type or self.auth_type == 'password':
            self.username = self.get_value('username')
            self.password = self.get_value('password')
        self.ticket_app_id = self.get_value('ticket_app_id')
        if not self.ticket_app_id:
            self.ticket_app_id = self.get_value('ticketAppId')
        if not self.ticket_app_id:
            self.ticket_app_id = self.get_value('ticketappid')
        self.asset_app_id = self.get_value('asset_app_id')
        if not self.asset_app_id:
            self.asset_app_id = self.get_value('assetAppId')
        if not self.asset_app_id:
            self.asset_app_id = self.get_value('assetappid')
        self.caching = self.get_value('caching', bool)
        self.timezone = self.get_value('timezone')
        self.full_host = self.get_value('full_host')

    def setup_from_attributes(self):
        if not self.timezone:
            self.timezone = 'Z'

        if self.sandbox:
            api_end = '/SBTDWebApi/api'
        else:
            api_end = '/TDWebApi/api'
        if self.full_host is None:
            self.api_url = 'https://' + self.org_name + '.teamdynamix.com' + api_end
        else:
            self.api_url = 'https://' + self.full_host + api_end

        if not self.auth_type or self.auth_type == 'password':
            if self.password == 'Prompt':
                pass_prompt = 'Enter the TDX Password for user ' + self.username + \
                              ' (this password will not be written to disk): '
                self.password = getpass.getpass(pass_prompt)

    def run_setup_wizard(self):
        # Initialization wizard
        print("\nIncomplete configuration. Please enter the following information: ")
        self.set_fqdn_wizard()
        self.set_sandbox_wizard()
        self.set_auth_type_wizard()
        self.set_ticket_app_id_wizard()
        self.set_asset_app_id_wizard()
        self.set_caching_wizard()
        self.set_timezone_wizard()
        self.set_logging_wizard()
        self.save_config_wizard()

    def set_fqdn_wizard(self):
        fqdn_invalid = True
        fqdn = False
        while fqdn_invalid:
            fqdn_choice = input("\nUse a Fully-Qualified DNS Name for your TDX Instance "
                                "(if not *.teamdynamix.com)? [Y/N]: ")
            if fqdn_choice.lower() in ['y', 'ye', 'yes', 'true']:
                fqdn = True
                fqdn_invalid = False
            elif fqdn_choice.lower() in ['n', 'no', 'false']:
                fqdn_invalid = False
        if fqdn:
            print("Enter the fully qualified DNS name of your TDX instance.")
            init_full_host = input("FQDN (its.myuniversity.edu): ")
            self.config.set('TDX API Settings', 'full_host', init_full_host)
        else:
            print("\n\nPlease enter your TeamDynamix organization name.")
            print("This is the teamdynamix.com subdomain that you use to access TeamDynamix.")
            init_org_name = input("Organization Name (<org_name>.teamdynamix.com): ")
            self.config.set('TDX API Settings', 'org_name', init_org_name)

    def set_sandbox_wizard(self):
        sandbox_invalid = True
        while sandbox_invalid:
            sandbox_choice = input("\nUse TeamDynamix Sandbox? [Y/N]: ")
            if sandbox_choice.lower() in ['y', 'ye', 'yes', 'true']:
                self.config.set('TDX API Settings', 'sandbox', 'true')
                sandbox_invalid = False
            elif sandbox_choice.lower() in ['n', 'no', 'false']:
                self.config.set('TDX API Settings', 'sandbox', 'false')
                sandbox_invalid = False

    def set_token_wizard(self):
        provided_token = input("\nInput token now, or leave blank to fill programmatically later: ")
        if provided_token != "":
            self.token = provided_token

    def set_password_wizard(self):
        init_username = input("\nTDX API Username (tdxuser@company.com): ")
        self.config.set('TDX API Settings', 'username', init_username)
        print("\nTDXLib can store the password for the API user in the configuration file.")
        print("This is convenient, but not very secure.")
        password_invalid = True
        while password_invalid:
            password_choice = input("Store password for " + init_username + "? [Y/N]: ")
            if password_choice.lower() in ['y', 'ye', 'yes', 'true']:
                password_prompt = '\nEnter Password for ' + init_username + ": "
                init_password = getpass.getpass(password_prompt)
                self.config.set('TDX API Settings', 'password', init_password)
                password_invalid = False
            elif password_choice.lower() in ['n', 'no', 'false']:
                self.config.set('TDX API Settings', 'password', 'Prompt')
                password_invalid = False
            if password_invalid:
                print("\nInvalid Response.")

    def set_auth_type_wizard(self):
        auth_type_invalid = True
        auth_type = "password"
        while auth_type_invalid:
            auth_type = input("\nAuthentication Type (Only password and token currently supported) [password]: ")
            if auth_type == '':
                auth_type = 'password'
            if auth_type == "password":
                self.set_password_wizard()
                auth_type_invalid = False
            elif auth_type == "token":
                self.set_token_wizard()
                auth_type_invalid = False
        self.config.set("TDX API Settings", "authType", auth_type)

    def set_asset_app_id_wizard(self):
        init_asset_id = input("\nAssets App ID (optional): ")
        self.config.set('TDX API Settings', 'asset_app_id', init_asset_id)

    def set_ticket_app_id_wizard(self):
        init_ticket_id = input("\nTickets App ID (optional): ")
        self.config.set('TDX API Settings', 'ticket_app_id', init_ticket_id)

    def set_caching_wizard(self):
        print("\nTDXLib uses intelligent caching to speed up API calls on repetitive operations.")
        print("In very dynamic environments, TDXLib's caching can cause issues.")
        caching_invalid = True
        while caching_invalid:
            caching_choice = input("Disable Caching? Y/N [N]: ")
            if caching_choice == '' or caching_choice.lower() in ['y', 'ye', 'yes', 'true']:
                self.config.set('TDX API Settings', 'caching', 'true')
                caching_invalid = False
            elif caching_choice.lower() in ['n', 'no', 'false']:
                self.config.set('TDX API Settings', 'caching', 'false')
                caching_invalid = False
            if caching_invalid:
                print("Invalid Response.")

    def set_timezone_wizard(self):
        print("\nWhat timezone would you like to set for this integration (default: '-0500')?")
        timezone_invalid = True
        while timezone_invalid:
            timezone_choice = input(f"Timezone (default: {default_config['timezone']} ) [+/-0000]: ")
            if len(timezone_choice) == 5 and timezone_choice[:1] in ["+", "-"] and timezone_choice[1:].isdigit():
                self.config.set('TDX API Settings', 'timezone', timezone_choice)
                timezone_invalid = False
            if len(timezone_choice) == 0:
                self.config.set('TDX API Settings', 'timezone', default_config['timezone'])
                timezone_invalid = False
            if timezone_invalid:
                print("Invalid Reponse.")

    def set_logging_wizard(self):
        logging_invalid = False
        while logging_invalid:
            logging_choice = input(f"Log Level (default: {default_config['logging_level']}) "
                                   f"[CRITICAL, ERROR, WARNING, INFO, DEBUG]: ")
            if logging_choice in ["WARNING", "ERROR", "INFO", "DEBUG", "CRITICAL"]:
                self.config.set('TDX API Settings', 'log_level', logging_choice)
                logging_invalid = False
            if len(logging_choice) == 0:
                self.config.set('TDX API Settings', 'log_level', default_config['log_level'])
                logging_invalid = False
            if logging_invalid:
                print("Invalid Reponse")

    def save_config_wizard(self):
        filename = input(f"Enter config filename (default: {default_config['filename']}): ")
        if filename == "":
            filename = default_config['filename']
        with open(filename, 'w') as configfile:
            self.config.write(configfile)
        print(f'\nSettings saved to {filename}')
        self.filename = filename
