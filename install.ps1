# pokespin one-line installer (Windows PowerShell)
#   irm https://raw.githubusercontent.com/ShukiB/pokespin/main/install.ps1 | iex
# Pass args:  $env:POKESPIN_ARGS = "install --mode append"; irm ... | iex
$ErrorActionPreference = "Stop"

$repo = if ($env:POKESPIN_REPO) { $env:POKESPIN_REPO } else { "ShukiB/pokespin" }
$ref  = if ($env:POKESPIN_REF)  { $env:POKESPIN_REF }  else { "main" }
$url  = "https://raw.githubusercontent.com/$repo/$ref/dist/pokespin.py"

$py = $null
foreach ($c in @("python3", "python", "py")) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) { $py = $cmd.Source; break }
}
if (-not $py) { throw "pokespin: needs Python 3.8+ on PATH" }

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("pokespin-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    $file = Join-Path $tmp "pokespin.py"
    Invoke-WebRequest -Uri $url -OutFile $file -UseBasicParsing
    $pokeArgs = if ($env:POKESPIN_ARGS) { $env:POKESPIN_ARGS -split '\s+' } else { @("install") }
    & $py $file @pokeArgs
    if ($LASTEXITCODE -ne 0) { throw "pokespin exited with $LASTEXITCODE" }
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
