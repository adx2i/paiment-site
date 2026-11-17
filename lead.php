<?php
// Saves a rate-review request and emails a notification.
const NOTIFY_TO = 'info@paiment.cc';
const NOTIFY_FROM = 'noreply@paiment.cc';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: index.html#contact'); exit; }

function field(string $key, int $max = 160): string {
    $v = trim((string)($_POST[$key] ?? ''));
    $v = preg_replace('/[\r\n\t]+/', ' ', $v);
    return substr($v, 0, $max);
}

if (field('website') !== '') { header('Location: thanks.html', true, 303); exit; } // spam trap

$name = field('name', 120); $business = field('business'); $email = field('email');
$phone = field('phone', 40); $volume = field('volume', 40);

if ($name === '' || $business === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(422);
    echo '<!doctype html><meta charset="utf-8"><title>Check the form</title><p style="font-family:sans-serif;padding:40px">Please enter your name, business name and a valid email. <a href="index.html#contact">Go back to the form</a></p>';
    exit;
}

$dir = dirname(__DIR__) . '/paiment-data';
if (!is_dir($dir)) { mkdir($dir, 0700, true); }
$lead = ['id' => bin2hex(random_bytes(6)), 'at' => gmdate('c'), 'name' => $name, 'business' => $business,
    'email' => $email, 'phone' => $phone, 'volume' => $volume, 'status' => 'New', 'follow_up' => '', 'notes' => ''];
$saved = file_put_contents($dir . '/leads.jsonl', json_encode($lead) . "\n", FILE_APPEND | LOCK_EX);

$body = "New rate review request\n\nName: $name\nBusiness: $business\nEmail: $email\nPhone: $phone\nMonthly card sales: $volume\n";
$headers = 'From: Paiment website <' . NOTIFY_FROM . ">\r\nReply-To: $email\r\nContent-Type: text/plain; charset=UTF-8";
$mailed = @mail(NOTIFY_TO, 'New rate review request: ' . $business, $body, $headers);

if ($saved === false && !$mailed) {
    http_response_code(500);
    echo '<!doctype html><meta charset="utf-8"><title>Not sent</title><p style="font-family:sans-serif;padding:40px">Your request was not sent. Please email info@paiment.cc.</p>';
    exit;
}
header('Location: thanks.html', true, 303);
