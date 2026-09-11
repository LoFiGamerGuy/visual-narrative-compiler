$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$configPath=Join-Path $PSScriptRoot 'execution-config.json'
$config=Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
$utf8=New-Object System.Text.UTF8Encoding($false)
$sha=[System.Security.Cryptography.SHA256]::Create()
function HashFile([string]$path) {
 $stream=[System.IO.File]::OpenRead($path)
 try { return [System.BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','').ToLowerInvariant() } finally { $stream.Dispose() }
}
function Emit($value) { $value | ConvertTo-Json -Depth 8 -Compress | Write-Output }
$state=[ordered]@{status='running-preflight-no-deletions';started_utc=[DateTime]::UtcNow.ToString('o');free_C_before=[System.IO.DriveInfo]::new('C').AvailableFreeSpace;config_sha256=(HashFile $configPath);archives=@();directory_actions=@();duplicate_actions=@();errors=@()}
function SaveState { [System.IO.File]::WriteAllText((Join-Path $PSScriptRoot 'preflight.json'),($state|ConvertTo-Json -Depth 12),$utf8) }
SaveState
try {
 $maps=@{};$pools=@{}
 foreach($archive in $config.archives) {
  $file=Get-Item -LiteralPath $archive.path
  if($file.Length -ne $archive.bytes){throw ('ZIP size mismatch: '+$archive.path)}
  $actual=HashFile $archive.path
  if($actual -ne $archive.sha256){throw ('ZIP SHA mismatch: '+$archive.path)}
  if((HashFile $archive.manifest_path) -ne $archive.manifest_sha256){throw 'Retained manifest changed'}
  $manifest=Get-Content -Raw -LiteralPath $archive.manifest_path | ConvertFrom-Json
  $map=@{};$pool=@{}
  foreach($record in $manifest.files){
   $key=$record.path.Replace('\','/');$identity=$record.sha256+':'+$record.bytes
   if(!$map.ContainsKey($key)){$map[$key]=@()};$map[$key]+=$identity
   $pool[$identity]=$record.path
  }
  $mi=Get-Item -LiteralPath $archive.manifest_path;$identity=$archive.manifest_sha256+':'+$mi.Length
  $map['PACKAGE-MANIFEST.json']=@($identity);$pool[$identity]='PACKAGE-MANIFEST.json'
  $maps[$archive.version]=$map;$pools[$archive.version]=$pool
  $state.archives+=@{version=$archive.version;path=$archive.path;bytes=$file.Length;sha256=$actual;manifest_sha256=$archive.manifest_sha256;mtime_ticks=$file.LastWriteTimeUtc.Ticks;status='retained-zip-current-sha256-matches-recorded-build'}
  SaveState;Emit @{event='retained-archive-verified';version=$archive.version;bytes=$file.Length}
 }
 foreach($action in $config.directory_actions){
  $target=[System.IO.Path]::GetFullPath($action.path);$content=[System.IO.Path]::GetFullPath($action.content_root)
  if(!$target.StartsWith($config.base+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Target outside isolated worktree'}
  if($target -eq $config.protected_reader -or $config.protected_reader.StartsWith($target+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Protected reader deletion target'}
  if(!$content.StartsWith($target,[System.StringComparison]::OrdinalIgnoreCase)){throw 'Invalid content root'}
  $targetItem=Get-Item -LiteralPath $target
  $inventory=Join-Path $PSScriptRoot ('inventories\'+$action.id+'.jsonl')
  $writer=New-Object System.IO.StreamWriter($inventory,$false,$utf8)
  [long]$bytes=0;[long]$count=0;[long]$matched=0;$unique=@()
  $stack=New-Object 'System.Collections.Generic.Stack[System.IO.DirectoryInfo]';$stack.Push($targetItem)
  try {
   while($stack.Count -gt 0){
    $dir=$stack.Pop()
    if(($dir.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0){throw ('Reparse directory: '+$dir.FullName)}
    foreach($item in $dir.GetFileSystemInfos()){
     if(($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0){throw ('Reparse item: '+$item.FullName)}
     if(($item.Attributes -band [System.IO.FileAttributes]::Directory) -ne 0){$stack.Push($item);continue}
     $rel=$item.FullName.Substring($target.Length+1).Replace('\','/')
     $contentRel=if($item.FullName.StartsWith($content+'\',[System.StringComparison]::OrdinalIgnoreCase)){$item.FullName.Substring($content.Length+1).Replace('\','/')}else{'OUTSIDE-CONTENT/'+$rel}
     [long]$n=$item.Length;[long]$ticks=$item.LastWriteTimeUtc.Ticks;$hash=HashFile $item.FullName
     $item.Refresh();if($item.Length -ne $n -or $item.LastWriteTimeUtc.Ticks -ne $ticks){throw ('File changed while hashing: '+$item.FullName)}
     $identity=$hash+':'+$n;$isMatch=$maps[$action.archive_version].ContainsKey($contentRel) -and $maps[$action.archive_version][$contentRel] -contains $identity
     $matchedVia=$action.archive_version
     if(!$isMatch -and $action.kind -eq 'partial_staging'){
      foreach($version in @($action.archive_version,$action.also_compare_version)){
       if($pools[$version].ContainsKey($identity)){$isMatch=$true;$matchedVia=$version+':'+$pools[$version][$identity];break}
      }
     }
     if($isMatch){$matched++}else{
      $ext=[System.IO.Path]::GetExtension($item.Name);if($ext.Length -gt 12){$ext='.bin'}
      $preserved=Join-Path $PSScriptRoot ('unique-files\'+$hash+$ext)
      if(!(Test-Path -LiteralPath $preserved)){[System.IO.File]::Copy($item.FullName,$preserved,$false)}
      if((HashFile $preserved) -ne $hash -or (Get-Item -LiteralPath $preserved).Length -ne $n){throw 'Unique preservation mismatch'}
      $unique+=@{original_path=$item.FullName;relative_path=$rel;bytes=$n;sha256=$hash;preserved_path=$preserved}
     }
     $writer.WriteLine((@{p=$rel;n=$n;t=$ticks;h=$hash;contained=$isMatch;via=$matchedVia}|ConvertTo-Json -Compress))
     $bytes+=$n;$count++
     if($count % 5000 -eq 0){Emit @{event='candidate-hashing';id=$action.id;files=$count;bytes=$bytes}}
    }
   }
  }finally{$writer.Dispose()}
  $record=@{id=$action.id;phase=$action.phase;kind=$action.kind;path=$target;content_root=$content;archive_version=$action.archive_version;files=$count;bytes=$bytes;planned_bytes=$action.planned_bytes;matched_files=$matched;unique_preserved=$unique;inventory=$inventory;inventory_sha256=(HashFile $inventory);status='contained-or-unique-preserved-ready-for-explicit-removal'}
  $state.directory_actions+=$record;SaveState;Emit @{event='candidate-ready';id=$action.id;files=$count;bytes=$bytes;unique_preserved=$unique.Count;path=$target}
 }
 foreach($action in $config.duplicate_actions){
  $a=Get-Item -LiteralPath $action.remove;$b=Get-Item -LiteralPath $action.retain
  if($a.Length -ne $action.bytes -or $b.Length -ne $action.bytes){throw 'Duplicate archive size changed'}
  if((HashFile $a.FullName) -ne $action.sha256 -or (HashFile $b.FullName) -ne $action.sha256){throw 'Duplicate archive hash changed'}
  $state.duplicate_actions+=@{id=$action.id;remove=$a.FullName;retain=$b.FullName;bytes=$a.Length;sha256=$action.sha256;remove_mtime_ticks=$a.LastWriteTimeUtc.Ticks;retain_mtime_ticks=$b.LastWriteTimeUtc.Ticks;status='current-full-sha256-identical'}
  SaveState;Emit @{event='duplicate-archive-ready';id=$action.id;bytes=$a.Length}
 }
 $state.status='preflight-complete-no-deletions';$state.ended_utc=[DateTime]::UtcNow.ToString('o');SaveState
 Emit @{event='preflight-complete';directories=$state.directory_actions.Count;duplicates=$state.duplicate_actions.Count;archives=$state.archives.Count}
}catch{
 $state.status='preflight-error-no-deletions';$state.errors+=($_|Out-String);SaveState;Emit @{event='preflight-error';error=($_|Out-String)};exit 1
}finally{$sha.Dispose()}
