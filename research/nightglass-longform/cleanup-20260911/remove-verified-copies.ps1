$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$utf8=New-Object System.Text.UTF8Encoding($false)
$sha=[System.Security.Cryptography.SHA256]::Create()
function HashFile([string]$path){$stream=[System.IO.File]::OpenRead($path);try{return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','').ToLowerInvariant()}finally{$stream.Dispose()}}
function Emit($value){$value|ConvertTo-Json -Depth 8 -Compress|Write-Output}
$configPath=Join-Path $PSScriptRoot 'execution-config.json'
$config=Get-Content -Raw -LiteralPath $configPath|ConvertFrom-Json
$binding=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'removal-binding.json')|ConvertFrom-Json
$preflightPath=Join-Path $PSScriptRoot 'preflight.json'
if((HashFile $preflightPath) -ne $binding.preflight_sha256){throw 'Preflight binding changed'}
$preflight=Get-Content -Raw -LiteralPath $preflightPath|ConvertFrom-Json
if($preflight.status -ne 'preflight-complete-no-deletions' -or $preflight.errors.Count -ne 0){throw 'Preflight incomplete'}
if((HashFile $configPath) -ne $preflight.config_sha256){throw 'Configuration changed'}
$state=[ordered]@{status='removal-running';authorization=$config.authorized_by;started_utc=[DateTime]::UtcNow.ToString('o');free_C_before=[System.IO.DriveInfo]::new('C').AvailableFreeSpace;preflight_sha256=$binding.preflight_sha256;actions=@();current_action=$null;logical_bytes_removed=[long]0;files_removed=[long]0;errors=@()}
function SaveState{[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'removal-result.json'),($state|ConvertTo-Json -Depth 12),$utf8)}
SaveState
try{
 foreach($a in $preflight.archives){$f=Get-Item -LiteralPath $a.path;if($f.Length -ne $a.bytes -or $f.LastWriteTimeUtc.Ticks -ne $a.mtime_ticks){throw ('Retained archive changed: '+$a.path)}}
 foreach($a in $preflight.directory_actions){
  if($binding.directory_paths -notcontains $a.path){throw 'Target not explicitly bound'}
  $target=[IO.Path]::GetFullPath($a.path)
  if(!$target.StartsWith($config.base+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Directory outside permitted worktree'}
  if($target -eq $config.protected_reader -or $config.protected_reader.StartsWith($target+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Protected reader target'}
  if((HashFile $a.inventory) -ne $a.inventory_sha256){throw 'Candidate inventory changed'}
  foreach($u in $a.unique_preserved){if((HashFile $u.preserved_path) -ne $u.sha256 -or (Get-Item -LiteralPath $u.preserved_path).Length -ne $u.bytes){throw 'Preserved unique file missing or changed'}}
  $expected=@{};foreach($line in [IO.File]::ReadLines($a.inventory)){$entry=$line|ConvertFrom-Json;$expected[$entry.p]=$entry}
  [long]$count=0;[long]$bytes=0;$stack=New-Object 'System.Collections.Generic.Stack[System.IO.DirectoryInfo]';$stack.Push((Get-Item -LiteralPath $target))
  while($stack.Count -gt 0){
   $dir=$stack.Pop();if(($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'Reparse directory before deletion'}
   foreach($item in $dir.GetFileSystemInfos()){
    if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'Reparse item before deletion'}
    if(($item.Attributes -band [IO.FileAttributes]::Directory) -ne 0){$stack.Push($item);continue}
    $rel=$item.FullName.Substring($target.Length+1).Replace('\','/')
    if(!$expected.ContainsKey($rel)){throw ('New file since preflight: '+$item.FullName)}
    $e=$expected[$rel];if($item.Length -ne $e.n -or $item.LastWriteTimeUtc.Ticks -ne $e.t){throw ('Changed file since preflight: '+$item.FullName)}
    $count++;$bytes+=$item.Length
   }
  }
  if($count -ne $a.files -or $count -ne $expected.Count -or $bytes -ne $a.bytes){throw 'Candidate inventory mismatch before deletion'}
  $state.current_action=@{id=$a.id;path=$target;files=$count;bytes=$bytes;status='checked-and-starting-removal'};SaveState
  [IO.Directory]::Delete($target,$true)
  if([IO.Directory]::Exists($target)){throw 'Directory remains after removal'}
  $state.actions+=@{id=$a.id;phase=$a.phase;kind=$a.kind;removed_path=$target;bytes=$bytes;files=$count;retained_archive_version=$a.archive_version;unique_preserved=$a.unique_preserved;inventory_sha256=$a.inventory_sha256;status='removed-after-containment-and-change-check';utc=[DateTime]::UtcNow.ToString('o')}
  $state.logical_bytes_removed+=$bytes;$state.files_removed+=$count;$state.current_action=$null;SaveState
  Emit @{event='directory-removed';id=$a.id;bytes=$bytes;files=$count;path=$target}
 }
 foreach($a in $preflight.duplicate_actions){
  if($binding.duplicate_paths -notcontains $a.remove){throw 'Duplicate deletion not explicitly bound'}
  $remove=Get-Item -LiteralPath $a.remove;$retain=Get-Item -LiteralPath $a.retain
  if($remove.Length -ne $a.bytes -or $retain.Length -ne $a.bytes -or $remove.LastWriteTimeUtc.Ticks -ne $a.remove_mtime_ticks -or $retain.LastWriteTimeUtc.Ticks -ne $a.retain_mtime_ticks){throw 'Duplicate ZIP changed since full-hash check'}
  $state.current_action=@{id=$a.id;path=$a.remove;bytes=$a.bytes;status='starting-exact-duplicate-removal'};SaveState
  [IO.File]::Delete($a.remove)
  if([IO.File]::Exists($a.remove)){throw 'Duplicate ZIP remains'}
  $state.actions+=@{id=$a.id;phase=1;kind='duplicate_archive';removed_path=$a.remove;retained_path=$a.retain;bytes=$a.bytes;files=1;sha256=$a.sha256;status='duplicate-filename-retired-retained-by-exact-sha256';utc=[DateTime]::UtcNow.ToString('o')}
  $state.logical_bytes_removed+=$a.bytes;$state.files_removed++;$state.current_action=$null;SaveState
  Emit @{event='duplicate-archive-removed';id=$a.id;bytes=$a.bytes;retained=$a.retain}
 }
 $state.status='phases1-2-removal-complete-postcheck-pending';$state.ended_utc=[DateTime]::UtcNow.ToString('o');$state.free_C_after=[IO.DriveInfo]::new('C').AvailableFreeSpace;SaveState
 Emit @{event='removal-complete';actions=$state.actions.Count;bytes=$state.logical_bytes_removed;files=$state.files_removed;free_C_after=$state.free_C_after}
}catch{$state.status='removal-error';$state.errors+=($_|Out-String);SaveState;Emit @{event='removal-error';error=($_|Out-String)};exit 1}finally{$sha.Dispose()}
