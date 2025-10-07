<#
PowerShell helper to generate SDKs from the OpenAPI spec.
Tries npx @openapitools/openapi-generator-cli first, then falls back to Docker if npx isn't available.
#>
$spec = Join-Path (Get-Location) "openapi\project-nexus-core.yaml"
$tsOut = Join-Path (Get-Location) "sdk\generated\typescript"
$pyOut = Join-Path (Get-Location) "sdk\generated\python"
$tsConfig = Join-Path (Get-Location) "openapi\generator\typescript-config.json"
$pyConfig = Join-Path (Get-Location) "openapi\generator\python-config.json"

function Run-GeneratorWithNpx([string]$generator, [string]$out, [string]$config){
    Write-Host "Attempting generation with npx for generator: $generator"
    $cmd = "npx @openapitools/openapi-generator-cli generate -i `"$spec`" -g $generator -o `"$out`" -c `"$config`" --skip-validate-spec"
    Write-Host $cmd
    $rv = cmd /c $cmd
    return $LASTEXITCODE
}

function Run-GeneratorWithDocker([string]$generator, [string]$out, [string]$config){
    Write-Host "Attempting generation with Docker for generator: $generator"
    # Convert Windows path to a Docker-friendly path and escape quotes
    $pwdUnix = (Get-Location).Path -replace "\\","/"
    $outPath = $out -replace "\\","/"
    $configPath = $config -replace "\\","/"
    $cmd = "docker run --rm -v `"$pwdUnix`:/local`" openapitools/openapi-generator-cli generate -i /local/openapi/project-nexus-core.yaml -g $generator -o /local/$outPath -c /local/$configPath --skip-validate-spec"
    Write-Host $cmd
    $rv = cmd /c $cmd
    return $LASTEXITCODE
}

# Try TypeScript (typescript-fetch)
$rc = Run-GeneratorWithNpx 'typescript-fetch' 'sdk/generated/typescript' 'openapi/generator/typescript-config.json'
if ($rc -ne 0) {
    Write-Host "npx generation failed or not available (rc=$rc), trying Docker..."
    $rc2 = Run-GeneratorWithDocker 'typescript-fetch' 'sdk/generated/typescript' 'openapi/generator/typescript-config.json'
    if ($rc2 -ne 0) { Write-Host "Docker generation failed (rc=$rc2)"; exit $rc2 }
}

# Try Python
$rc = Run-GeneratorWithNpx 'python' 'sdk/generated/python' 'openapi/generator/python-config.json'
if ($rc -ne 0) {
    Write-Host "npx generation failed or not available (rc=$rc), trying Docker..."
    $rc2 = Run-GeneratorWithDocker 'python' 'sdk/generated/python' 'openapi/generator/python-config.json'
    if ($rc2 -ne 0) { Write-Host "Docker generation failed (rc=$rc2)"; exit $rc2 }
}

Write-Host "Generation script completed. Check sdk/generated for outputs."; exit 0
