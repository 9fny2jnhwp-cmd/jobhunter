# Link this repo to GitHub and push. Edit $RepoUrl before running.
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoUrl  # e.g. https://github.com/YOUR_USER/jobhunter-ai.git
)

$git = "C:\Program Files\Git\cmd\git.exe"
$root = Split-Path -Parent $PSScriptRoot

Set-Location $root

& $git remote remove origin 2>$null
& $git remote add origin $RepoUrl
& $git branch -M main
& $git push -u origin main

Write-Host "Pushed to $RepoUrl"
