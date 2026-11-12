import subprocess

cmd = ['powershell', '-Command', 'Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*8000*" } | Select-Object ProcessId, CommandLine | Format-List']
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(res.stdout)

