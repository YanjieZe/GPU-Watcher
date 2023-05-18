import os

import subprocess
from typing import List
import re
from termcolor import cprint, colored
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('server', type=str, default='none', help='server name')



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


def watch_gpus():
    # 服务器列表
    args = parser.parse_args()
    if args.server == 'none':
        # get args    
        servers = ["qizhi", "qizhi2", "qizhi3", "qizhi4",]
    else:
        servers =  args.server.split(",")
    for server in servers:
        cprint(f"========== {server} =========", "cyan")
        print(get_gpu_status(server))


if __name__ == "__main__":
    watch_gpus()
