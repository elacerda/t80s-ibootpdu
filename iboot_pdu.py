import requests
from getpass import getpass
from os.path import basename
from datetime import datetime

def print_level(msg, level=0, verbose=0):
    '''
    Print a message with a specified verbosity level.

    Parameters
    ----------
    msg : str
        The message to be printed.

    level : int, optional
        The verbosity level of the message. Defaults to 0.

    verbose : int, optional
        The overall verbosity level. Messages with verbosity levels less than or equal to
        this value will be printed. Defaults to 0.
    '''    
    import __main__ as main
    try:
        __script_name__ = basename(main.__file__)
    except AttributeError:
        __script_name__ = ''

    if verbose >= level:
        print(f'[{datetime.now().isoformat()}] - {__script_name__}: {msg}')

class iboot:
    _outlets = {
        'fanwest': 1,
        'faneast': 2,
        'filterwheel': 3,
    }

    def __init__(self, ip, outlets=None, action=None, token=None, verbose=0):
        self.ip = ip
        self.http_link = f'http://{ip}/services'
        if outlets is None:
            self.outlets = [x for x in self._outlets.values()]
        else:
            self.outlets = [self._outlets[x] for x in outlets]
        self.action = action
        self.token = token
        self.auth(verbose)

    def reqpost(self, link, json):
        data = None
        success = False
        req = requests.post(f'{self.http_link}/{link}/', json=json)
        if req.status_code == 200:
            data = req.json()
            success = data['success'].lower().capitalize() == 'True'
        else:
            print_level('Error retrieving data')
        return data, success

    def auth(self, verbose=0):
        if self.token is None:
            token = None
            credentials = {'username': 'admin', 'password': getpass()}
            data, success = self.reqpost('auth', credentials)
            if success:
                token = data['token']
                print_level(f'token: {token}', 1, verbose)
            else:
                if data:
                    print_level(f'{data['message']}')
                else:
                    print_level('Token not acquired...')
            self.token = token
    
    def get_status(self):
        data, success = self.reqpost('retrieve', json={'token': self.token, 'outlets': self.outlets})
        if success:
            _out = [int(x) for x in data['outlets'].keys()]
            for i, iout in enumerate(_out):
                _outname = list(self._outlets.keys())[iout - 1]
                print_level(f'{_outname}: {data['outlets'][str(iout)]}')
        else:
            print_level(f'{data['message']}')

    def control_outlets(self):
        control = {
            'token': self.token, 
            'control': 'outlet', 
            'command': self.action, 
            'outlets': self.outlets,
        }
        data, success = self.reqpost('control', json=control)
        msg = 'Done' if success else data['message']
        print_level(f'{msg}')