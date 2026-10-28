# Private Credential Setup

Read this only when credentials are missing or inaccessible. Reuse a working configured key. The user enters the key privately; never request it in chat, read unrelated secrets, automate login, or inspect a browser. Do not enable shell tracing, verbose HTTP logging or print secret-store output. Never put the value in command arguments, shell profiles, repository files or request caches.

The user generates/copies their key at [API-key settings](https://beta.alphaengine.trade/#profile/api-key). Regeneration replaces the single active key immediately. Setup changes storage; it does not generate or rotate keys.

## Choose the Actual Runtime

Check whether `ALPHAENGINE_API_KEY` is present using a boolean only. A desktop agent, remote host, container or WSL process does not inherit exports from a separate terminal or the user's Windows/macOS secret store automatically. Run the loader below in the same process/invocation as the API client, or use the host's existing secure secret injection. Do not repeatedly send the user through setup when only process access is missing.

## macOS: Keychain Access

Use the login/default keychain's **generic password** storage. Apple Passwords is a different app and is not this CLI storage.

The user runs this in their own Terminal, with `-w` last and no password argument:

```zsh
security add-generic-password -U -a "$(id -un)" -s alphaengine-api-key -w
```

They paste the key at the hidden password prompt and press Enter. The key does not appear in the command or shell history. This updates that named local item if it already exists. Keep normal Keychain access prompts; do not use `-A` to grant all applications access.

The agent can load it in its request invocation without displaying it:

```bash
set +x
ALPHAENGINE_API_KEY="$(security find-generic-password -a "$(id -un)" -s alphaengine-api-key -w)" || exit 1
export ALPHAENGINE_API_KEY
if [ -n "$ALPHAENGINE_API_KEY" ]; then
  printf '%s\n' 'API key accessible: true'
else
  printf '%s\n' 'API key unavailable' >&2; exit 1
fi
# Run the API client here, in this same shell. Never run env/printenv on the key.
```

An inaccessible/locked item is a local access problem, not evidence that AlphaEngine rejected the key. Let the user unlock/authorize normal Keychain access themselves.

## Windows: PowerShell and User-Bound Encrypted Storage

On **Windows**, PowerShell can persist a credential outside the repository using Windows DPAPI. It can be decrypted only by the same Windows user on the same computer. This method is not secure credential encryption on macOS/Linux PowerShell and must not be used there. See [Microsoft's credential export/import documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/import-clixml).

The user runs this in their own Windows PowerShell terminal:

```powershell
$ErrorActionPreference = 'Stop'
$aeKeyDirectory = Join-Path $env:LOCALAPPDATA 'AlphaEngine'
$aeKeyPath = Join-Path $aeKeyDirectory 'api-key.clixml'
$null = New-Item -ItemType Directory -Force -Path $aeKeyDirectory
$aeSecureKey = Read-Host 'Paste your AlphaEngine API key' -AsSecureString
if ($aeSecureKey.Length -eq 0) { throw 'No API key entered' }
$aeCredential = [System.Management.Automation.PSCredential]::new('alphaengine', $aeSecureKey)
$aeCredential | Export-Clixml -LiteralPath $aeKeyPath
Remove-Variable aeSecureKey, aeCredential
```

Input is hidden using [`Read-Host -AsSecureString`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/read-host). Do not use `setx` or a user-wide plaintext environment variable for persistence.

The agent loads it in the PowerShell invocation that starts the API client:

```powershell
$ErrorActionPreference = 'Stop'
$aeKeyPath = Join-Path $env:LOCALAPPDATA 'AlphaEngine/api-key.clixml'
$aeCredential = Import-Clixml -LiteralPath $aeKeyPath
$env:ALPHAENGINE_API_KEY = $aeCredential.GetNetworkCredential().Password
Remove-Variable aeCredential
Write-Output ('API key accessible: ' + (-not [string]::IsNullOrWhiteSpace($env:ALPHAENGINE_API_KEY)))
# Run the API client here, in this same PowerShell process.
```

Use `curl.exe` for curl examples on Windows, not Windows PowerShell's `curl` alias. The Unix shell examples in API workflow require a Bash-compatible environment and do not configure PowerShell. If the agent actually runs in WSL or a remote/container host, use that runtime's secure injection instead; do not copy a plaintext key into its repository.

Native Windows PowerShell supplies `Invoke-RestMethod`, `ConvertFrom-Json` and `ConvertTo-Json`; Python is not a prerequisite. Use a header hashtable in memory, verified HTTPS and no cross-origin redirects. When serializing nested candidates/responses with `ConvertTo-Json`, set sufficient explicit `-Depth` to avoid truncating components or simulation data. Follow the runtime-neutral [candidate validation rules](candidate-validation.md).

## Access Preflight

1. Check only that the intended key source is accessible and nonempty. Reject embedded CR/LF before constructing a header. Capture secret-store output privately; log only success/failure.
2. Check the documented origin with HTTPS verification enabled, then make one authenticated catalog GET. This confirms authentication and read access. Compute scopes are enforced by their endpoints; a successful GET does not prove every scope.
3. Distinguish local sandbox/network restrictions, DNS, TLS trust-store failures, and HTTP responses. Use the host's permitted network path and verified system trust store where available. Never disable certificate checks or automatically change origins. Report unresolved connectivity separately from authentication.
4. Follow structured `401`/`403`/`429` handling in [API workflow](api-workflow.md#failures-and-bounded-retries). Do not rotate a valid key to address a transport, scope or rate-limit failure.

For HTTP requests, keep the key in process memory or pass the header to curl through stdin (`--header @-`), not a literal command argument or a temporary header file. Send it only to `https://api-router.alphaengine.trade`; do not follow redirects with credentials.
