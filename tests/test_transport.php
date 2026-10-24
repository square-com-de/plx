<?php
require $argv[1];
$cases = [
 [['HTTPS'=>'on'], [], true], [['HTTPS'=>'1'], [], true], [['HTTPS'=>'off'], [], false], [['HTTPS'=>'false'], [], false],
 [['HTTPS'=>'off','REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>'https'], [], false],
 [['REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>'https'], ['192.0.2.10'], true],
 [['REMOTE_ADDR'=>'192.0.2.11','HTTP_X_FORWARDED_PROTO'=>'https'], ['192.0.2.10'], false],
 [['REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>'https,http'], ['192.0.2.10'], false],
 [['REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>'http,https'], ['192.0.2.10'], false],
 [['REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>'http'], ['192.0.2.10'], false],
 [['REMOTE_ADDR'=>'192.0.2.10','HTTP_FORWARDED'=>'proto=https','HTTP_X_FORWARDED_SSL'=>'on'], ['192.0.2.10'], false],
 [['REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>'https'], ['0.0.0.0/0'], false],
 [['REMOTE_ADDR'=>'::1','HTTP_X_FORWARDED_PROTO'=>'https'], ['0:0:0:0:0:0:0:1'], true],
 [['HTTPS'=>'on','REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>'http'], ['192.0.2.10'], false],
 [['HTTPS'=>'on','REMOTE_ADDR'=>'192.0.2.10'], ['192.0.2.10'], true],
 [['HTTPS'=>'on','REMOTE_ADDR'=>'192.0.2.11','HTTP_X_FORWARDED_PROTO'=>'http'], ['192.0.2.10'], true],
 [['REMOTE_ADDR'=>'not-an-ip','HTTP_X_FORWARDED_PROTO'=>'https'], ['not-an-ip'], false],
 [['REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>'HTTPS'], ['invalid',42,'192.0.2.10'], true],
 [['REMOTE_ADDR'=>'192.0.2.10','HTTP_X_FORWARDED_PROTO'=>''], ['192.0.2.10'], false]
];
foreach ($cases as $i=>$case) {
 if(plx_is_https($case[0],$case[1]) !== $case[2]) { throw new Exception('case '.$i); }
}
$dir=sys_get_temp_dir().'/plx-transport-'.bin2hex(random_bytes(8));mkdir($dir,0700);
try {
 foreach ([null,'broken','{"trusted_proxies":"192.0.2.10"}',str_repeat('x',4097)] as $value) {
  if ($value !== null) file_put_contents($dir.'/trusted-proxies.json',$value);
  if(plx_trusted_proxies($dir)!==[]) throw new Exception('invalid config trusted');
 }
 file_put_contents($dir.'/trusted-proxies.json','{"trusted_proxies":["192.0.2.10"]}');
 if(plx_trusted_proxies($dir)!==['192.0.2.10']) throw new Exception('valid config ignored');
} finally { @unlink($dir.'/trusted-proxies.json');rmdir($dir); }
echo count($cases)." transport cases and 5 config cases passed\n";
