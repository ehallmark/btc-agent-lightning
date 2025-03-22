from subprocess import Popen, PIPE, STDOUT
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

WALLET_PASSWORD_FILE = os.environ['WALLET_PASSWORD_FILE']
LND_EXECUTABLE = os.environ['LND_EXECUTABLE']
LND_DATA_DIR_PREFIX = os.environ['LND_DATA_DIR_PREFIX']
BTCD_EXECUTABLE = os.environ['BTCD_EXECUTABLE']
BTCCTL_EXECUTABLE = os.environ['BTCCTL_EXECUTABLE']
LNCLI_EXECUTABLE = os.environ['LNCLI_EXECUTABLE']


def mine_blocks(n: int):
    commands = [
        BTCCTL_EXECUTABLE,
        "--simnet",
        "--rpcuser=kek",
        "--rpcpass=kek",
        "generate",
        str(n),
    ]
    process = Popen(commands, stdout=PIPE, stderr=STDOUT)
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            print(f"btccli:: {output.decode('utf-8').strip()}")
    print('Finished mining blocks.')


def start_btcd():
    def run():
        commands = [
            BTCD_EXECUTABLE,
            "--txindex",
            "--simnet",
            "--rpcuser=kek",
            "--rpcpass=kek",
            "--miningaddr=rmfMh47Qp34w66FZacjRE66oBCkgYXLVV7"
        ]
        process = Popen(commands, stdout=PIPE, stderr=STDOUT)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"btcd:: {output.decode('utf-8').strip()}")
    thread = threading.Thread(target=run)
    thread.start()


def start_lnd(user: str, rpc_port: int, port: int, rest_port: int):
    def run():
        commands = [
            LND_EXECUTABLE,
            f"--rpclisten=localhost:{rpc_port}",
            f"--listen=localhost:{port}",
            f"--restlisten=localhost:{rest_port}",
            f"--datadir={LND_DATA_DIR_PREFIX}/{user}/data",
            f"--logdir={LND_DATA_DIR_PREFIX}/{user}/log",
            f"--wallet-unlock-password-file={WALLET_PASSWORD_FILE}",
            "--debuglevel=info",
            "--bitcoin.simnet",
            "--bitcoin.active",
            "--bitcoin.node=btcd",
            "--btcd.rpcuser=kek",
            "--btcd.rpcpass=kek",
            "--accept-amp",
        ]
        process = Popen(commands, stdout=PIPE, stderr=STDOUT)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"lnd-{user}:: {output.decode('utf-8').strip()}")
    thread = threading.Thread(target=run)
    thread.start()


def main():
    start_btcd()
    time.sleep(3)  # wait for btcd to start
    mine_blocks(10)
    start_lnd("alice", 10001, 10011, 8001)
    start_lnd("bob", 10002, 10012, 8002)
    start_lnd("charlie", 10003, 10013, 8003)


if __name__ == "__main__":
    main()