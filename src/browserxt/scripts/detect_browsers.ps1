$chromeRegistryPaths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'
)

$firefoxRegistryPaths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe'
)

$edgeRegistryPaths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe'
)

$braveRegistryPaths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\brave.exe',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\brave.exe'
)

$operaRegistryPaths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\opera.exe',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\opera.exe'
)

$chromePossiblePaths = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
)

$firefoxPossiblePaths = @(
    "$env:ProgramFiles\Mozilla Firefox\firefox.exe",
    "$env:ProgramFiles (x86)\Mozilla Firefox\firefox.exe",
    "$env:LocalAppData\Mozilla Firefox\firefox.exe"
)

$edgePossiblePaths = @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe",
    "$env:LocalAppData\Microsoft\Edge\Application\msedge.exe"
)

$bravePossiblePaths = @(
    "$env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$env:ProgramFiles (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$env:LocalAppData\BraveSoftware\Brave-Browser\Application\brave.exe"
)

$operaPossiblePaths = @(
    "$env:ProgramFiles\Opera\launcher.exe",
    "$env:ProgramFiles (x86)\Opera\launcher.exe",
    "$env:LocalAppData\Programs\Opera\launcher.exe"
)

function Find-BrowserPath {
    param (
        [string[]]$registryPaths,
        [string[]]$possiblePaths
    )

    $browserPaths = @()

    # Check registry paths
    foreach ($regPath in $registryPaths) {
        if (Test-Path $regPath) {
            try {
                $browserExe = Get-ItemProperty -Path $regPath -Name '(default)'
                if ($browserExe -ne $null) {
                    $browserPaths += $browserExe.'(default)'
                }
            } catch {
                # Handle cases where the path property does not exist
            }
        }
    }

    # Check possible installation paths
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $browserPaths += $path
        }
    }

    # Remove duplicates
    $browserPaths = $browserPaths | Select-Object -Unique

    return $browserPaths
}

function Get-DefaultBrowser {
    $defaultBrowserProgId = (Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice' -Name 'ProgId').ProgId

    switch ($defaultBrowserProgId) {
        'ChromeHTML' { return 'chrome' }
        'FirefoxURL' { return 'firefox' }
        'MSEdgeHTM'  { return 'edge' }
        'BraveHTML'  { return 'brave' }
        'OperaStable' { return 'opera' }
        default { return 'none' }
    }
}

$browsers = @{}
$defaultBrowser = Get-DefaultBrowser

# Find Chrome paths
$chromePaths = Find-BrowserPath -registryPaths $chromeRegistryPaths -possiblePaths $chromePossiblePaths
if ($chromePaths.Count -gt 0) {
    $browsers["chrome"] = $chromePaths
}

# Find Firefox paths
$firefoxPaths = Find-BrowserPath -registryPaths $firefoxRegistryPaths -possiblePaths $firefoxPossiblePaths
if ($firefoxPaths.Count -gt 0) {
    $browsers["firefox"] = $firefoxPaths
}

# Find Edge paths
$edgePaths = Find-BrowserPath -registryPaths $edgeRegistryPaths -possiblePaths $edgePossiblePaths
if ($edgePaths.Count -gt 0) {
    $browsers["edge"] = $edgePaths
}

# Find Brave paths
$bravePaths = Find-BrowserPath -registryPaths $braveRegistryPaths -possiblePaths $bravePossiblePaths
if ($bravePaths.Count -gt 0) {
    $browsers["brave"] = $bravePaths
}

# Find Opera paths
$operaPaths = Find-BrowserPath -registryPaths $operaRegistryPaths -possiblePaths $operaPossiblePaths
if ($operaPaths.Count -gt 0) {
    $browsers["opera"] = $operaPaths
}

# Add default browser to the output
$output = @{
    default = $defaultBrowser
    browsers = $browsers
}

# Output as JSON
$output | ConvertTo-Json -Compress