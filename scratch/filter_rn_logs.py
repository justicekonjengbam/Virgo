import subprocess

cmd = [
    r"C:\platform-tools\adb.exe",
    "-s", "R52X90A40LV",
    "logcat",
    "-d",
    "-v", "time",
    "--pid=17630"
]

res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
lines = res.stdout.splitlines()

for l in lines:
    if "ReactNativeJS" in l:
        print(l)
