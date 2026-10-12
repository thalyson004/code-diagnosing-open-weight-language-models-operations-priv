param([Parameter(Mandatory=$true)][string[]]$Models, [switch]$Full, [switch]$Execute,
      [string]$OutputDir = (Join-Path $PSScriptRoot 'results-api'))
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$apiRegistryPath = Join-Path $OutputDir 'provider-models.json'
$apiRegistry = @{ models = @($Models | ForEach-Object {
    @{ id=$_; provider='openrouter'; size_b=$null; family='api'; specialization='external' }
}) } | ConvertTo-Json -Depth 5
if (Test-Path -LiteralPath $apiRegistryPath) {
    if ((Get-Content -LiteralPath $apiRegistryPath -Raw).Trim() -ne $apiRegistry.Trim()) {
        throw 'The API model selection changed. Choose a separate output directory.'
    }
} else {
    [IO.File]::WriteAllText($apiRegistryPath, $apiRegistry, [Text.UTF8Encoding]::new($false))
}
& (Join-Path $PSScriptRoot 'run.ps1') -Models $Models -ModelConfig $apiRegistryPath -Provider openrouter -Full:$Full -Execute:$Execute -OutputDir $OutputDir
