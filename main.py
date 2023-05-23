# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import assetvars_new
import tape
import strats
import os
import sys

config_file_path = os.path.join(os.path.dirname(__file__), 'config.csv')

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    CONFIG = assetvars_new.AssetVariables(config_file=config_file_path)
    TAPE_FILE = input("Enter tape file name: ")
    TAPE_TYPE = input("Enter tape type (raw, clean): ")
    TAPE = tape.Tape(tape_file=TAPE_FILE, tape_type=TAPE_TYPE, config_data=CONFIG)
    

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
