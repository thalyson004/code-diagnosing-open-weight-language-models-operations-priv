param([switch]$Full, [switch]$Execute, [string]$OutputDir = (Join-Path $PSScriptRoot 'results-study'))
$studyModels = @('gpt-oss:20b','deepseek-r1:14b','qwen3:14b','qwen3.5:9b','qwen3:8b','ibm/granite4.2:8b')
& (Join-Path $PSScriptRoot 'run.ps1') -Models $studyModels -Provider ollama -Full:$Full -Execute:$Execute -OutputDir $OutputDir
