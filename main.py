from argparse import ONE_OR_MORE, ArgumentParser
from colorama import Fore


def run():
    print("How many times engineers does it take to change a light bulb?")
    n = int(input())
    print(f"{Fore.BLUE}{n}, really? {Fore.YELLOW}Ach, you are probably right")


run()
