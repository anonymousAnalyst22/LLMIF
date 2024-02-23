import logging
logging.basicConfig(
    format='[%(name)s] %(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/fuzzing.log',
    level=logging.INFO,
    filemode='w')
import sys
import random
random.seed(40)
import argparse
sys.path.insert(0, 'lib')

from zbee_controller import ZbeeController
from cmd_identifier import CmdIdentifier
from spec_fuzzer import SpecFuzzer
from lib.controller_constants import STACK_ADDR

parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help'
)
parser.add_argument('--reset_addr')
args = parser.parse_args()

# Initiate network commissioning and let target device join the network.
zbeeController = ZbeeController(port=STACK_ADDR, baud_rate=115200)
if args.reset_addr is not None:
    addr = int(args.reset_addr, 16)
    zbeeController.reset_device(addr, False)
    exit()
if zbeeController.device_scan() != 0x0:
    print("Did not discover any potential target device!")
    exit(0)

zbeeController.configure_poll()
## Build the command list for the target device.
cmdIdentifier = CmdIdentifier()
cmdIdentifier.cmd_scanning(zbeeController)
## Load the repo and reverse enigneer the identified cluster.
cmdIdentifier.load_repo(zbeeController.target_device.hash_sig)
# Exclude (1) configure reports, (2) write attributes no response commands, (3) Discover Command Received Response, (4) Default Response
# The above commands may introduce errors for response monitoring
cmdIdentifier.reverse_engineering(zbeeController)

"""Code for using spec fuzzer"""
spec_fuzzer = SpecFuzzer(zbeeController)
spec_fuzzer.fuzzing_with_feedback()
