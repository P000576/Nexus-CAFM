OpenAPI Generator configs

- `typescript-config.json` — configuration for TypeScript (typescript-fetch) generator.
- `python-config.json` — configuration for Python generator.

Local generation helper:

```powershell
# from repo root
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\generate-sdk.ps1
```

CI: A GitHub Actions workflow `.github/workflows/generate-sdk.yml` runs the generation using the official openapi-generator-cli Docker image and uploads the generated SDKs as an artifact.
