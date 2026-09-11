$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$config=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'execution-config.json')|ConvertFrom-Json
$removal=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'removal-result.json')|ConvertFrom-Json
if($removal.status -ne 'phases1-2-removal-complete-postcheck-pending' -or $removal.errors.Count -ne 0){throw 'Removal not complete'}
$utf8=New-Object System.Text.UTF8Encoding($false);$sha=[Security.Cryptography.SHA256]::Create()
function HashFile([string]$path){$stream=[IO.File]::OpenRead($path);try{return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','').ToLowerInvariant()}finally{$stream.Dispose()}}
function Emit($value){$value|ConvertTo-Json -Depth 8 -Compress|Write-Output}
$state=[ordered]@{status='postcheck-running';started_utc=[DateTime]::UtcNow.ToString('o');reader_files_checked=0;reader_bytes_checked=[long]0;capture_files_checked=0;review_bindings_checked=0;retained_manifests_checked=0;missing_removed_paths=0;errors=@()}
function SaveState{[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'postcheck.json'),($state|ConvertTo-Json -Depth 10),$utf8)}
SaveState
try{
 $archive=$config.archives|Where-Object {$_.version -eq 'Nightglass-NineChapters-v1'}
 $manifestPath=Join-Path $config.protected_reader 'PACKAGE-MANIFEST.json'
 if((HashFile $manifestPath) -ne $archive.manifest_sha256){throw 'Current reader manifest changed'}
 $manifest=Get-Content -Raw -LiteralPath $manifestPath|ConvertFrom-Json
 $expected=@{'PACKAGE-MANIFEST.json'=$true}
 foreach($record in $manifest.files){
  $p=Join-Path $config.protected_reader $record.path
  if(!(Test-Path -LiteralPath $p -PathType Leaf)){throw ('Current reader file missing: '+$record.path)}
  $info=Get-Item -LiteralPath $p
  if($info.Length -ne $record.bytes -or (HashFile $p) -ne $record.sha256){throw ('Current reader bytes changed: '+$record.path)}
  $expected[$record.path.Replace('\','/')]=$true;$state.reader_files_checked++;$state.reader_bytes_checked+=$info.Length
  if($state.reader_files_checked % 4000 -eq 0){Emit @{event='current-reader-files-verified';files=$state.reader_files_checked}}
 }
 $stack=New-Object 'System.Collections.Generic.Stack[IO.DirectoryInfo]';$stack.Push((Get-Item -LiteralPath $config.protected_reader));$count=0
 while($stack.Count -gt 0){foreach($item in $stack.Pop().GetFileSystemInfos()){
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'Reader reparse point'}
  if(($item.Attributes -band [IO.FileAttributes]::Directory) -ne 0){$stack.Push($item);continue}
  $rel=$item.FullName.Substring($config.protected_reader.Length+1).Replace('\','/');if(!$expected.ContainsKey($rel)){throw ('Unexpected reader file: '+$rel)};$count++
 }}
 if($count -ne $expected.Count){throw 'Reader inventory mismatch'}
 $state.reader_files_including_manifest=$count;$state.reader_manifest_sha256=$archive.manifest_sha256
 $indexPath=Join-Path $config.base 'research\nightglass-longform\assets\package\NINECHAPTER-ACTUAL-CAPTURE-INDEX.json'
 $index=Get-Content -Raw -LiteralPath $indexPath|ConvertFrom-Json
 foreach($record in $index.captures){if((HashFile (Join-Path $config.base $record.path)) -ne $record.sha256){throw 'Retained review screenshot changed'};$state.capture_files_checked++}
 foreach($record in $index.review_bindings){if((HashFile (Join-Path $config.base $record.path)) -ne $record.sha256){throw 'Retained actual review record changed'};$state.review_bindings_checked++}
 $verPath=Join-Path $config.base 'production\nightglass-longform\package\output\Nightglass-NineChapters-v1-verification\verification.json'
 if((HashFile $verPath) -ne $index.verification_receipt_sha256){throw 'Original verification receipt changed'}
 $state.original_verification_receipt_sha256=$index.verification_receipt_sha256
 foreach($a in $config.archives){if((HashFile $a.manifest_path) -ne $a.manifest_sha256){throw 'Retained manifest changed'};if(!(Test-Path -LiteralPath $a.path -PathType Leaf)){throw 'Milestone ZIP missing before phase3'};$state.retained_manifests_checked++}
 foreach($a in $removal.actions){if(Test-Path -LiteralPath $a.removed_path){throw ('Removed path remains: '+$a.removed_path)};$state.missing_removed_paths++}
 if($state.capture_files_checked -ne 67 -or $state.reader_files_checked -ne 8953 -or $state.missing_removed_paths -ne 20){throw 'Unexpected final counts'}
 $snapshot=Get-Content -Raw -LiteralPath (Join-Path $config.protected_reader 'production\nightglass-longform\reader\snapshot.json')|ConvertFrom-Json
 $state.chapters=$snapshot.chapters.Count;$state.nightglass_panels=($snapshot.chapters|Measure-Object -Property available -Sum).Sum
 if($state.chapters -ne 9 -or $state.nightglass_panels -ne 393){throw 'Reader chapter counts changed'}
 $state.reader_entry=Join-Path $config.protected_reader 'START-HERE.html'
 $state.status='PASS-current-reader-exact-bytes-and-review-evidence-preserved';$state.ended_utc=[DateTime]::UtcNow.ToString('o');$state.free_C_after=[IO.DriveInfo]::new('C').AvailableFreeSpace
 $state.scope='Exact manifest/inventory check of retained current reader and hash check of67 existing screenshots/3 review records. Prior23-route browser evidence reused; no new browser or editorial reread.'
 SaveState;Emit $state
}catch{$state.status='postcheck-error';$state.errors+=($_|Out-String);SaveState;Emit @{event='postcheck-error';error=($_|Out-String)};exit 1}finally{$sha.Dispose()}
