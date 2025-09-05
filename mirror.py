import sys
import subprocess
import shutil
from typing import Optional, Tuple


def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def run(cmd: list[str], timeout: int = 15) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
    return p.returncode, out.strip(), err.strip()


def ensure_adb_server(adb_path: str) -> None:
    run([adb_path, "start-server"], timeout=10)


def adb_pair(adb_path: str, ip: str, pair_port: int, code: str) -> Tuple[bool, str]:
    rc, out, err = run([adb_path, "pair", f"{ip}:{pair_port}", code], timeout=20)
    msg = out + ("\n" + err if err else "")
    ok = rc == 0 and "Successfully paired" in msg
    return ok, msg


def adb_connect(adb_path: str, ip: str, connect_port: int) -> Tuple[bool, str]:
    rc, out, err = run([adb_path, "connect", f"{ip}:{connect_port}"], timeout=15)
    msg = out + ("\n" + err if err else "")
    ok = rc == 0 and ("connected to" in msg or "already connected to" in msg)
    return ok, msg


def main():
    adb_path = which("adb")
    if not adb_path:
        print("[!] adb not found. Install Android platform-tools and ensure it is on PATH.")
        sys.exit(1)

    print("=== Android Wireless Debugging Tool ===")
    ip = input("Device IP: ").strip()
    pair_port = int(input("Pairing port (shown on phone): ").strip())
    code = input("6-digit pairing code: ").strip()
    connect_port = int(input("Connect port (shown on phone): ").strip())

    ensure_adb_server(adb_path)

    print(f"[*] Pairing with {ip}:{pair_port} …")
    ok1, msg1 = adb_pair(adb_path, ip, pair_port, code)
    print(msg1)
    #if not ok1:
        #print("[!] Pairing failed.")
        #sys.exit(1)

    print(f"[*] Connecting to {ip}:{connect_port} …")
    ok2, msg2 = adb_connect(adb_path, ip, connect_port)
    print(msg2)
    if not ok2:
        print("[!] Connect failed.")
        sys.exit(1)

    print("[+] Success! Device is paired and connected via ADB.")


if __name__ == "__main__":
    main()
