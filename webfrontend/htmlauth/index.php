<?php
declare(strict_types=1);
require_once 'loxberry_system.php';
require_once 'loxberry_web.php';

// The plugin is served exclusively through LoxBerry's authenticated htmlauth area.
if (empty($_SERVER['REMOTE_USER'])) {
    http_response_code(403);
    exit('Bitte über die LoxBerry-Pluginverwaltung anmelden.');
}
$https = !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off';
$cookiePath = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/') . '/';
session_name('porsche2lox_' . substr(hash('sha256', $lbpdatadir), 0, 12));
session_set_cookie_params(['httponly' => true, 'secure' => $https, 'samesite' => 'Strict', 'path' => $cookiePath]);
ini_set('session.use_strict_mode', '1');
session_start();
if (!isset($_SESSION['csrf'])) {
    $_SESSION['csrf'] = bin2hex(random_bytes(32));
}
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: no-referrer');
header('X-Frame-Options: SAMEORIGIN');

// Model images are private cached files, exposed only for configured vehicles.
if (isset($_GET['image'])) {
    session_write_close();
    $config = json_decode(@file_get_contents($lbpconfigdir . '/settings.json') ?: '{}', true);
    foreach (($config['vehicles'] ?? []) as $vehicle) {
        if (($vehicle['alias'] ?? '') !== $_GET['image']) { continue; }
        $path = $lbpdatadir . '/vehicle-' . hash('sha256', $vehicle['vin']) . '.image';
        if (!is_file($path) || filesize($path) > 2000000) { break; }
        $mime = (new finfo(FILEINFO_MIME_TYPE))->file($path);
        if (!in_array($mime, ['image/png', 'image/jpeg', 'image/webp'], true)) { break; }
        header('Content-Type: ' . $mime);
        header('Cache-Control: private, max-age=3600');
        readfile($path);
        exit;
    }
    http_response_code(404);
    exit;
}

if (isset($_GET['api'])) {
    header('Content-Type: application/json; charset=utf-8');
    try {
        if ($_SERVER['REQUEST_METHOD'] !== 'POST' ||
            !hash_equals($_SESSION['csrf'], $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '')) {
            http_response_code(403);
            throw new RuntimeException('Ungültige Anfrage. Bitte Seite neu laden.');
        }
        if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 30000) {
            throw new RuntimeException('Anfrage zu groß.');
        }
        $request = json_decode(file_get_contents('php://input', false, null, 0, 30001), true, 32, JSON_THROW_ON_ERROR);
        $allowed = ['status', 'save', 'login', 'captcha', 'vehicles', 'poll', 'logout', 'cancel', 'loxone_export'];
        if (!is_array($request) || !in_array($request['action'] ?? '', $allowed, true)) {
            throw new RuntimeException('Diese Aktion wird nicht unterstützt.');
        }
        if (!$https && in_array($request['action'], ['login', 'captcha', 'save'], true)) {
            throw new RuntimeException('Bitte LoxBerry über HTTPS öffnen, bevor Zugangsdaten eingegeben werden.');
        }
        session_write_close();
        $socket = @stream_socket_client('unix://' . $lbpdatadir . '/control.sock', $errno, $error, 3);
        if (!$socket) {
            throw new RuntimeException('PLX-Dienst nicht erreichbar. Bitte Installation und Dienststatus prüfen.');
        }
        stream_set_timeout($socket, 25);
        // Associative decoding turns an empty JSON object into a PHP array.
        // Preserve the control protocol's object type for parameterless actions.
        if (isset($request['params']) && $request['params'] === []) {
            $request['params'] = new stdClass();
        }
        $wire = json_encode($request, JSON_THROW_ON_ERROR) . "\n";
        $offset = 0;
        while ($offset < strlen($wire)) {
            $written = fwrite($socket, substr($wire, $offset));
            if (!$written) { throw new RuntimeException('Anfrage konnte nicht übertragen werden.'); }
            $offset += $written;
        }
        $reply = fgets($socket, 4194305);
        fclose($socket);
        if ($reply === false || strlen($reply) > 4194304) {
            throw new RuntimeException('Der Dienst hat nicht rechtzeitig geantwortet.');
        }
        json_decode($reply, true, 64, JSON_THROW_ON_ERROR);
        echo $reply;
    } catch (Throwable $error) {
        if (http_response_code() < 400) { http_response_code(400); }
        // Only deliberate messages are returned; never dump request or exception traces.
        $message = $error instanceof RuntimeException ? $error->getMessage() : 'Ungültige Anfrage.';
        echo json_encode(['ok' => false, 'error' => $message]);
    }
    exit;
}
$csrf = htmlspecialchars($_SESSION['csrf'], ENT_QUOTES, 'UTF-8');
session_write_close();
LBWeb::lbheader('PLX', 'https://github.com/square-com-de/plx', '', true);
include $lbptemplatedir . '/dashboard.html';
LBWeb::lbfooter();
