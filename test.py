import re
import subprocess
import platform
import psutil
import socket
import wmi
import distro
import json


def get_disk_info():
    disk_info = {}
    partitions = psutil.disk_partitions(all=True)
    for partition in partitions:
        partition_info = psutil.disk_usage(partition.mountpoint)
        disk_info[f"{partition.device} ({partition.mountpoint})"] = {
            'Total Space (GB)': round(partition_info.total / (1024 ** 3), 2),
            'Used Space (GB)': round(partition_info.used / (1024 ** 3), 2),
            'Free Space (GB)': round(partition_info.free / (1024 ** 3), 2),
            'Usage (%)': partition_info.percent
        }
    return disk_info

def get_network_interfaces():
    network_info = {}
    interfaces = psutil.net_if_addrs()
    for interface, addresses in interfaces.items():
        for address in addresses:
            if address.family == socket.AF_INET:
                network_info[interface] = address.address
                break
    return network_info

def get_system_updates():
    update_info = {}
    try:
        update_session = win32com.client.Dispatch('Microsoft.Update.Session')
        update_searcher = update_session.CreateUpdateSearcher()

        search_result_installed = update_searcher.Search("IsInstalled=1 and Type='Software'")
        update_info['Installed Updates'] = search_result_installed.Updates.Count

        search_result_available = update_searcher.Search("IsInstalled=0 and Type='Software'")
        update_info['Available Updates'] = search_result_available.Updates.Count

    except Exception as e:
        print(f"Error retrieving system update details: {e}")
    return update_info

# def get_installed_software():
#     software_info = []
#     try:
#         software_list = win32com.client.Dispatch("WbemScripting.SWbemLocator")
#         wmi_service = software_list.ConnectServer(".", "root\cimv2")
#         wmi_query = "SELECT * FROM Win32_Product"
#         software_items = wmi_service.ExecQuery(wmi_query)
#
#         for item in software_items:
#             software_info.append(item.Caption)
#     except Exception as e:
#         print(f"Error retrieving installed software list: {e}")
#     return software_info


def get_installed_software():
    software_info = []
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        reg_view = winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, reg_view) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    try:
                        display_name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                        software_info.append(display_name)
                    except FileNotFoundError:
                        pass
    except Exception as e:
        print(f"Error retrieving installed software list: {e}")
    return software_info

# Call the function to get installed software
# installed_software = get_installed_software()
# for software in installed_software:
#     print(software)

def get_system_info():
    system_info = {
    "System" : platform.system(),
    "Node Name" : platform.node(),
    "Release": platform.release(),
    "Version": platform.version(),
    "Machine": platform.machine(),
    "Processor": platform.processor(),
    "Architecture": platform.architecture()[0],

    "Total RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
    "Available RAM (GB)": round(psutil.virtual_memory().available / (1024 ** 3), 2),
    "Used RAM (GB)": round(psutil.virtual_memory().used / (1024 ** 3), 2),
    "CPU Cores": psutil.cpu_count(logical=False),
    "Total CPU Threads": psutil.cpu_count(logical=True),
    "CPU Usage (%)": psutil.cpu_percent(),
    "Boot Time": psutil.boot_time(),

    "Disk Information": {},
    "Network Interfaces": {},

    "System Updates": {
            "Installed Updates": get_system_updates()['Installed Updates'],
            "Available Updates": get_system_updates()['Available Updates']
        },

    "Installed Software Count": len(get_installed_software()),
    "Installed Software": get_installed_software(),
    "Model": platform.machine(),
    "Manufacturer": platform.system(),
    "Number of Processors": psutil.cpu_count(logical=True),
    "System Type": platform.system(),
    "System Family": platform.system()
    }
    for disk in psutil.disk_partitions():
        usage = psutil.disk_usage(disk.mountpoint)
        system_info["Disk Information"][disk.device] = {
            "Total Space (GB)": round(usage.total / (1024 ** 3), 2),
            "Used Space (GB)": round(usage.used / (1024 ** 3), 2),
            "Free Space (GB)": round(usage.free / (1024 ** 3), 2),
            "Usage (%)": usage.percent
        }

        # Fetch network interfaces
    for iface, addresses in psutil.net_if_addrs().items():
        system_info["Network Interfaces"][iface] = addresses[0].address

        # Convert the dictionary to JSON format
    json_data = json.dumps(system_info, indent=4)
    return json_data


