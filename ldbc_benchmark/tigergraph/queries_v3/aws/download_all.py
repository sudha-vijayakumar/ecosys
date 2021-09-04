import argparse
import time
import subprocess
from scp import SCPClient
import paramiko
from pathlib import Path
import os

ips = []
nodes = len(ips)
user = "tigergraph"
pin = "tigergraph"
workdir = '/home/tigergraph'
def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

def main():
  for i,ip in enumerate(ips):
    ssh = createSSHClient(ip, 22, user, pin)
    scp = SCPClient(ssh.get_transport())
    print(f'logging to {ip}')
    scp.put('.aws/credential', workdir + '/.aws')
    scp.put('download_one_partition.py', workdir)
    scp.put('download_decompress.sh', workdir)
    
    stdin, stdout, stderr = ssh.exec_command(f''' 
      cd {workdir}
      export index={i}
      export nodes={nodes}
      nohup sh download_decompress.sh > log.download 2>&1 < /dev/null &  
    ''')
    time.sleep(4)
    stdin, stdout, stderr = ssh.exec_command(f'tail {workdir}/log.download')
    for line in stdout.read().splitlines():
      print(line.decode('utf-8'))
    
    ssh.close()
    scp.close()  

if __name__ == '__main__':
  main()