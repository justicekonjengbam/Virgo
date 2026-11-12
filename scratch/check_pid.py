import subprocess
cmd = ['powershell', '-Command', 'Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -eq 15948 } | Select-Object ProcessId, Name, CommandLine | Format-List']
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(res.stdout)

