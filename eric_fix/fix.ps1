$servers = Get-Content c:\techops\machines.txt

foreach ($machine in $servers) {
"-------------------" >> c:\techops\status.txt
Get-Date >> c:\techops\status.txt
$machine >> c:\techops\status.txt
Get-Service -ComputerName $machine -Name ThisAnnoysEric| Restart-Service -Force
Get-Service -ComputerName $machine -Name ThisAnnoysEric >> c:\techops\status.txt
"-------------------" >> c:\techops\status.txt
}

#ideally status.txt would reside in a network share somewhere