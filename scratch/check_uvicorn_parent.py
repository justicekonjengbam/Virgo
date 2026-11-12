import subprocess

cmd = ['powershell', '-Command', 'Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(65220, 31812) } | Select-Object ProcessId, ParentProcessId, CommandLine | Format-List']
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(res.stdout)

cmd2 = ['powershell', '-Command', 'Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(31812, 65220) } | ForEach-Object { Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -eq $_.ParentProcessId } } | Select-Object ProcessId, CommandLine | Format-List']
res2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("Parents:")
print(res2.stdout)

