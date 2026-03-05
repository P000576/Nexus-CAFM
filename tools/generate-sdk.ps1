<#
PowerShell helper to generate SDKs from the OpenAPI spec.
Uses npx @openapitools/openapi-generator-cli (requires Node.js and npm to be installed).
#>
$spec = Join-Path (Get-Location) "openapi\project-nexus-core.yaml"
$tsOut = Join-Path (Get-Location) "sdk\generated\typescript"
$pyOut = Join-Path (Get-Location) "sdk\generated\python"
$tsConfig = Join-Path (Get-Location) "openapi\generator\typescript-config.json"
$pyConfig = Join-Path (Get-Location) "openapi\generator\python-config.json"

function Run-GeneratorWithNpx([string]$generator, [string]$out, [string]$config){
    Write-Host "Generating with npx for generator: $generator"
    $cmd = "npx @openapitools/openapi-generator-cli generate -i `"$spec`" -g $generator -o `"$out`" -c `"$config`" --skip-validate-spec"
    Write-Host $cmd
    $rv = cmd /c $cmd
    return $LASTEXITCODE
}

# Try TypeScript (typescript-fetch)
Write-Host "Generating TypeScript SDK..."
$rc = Run-GeneratorWithNpx 'typescript-fetch' 'sdk/generated/typescript' 'openapi/generator/typescript-config.json'
if ($rc -ne 0) { Write-Host "TypeScript generation failed (rc=$rc)"; exit $rc }

# Try Python
Write-Host "Generating Python SDK..."
$rc = Run-GeneratorWithNpx 'python' 'sdk/generated/python' 'openapi/generator/python-config.json'
if ($rc -ne 0) { Write-Host "Python generation failed (rc=$rc)"; exit $rc }

Write-Host "✓ SDK generation completed successfully. Check sdk/generated for outputs."; exit 0
