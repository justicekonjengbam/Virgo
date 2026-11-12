import subprocess

adb = r"C:\platform-tools\adb.exe"
device = "R52X90A40LV"

def run_adb(args):
    cmd = [adb, "-s", device] + args
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    return res.stdout

print("=== PS -A ===")
ps_out = run_adb(["shell", "ps -A"])
for line in ps_out.splitlines():
    if "driverapp" in line or "passengerapp" in line:
        print(line)

print("\n=== RECENT LOGCAT (ReactNativeJS, Driver, Exception) ===")
log_out = run_adb(["logcat", "-d", "-v", "time", "-t", "500"])
for line in log_out.splitlines():
    if any(k in line for k in ["driverapp", "ReactNativeJS", "RideRequest", "offer", "Offer", "WebSocket", "17630", "Exception", "Fatal"]):
        print(line)

