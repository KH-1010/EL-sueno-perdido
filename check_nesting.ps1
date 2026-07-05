$lines = [System.IO.File]::ReadAllLines('C:\Users\KH\Downloads\files\index.html', [System.Text.Encoding]::UTF8)
$depth = 0
for ($i = 7162; $i -lt 9020; $i++) {
    $line = $lines[$i]
    $opens = ([regex]::Matches($line, '<div[\s>]')).Count
    $closes = ([regex]::Matches($line, '</div>')).Count
    $depth += $opens - $closes
    if ($opens -gt 0 -or $closes -gt 0) {
        Write-Output "$($i+1): depth=$depth o=$opens c=$closes"
    }
}
