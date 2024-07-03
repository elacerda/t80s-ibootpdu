import os
import sys
import argparse as ap
from os.path import basename

from iboot_pdu import iboot, print_level

__script_name__ = basename(sys.argv[0])

class readFileArgumentParser(ap.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(readFileArgumentParser, self).__init__(*args, **kwargs)

    def convert_arg_line_to_args(self, line):
        for arg in line.split():
            if not arg.strip():
                continue
            if arg[0] == '#':
                break
            yield arg

def parse_arguments(default_args_file=None):
    parser = readFileArgumentParser(fromfile_prefix_chars='@')

    parser.add_argument('--iboot_http', '-H', type=str, default=None, help='T80-South iBoot PDU http link.')
    parser.add_argument('--fanwest', '-W', action='store_true', default=False, help='Control FanWest outlet')
    parser.add_argument('--faneast', '-E', action='store_true', default=False, help='Control FanEast outlet')
    parser.add_argument('--filterwheel', '-F', action='store_true', default=False, help='Control FilterWheel outlet')
    parser.add_argument('--token', '-T', type=str, default=None, help='Access token: XXXX-XXXX-XXXX-XXXX')
    parser.add_argument('--on', action='store_true', default=False, help='Turn on requested outlet')
    parser.add_argument('--off', action='store_true', default=False, help='Turn off requested outlet')
    parser.add_argument('--cycle', action='store_true', default=False, help='Cycle requested outlet')
    parser.add_argument('--verbose', '-v', action='count', default=0)

    args_list = sys.argv[1:]
    args = parser.parse_args(args=args_list)

    # HTTP LINK
    if args.iboot_http is None:
        print_level('missing --iboot_http. Trying to read from enviroment...')
        env_http = os.environ.get('T80S_IBOOT_HTTP', None)
        if env_http is None:
            parser.error('missing T80S_IBOOT_HTTP enviroment variable...')
        else:
            print_level('Done', 1, args.verbose)
            args.iboot_http = env_http
    
    # ACTION
    err_msg = 'You must choose --on, --off or --cycle'
    if (args.on or args.off or args.cycle):
        if ((not args.on or (args.off or args.cycle)) 
            and (not args.off or (args.cycle or args.on)) 
            and (not args.cycle or (args.on or args.off))):
            parser.error(err_msg)

    # OUTLETS
    args.outlets = []
    if args.fanwest:
        args.outlets.append('fanwest')
    if args.faneast:
        args.outlets.append('faneast')
    if args.filterwheel:
        args.outlets.append('filterwheel')
    if len(args.outlets) == 0:
        args.outlets = None
    
    args.action = None
    if args.on:
        args.action = 'on'
    if args.off:
        args.action = 'off'
    if args.cycle:
        args.action = 'cycle'

    return args

if __name__ == '__main__':
    args = parse_arguments()

    control = iboot(
        http_link=args.iboot_http,
        outlets=args.outlets, 
        action=args.action, 
        token=args.token, 
        verbose=args.verbose,
    )
    if control.action is None:
        control.get_status()
    else:
        control.control_outlets()token