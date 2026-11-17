<?php
// Private lead tracker. Protect this folder with cPanel "Directory Privacy" before use.
$user = $_SERVER['REMOTE_USER'] ?? $_SERVER['REDIRECT_REMOTE_USER'] ?? $_SERVER['PHP_AUTH_USER'] ?? '';
if ($user === '') { http_response_code(403); exit('Locked. Turn on Directory Privacy for the admin folder in cPanel, then reload.'); }

$file = dirname(__DIR__, 2) . '/paiment-data/leads.jsonl';
$statuses = ['New', 'Contacted', 'Statement received', 'Quoted', 'Won', 'Lost'];

function load(string $file): array {
    if (!is_file($file)) return [];
    $rows = [];
    foreach (file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        $r = json_decode($line, true);
        if (is_array($r) && isset($r['id'])) $rows[] = $r;
    }
    return $rows;
}
function e($v): string { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); }

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $origin = parse_url($_SERVER['HTTP_ORIGIN'] ?? $_SERVER['HTTP_REFERER'] ?? '', PHP_URL_HOST);
    if ($origin !== ($_SERVER['HTTP_HOST'] ?? '')) { http_response_code(403); exit('Blocked.'); }
    $rows = load($file);
    foreach ($rows as &$r) {
        if ($r['id'] === ($_POST['id'] ?? '')) {
            if (in_array($_POST['status'] ?? '', $statuses, true)) $r['status'] = $_POST['status'];
            $fu = $_POST['follow_up'] ?? '';
            $r['follow_up'] = preg_match('/^\d{4}-\d{2}-\d{2}$/', $fu) ? $fu : '';
            $r['notes'] = substr(trim((string)($_POST['notes'] ?? '')), 0, 2000);
        }
    }
    unset($r);
    file_put_contents($file, implode("\n", array_map('json_encode', $rows)) . "\n", LOCK_EX);
    header('Location: ./', true, 303); exit;
}
$rows = array_reverse(load($file));
$today = date('Y-m-d');
?><!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Paiment leads</title>
<style>
body{margin:0;font:16px/1.5 system-ui,sans-serif;background:#EEF0F2;color:#23262B}
main{max-width:1100px;margin:0 auto;padding:32px 20px}
h1{margin:0 0 4px;font-size:32px}
.lead{background:#fff;border-radius:16px;padding:20px;margin-top:16px;display:flex;flex-wrap:wrap;gap:16px 32px}
.lead>div{flex:1 1 260px;min-width:0}
.due{box-shadow:inset 0 0 0 2px #FF8A2A}
label{display:block;font-weight:600;font-size:14px;margin-top:8px}
select,input,textarea{font:inherit;width:100%;box-sizing:border-box;padding:8px 10px;border:1.5px solid #8A9099;border-radius:8px;background:#fff}
button{font:inherit;font-weight:600;margin-top:12px;padding:10px 18px;border:0;border-radius:10px;background:#23262B;color:#fff;cursor:pointer}
small{color:#4A4F57}
</style></head><body><main>
<h1>Leads</h1>
<small><?= count($rows) ?> total. Orange outline means the follow-up date is today or past.</small>
<?php if (!$rows): ?><p>No leads yet. Submitted forms will appear here.</p><?php endif; ?>
<?php foreach ($rows as $r): $due = ($r['follow_up'] ?? '') !== '' && $r['follow_up'] <= $today && !in_array($r['status'], ['Won', 'Lost'], true); ?>
<section class="lead<?= $due ? ' due' : '' ?>">
<div>
<strong><?= e($r['business']) ?></strong><br><?= e($r['name']) ?><br>
<a href="mailto:<?= e($r['email']) ?>"><?= e($r['email']) ?></a><br><?= e($r['phone']) ?><br>
<small>Monthly card sales: <?= e($r['volume']) ?><br>Received <?= e(substr($r['at'], 0, 10)) ?></small>
</div>
<form method="post"><input type="hidden" name="id" value="<?= e($r['id']) ?>">
<label>Status<select name="status"><?php foreach ($statuses as $s): ?><option<?= $s === $r['status'] ? ' selected' : '' ?>><?= e($s) ?></option><?php endforeach; ?></select></label>
<label>Next follow-up<input type="date" name="follow_up" value="<?= e($r['follow_up'] ?? '') ?>"></label>
<label>Notes<textarea name="notes" rows="2"><?= e($r['notes'] ?? '') ?></textarea></label>
<button type="submit">Save</button></form>
</section>
<?php endforeach; ?>
</main></body></html>
