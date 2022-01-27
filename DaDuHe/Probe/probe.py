import psutil
import platform
import subprocess


ping_host = '192.168.0.114'
process_name = '企业微信'


if __name__ == '__main__':
    while True:
        # 系统的内存利用率
        mem = psutil.virtual_memory().percent

        # 系统的CPU利用率
        cpu = psutil.cpu_percent(interval=1)

        disk_infos = []
        # 系统的磁盘使用情况
        for disk in psutil.disk_partitions():
            disk_name = disk.device.split(':')[0]
            disk_info = psutil.disk_usage(disk.device)
            disk_infos.append({
                'name': disk_name,
                'percent': str(disk_info.percent),
                'freeSize': disk_info.free // 1024 // 1024 // 1024
            })

        # ping
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ping_host]
        reachable = subprocess.call(command) == 0

        for pid in psutil.pids():
            p = psutil.Process(pid)
            if p.name() == process_name:
                process = p
        print(process.pid)
