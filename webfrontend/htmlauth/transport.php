<?php
declare(strict_types=1);

/** Only an explicitly trusted immediate peer may describe terminated TLS. */
function plx_is_https(array $server, array $trustedProxies): bool
{
    $native = strtolower((string)($server['HTTPS'] ?? ''));
    $peer = (string)($server['REMOTE_ADDR'] ?? '');
    $directHttps = $native === 'on' || $native === '1';
    if (!filter_var($peer, FILTER_VALIDATE_IP)) { return $directHttps; }
    foreach ($trustedProxies as $proxy) {
        if (!is_string($proxy) || !filter_var($proxy, FILTER_VALIDATE_IP)) { continue; }
        if (inet_pton($peer) === inet_pton($proxy) && array_key_exists('HTTP_X_FORWARDED_PROTO', $server)) {
            // Reject ambiguous/multi-hop lists rather than guessing their order.
            return strtolower(trim((string)($server['HTTP_X_FORWARDED_PROTO'] ?? ''))) === 'https';
        }
    }
    return $directHttps;
}

function plx_trusted_proxies(string $configDir): array
{
    $path = $configDir . '/trusted-proxies.json';
    if (!is_file($path) || filesize($path) > 4096) { return []; }
    $value = json_decode((string)@file_get_contents($path), true);
    return is_array($value) && isset($value['trusted_proxies']) && is_array($value['trusted_proxies'])
        ? $value['trusted_proxies'] : [];
}