def list_installed_packages(linux_distro):
    package_managers = {
        "apt": "dpkg -l",
        "dnf": "dnf list installed",
        "pacman": "pacman -Q",
        "yum": "yum list installed",
        "flatpak": "flatpak list",
        "snap": "snap list",
        # Add other package managers and their commands here
    }
    linux_file = 'scan_report.txt'
    for manager, command in package_managers.items():
        print(f"---- {manager.upper()} Packages ----")
        try:
            output = subprocess.check_output(command, shell=True, text=True)
            print(output)
            with open(linux_file,'w') as file:
                file.write(output)
        except subprocess.CalledProcessError as e:
            continue
        print()

#def file_to_json(input_file,output_file):


os = platform.system()
if os=="Windows":
    import win32com.client
    import winreg
    system_info_json = get_system_info()
    print(system_info_json)
    installed_software = get_installed_software()

    inst_soft = "Installed Software.txt"
    with open(inst_soft,"w") as f:
        for i in installed_software:
            f.write(i+"\n")

    output_file = "system_info.txt"
    with open(output_file, "w") as file:
        file.write(system_info_json)

else:
    linux_distro = distro.id().lower()
    if linux_distro in ["debian", "ubuntu" , "kali"]:
        list_installed_packages(linux_distro)
    elif linux_distro in ["fedora", "centos", "rhel"]:
        list_installed_packages(linux_distro)
    elif linux_distro == "arch":
        list_installed_packages(linux_distro)
        # Add more distribution checks and corresponding package managers if needed
    else:
        print(f"Unsupported Linux distribution: {linux_distro}")



tool_cmd = [

    ["nmap -p1433 --open -Pn ", ""],
    ["nmap -p3306 --open -Pn ", ""],
    ["nmap -p1521 --open -Pn ", ""],
    ["nmap -p3389 --open -sU -Pn ", ""],
    ["nmap -p3389 --open -sT -Pn ", ""],
    ["nmap -p1-65535 --open -Pn ", ""],
    ["nmap -p1-65535 -sU --open -Pn ", ""],
    ["nmap -p161 -sU --open -Pn ", ""],
    ["nmap -p445,137-139 --open -Pn ", ""],
    ["nmap -p137,138 --open -Pn ", ""],
    ["nmap -p80 --script=http-iis-webdav-vuln -Pn ", ""],
    ["nmap -F --open -Pn ", ""],
    ["nmap -p80 --script http-security-headers -Pn ", ""],
    ["nmap -p80,443 --script http-slowloris --max-parallelism 500 -Pn ", ""],
    ["nmap -p443 --script ssl-heartbleed -Pn ", ""],
    ["nmap -p443 --script ssl-poodle -Pn ", ""],
    ["nmap -p443 --script ssl-ccs-injection -Pn ", ""],
    ["nmap -p443 --script ssl-enum-ciphers -Pn ", ""],
    ["nmap -p443 --script ssl-dh-params -Pn ", ""],
    ["nmap -p23 --open -Pn ", ""],
    ["nmap -p21 --open -Pn ", ""],
    ["nmap --script stuxnet-detect -p445 -Pn ", ""],

    ["sslyze --certinfo=basic ", ""],
    ["sslyze --heartbleed ", ""],
    ["sslyze --compression ", ""],
    ["sslyze --reneg ", ""],
    ["sslyze --resum ", ""],

    ["golismero -e dns_malware scan ", ""],
    ["golismero -e heartbleed scan ", ""],
    ["golismero -e brute_url_predictables scan ", ""],
    ["golismero -e brute_directories scan ", ""],
    ["golismero -e sqlmap scan ", ""],
    ["golismero -e sslscan scan ", ""],
    ["golismero -e zone_transfer scan ", ""],
    ["golismero -e nikto scan ", ""],
    ["golismero -e brute_dns scan ", ""],
    ["golismero -e fingerprint_web scan ", ""],

    ["uniscan -w -u ", ""],
    ["uniscan -q -u ", ""],
    ["uniscan -r -u ", ""],
    ["uniscan -s -u ", ""],
    ["uniscan -d -u ", ""],
    ["uniscan -e -u ", ""],

    ["nikto -Plugins 'apache_expect_xss' -host ", ""],
    ["nikto -Plugins 'subdomain' -host ", ""],
    ["nikto -Plugins 'shellshock' -host ", ""],
    ["nikto -Plugins 'cookies' -host ", ""],
    ["nikto -Plugins 'put_del_test' -host ", ""],
    ["nikto -Plugins 'cgi' -host ", ""],
    ["nikto -Plugins 'ssl' -host ", ""],
    ["nikto -Plugins 'sitefiles' -host ", ""],
    ["nikto -Plugins 'paths' -host ", ""],
]

