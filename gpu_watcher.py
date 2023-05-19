import os

import subprocess
from typing import List
import re
from termcolor import cprint, colored
import argparse

parser = argparse.ArgumentParser()
# make it not required by default
parser.add_argument('server', type=str, default='all', help='server name', nargs='?')



# Use regular expressions to parse the output of nvidia-smi
def process_nvidia_smi_output(smi_output):
    # Split on newlines
    lines = smi_output.split("\n")
    # Remove any lines that don't contain '|', which are just blank lines
    lines = [line for line in lines if "|" in line]
    
    # remain the lines contain MB   
    lines = [line for line in lines if "MiB" in line and "%" in line]
    
    # clean the lines and only remain memory usage
    # | 61%   69C    P2   289W / 350W |  14036MiB / 24265MiB |     90%      Default | 
    # -> Memory: 14036MiB / 24265MiB | Usage: 90%
    lines_memory = [line.split("|")[2] for line in lines] 
    # convert MiB to GB
    lines_memory_used = [line.split("/")[0].strip() for line in lines_memory]
    lines_memory_used = [line.split("MiB")[0].strip() for line in lines_memory_used]
    lines_memory_used = [f"{int(line)/1024:.0f}GB" for line in lines_memory_used]
    
    lines_memory_total = [line.split("/")[1].strip() for line in lines_memory]
    lines_memory_total = [line.split("MiB")[0].strip() for line in lines_memory_total]
    lines_memory_total = [f"{int(line)/1024:.0f}GB" for line in lines_memory_total]
    
       
    line_util = [line.split("|")[3] for line in lines]
    # remove default
    line_util = [line.split("Default")[0] for line in line_util]
    
    # print them
    output = ""
    for i in range(len(lines_memory)):
        # add gpu id
        output += colored(f"GPU {i}", "red")
        output += colored(f" | Memory: {lines_memory_used[i]} / {lines_memory_total[i]}", "blue")
        output += colored(f" | Util: {line_util[i]}\n", "green")
        
        
    return output
    


def get_gpu_status(server: str) -> str:
    # 使用 ssh 和 nvidia-smi 获取 GPU 状态
    command = f"ssh {server} nvidia-smi"
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = process.communicate()

    # 检查是否有错误
    if process.returncode != 0:
        print(f"Error with server {server}: {error.decode()}")
        return ""
    else:
        return process_nvidia_smi_output(output.decode())
    
def get_cpu_status(server: str) -> str:
    # 获取cpu占用率
    command_cpu = "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'"
    command = f"ssh {server} {command_cpu}"
    
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = process.communicate()

    output = output.decode().strip()
    # 检查是否有错误
    if process.returncode != 0:
        print(f"Error with server {server}: {error.decode()}")
        return ""
    else:
        return colored(f"CPU Usage: {output}%", "green")

def get_memory_status(server: str) -> str:
    command_memory = "free | grep 'Mem:' "
    command = f"ssh {server} {command_memory}"
    
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    
    output, error = process.communicate()
    
    # Convert the byte string to a regular string
    output_str = output.decode("utf-8").strip()

    # Split the string into a list of values
    values = output_str.split()

    # Extract the used memory and total memory values
    used_memory = int(values[2])
    total_memory = int(values[1])
    
    # convert byte to GB
    used_memory = used_memory / 1024 / 1024
    total_memory = total_memory / 1024 / 1024
    
    
    # 检查是否有错误
    if process.returncode != 0:
        print(f"Error with server {server}: {error.decode()}")
        return ""
    else:
        return colored(f"Used Memory: {used_memory:.0f}GB / {total_memory:.0f}GB = {used_memory/total_memory*100:.0f}%", "blue")

def watch_gpus():
    # 服务器列表
    args = parser.parse_args()
    if args.server == 'all':
        # get args    
        servers = ["qizhi", "qizhi2", "qizhi3", "qizhi4",]
    else:
        servers =  args.server.split(",")
    for server in servers:
        cprint(f"========== {server} =========", "cyan")
        print(get_gpu_status(server))
        print(get_cpu_status(server))
        print(get_memory_status(server))
        print("\n")


if __name__ == "__main__":
    watch_gpus()
