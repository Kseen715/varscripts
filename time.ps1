# powershell command to capture execution time of command
# Usage: .\time.ps1 {command}
#  use measure-commnad to capture execution time of command

$command = $args[0]
$arguments = $args[1..$args.Length]
$measure = Measure-Command {start-process "$command" -ArgumentList $arguments -Wait -NoNewWindow}

# print execution time in format {time}s
Write-Host
"Time: " + $measure.TotalSeconds.ToString() + "s"