class Tools:
    def __init__(self,target):
        self.target = target
    def nmap(self,target):
        print("NMAP")
        # Execute Nmap commands against the target IP address and capture the output
        for nmap_cmd in nmap:
            cmd = nmap_cmd + target
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
            print("Scan Result:")
            print(result.stdout)
            output_file = "nmap_report.txt"

            with open(output_file, "w") as file:
                for command in tool_cmd:
                    cmd = nmap_cmd + target
                    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
                    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, error = process.communicate()

                    if output:
                        file.write(f"=== Command: {cmd} ===\n")
                        file.write(output.decode())
                        file.write("\n")
                    if error:
                        file.write(f"=== Error for Command: {cmd} ===\n")
                        file.write(error.decode())
                        file.write("\n")

            print("Nmap commands executed and report generated successfully.")

    def uniscan(self,target):
        print("UNISCAN")
        # Execute Nmap commands against the target IP address and capture the output
        for uniscan_cmd in uniscan:
            cmd = uniscan_cmd + target
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
            print("Scan Result:")
            print(result.stdout)
            print()

    def sslyze(self,target):
        print("SSLYZE")
        # Execute Nmap commands against the target IP address and capture the output
        for sslyze_cmd in sslyze:
            cmd = sslyze_cmd + target
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
            print("Scan Result:")
            print(result.stdout)
            print()

    def nikto(self,target):
        print("NIKTO")
        # Execute Nmap commands against the target IP address and capture the output
        for nikto_cmd in nikto:
            cmd = nikto_cmd + target
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
            print("Scan Result:")
            print(result.stdout)

    def golismero(self,target):
        print("GOLISMERO")
        # Execute Nmap commands against the target IP address and capture the output
        for golismero_cmd in golismero:
            cmd = golismero_cmd + target
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
            print("Scan Result:")
            print(result.stdout)
            print()


target = socket.gethostbyname(socket.gethostname())

nmap = []
uniscan = []
sslyze = []
nikto = []
golismero = []

# Extract Nmap commands from tool_cmd list
for cmd_pair in tool_cmd:
    for cmd_element in cmd_pair:
        element = str(cmd_element)
        # Use the modified regular expression pattern to find "nmap" as a standalone word or merged with other words.
        t1 = re.search(r'\bnmap\b', element, re.IGNORECASE)
        t2 = re.search(r'\buniscan\b', element, re.IGNORECASE)
        t3 = re.search(r'\bsslyze\b', element, re.IGNORECASE)
        t4 = re.search(r'\bnikto\b', element, re.IGNORECASE)
        t5 = re.search(r'\bgolismero\b', element, re.IGNORECASE)
        if t1 and element not in nmap:
            nmap.append(element)
        if t2 and element not in uniscan:
            uniscan.append(element)
        if t3 and element not in sslyze:
            sslyze.append(element)
        if t4 and element not in nikto:
            nikto.append(element)
        if t5 and element not in golismero:
            golismero.append(element)

tool = Tools(target)
tool.nmap(target)
tool.uniscan(target)
tool.sslyze(target)
tool.nikto(target)
tool.golismero(target)