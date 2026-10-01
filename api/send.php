<?php
/* Обработчик заявок с сайта РемКомСтрой.
   Принимает POST от форм калькулятора и записи на замер, отправляет письмо
   администратору и отвечает JSON-ом. Работает на обычном PHP-хостинге. */

declare(strict_types=1);

/* Совместимо с PHP 7.4 и новее: без синтаксиса и функций PHP 8,
   потому что на shared-хостингах до сих пор встречается 7.4. */

$config = require __DIR__ . '/config.php';

$wantsJson = strpos((string)($_SERVER['HTTP_ACCEPT'] ?? ''), 'application/json') !== false;

/** Ответ клиенту и выход. */
function respond(bool $ok, string $message, int $code = 200)
{
    global $wantsJson, $config;

    if ($wantsJson) {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok, 'message' => $message], JSON_UNESCAPED_UNICODE);
        exit;
    }

    // форма отправлена без JS
    if ($ok) {
        header('Location: ' . $config['fallback_redirect']);
    } else {
        http_response_code($code);
        header('Content-Type: text/plain; charset=utf-8');
        echo $message;
    }
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    respond(false, 'Метод не поддерживается.', 405);
}

/* ---------- ловушка для ботов ---------- */

if (trim((string)($_POST['website'] ?? '')) !== '') {
    // бот заполнил скрытое поле. Отвечаем «успехом», чтобы не подсказывать ему.
    respond(true, 'Заявка отправлена.');
}

/* ---------- ограничение частоты ---------- */

$ip = (string)($_SERVER['REMOTE_ADDR'] ?? '0.0.0.0');
$bucket = sys_get_temp_dir() . '/rks-rate-' . md5($ip) . '.json';
$now = time();
$hits = [];

if (is_readable($bucket)) {
    $decoded = json_decode((string)file_get_contents($bucket), true);
    if (is_array($decoded)) {
        $hits = array_filter($decoded, fn($t) => is_int($t) && $t > $now - (int)$config['rate_window']);
    }
}

if (count($hits) >= (int)$config['rate_limit']) {
    respond(false, 'Слишком много заявок подряд. Позвоните нам: +7 (909) 559-41-50.', 429);
}

$hits[] = $now;
@file_put_contents($bucket, json_encode(array_values($hits)), LOCK_EX);

/* ---------- разбор и проверка ---------- */

/** Чистит пользовательский ввод: убирает управляющие символы и режет длину. */
function clean(string $key, int $max = 300): string
{
    $value = (string)($_POST[$key] ?? '');
    $value = str_replace(["\r", "\0"], '', $value);
    $value = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $value) ?? '';
    return mb_substr(trim($value), 0, $max);
}

$name    = clean('name', 80);
$phone   = clean('phone', 30);
$address = clean('address', 200);
$comment = clean('comment', 1000);
$summary = clean('calc_summary', 2000);
$formId  = clean('form_id', 40) ?: 'Заявка с сайта';
$page    = clean('page_url', 200);

$digits = preg_replace('/\D/', '', $phone) ?? '';

$errors = [];
if (mb_strlen($name) < 2)         $errors[] = 'Укажите имя.';
if (strlen($digits) !== 11)       $errors[] = 'Укажите телефон полностью.';
if (empty($_POST['consent']))     $errors[] = 'Нужно согласие на обработку персональных данных.';

if ($errors) {
    respond(false, implode(' ', $errors), 422);
}

/* ---------- письмо ---------- */

$lines = [];
$lines[] = 'Тип заявки: ' . $formId;
$lines[] = 'Имя: ' . $name;
$lines[] = 'Телефон: ' . $phone;
if ($address !== '') $lines[] = 'Адрес для замера: ' . $address;
if ($comment !== '') $lines[] = 'Комментарий: ' . $comment;

if ($summary !== '') {
    $lines[] = '';
    $lines[] = '--- Расчёт калькулятора ---';
    $lines[] = $summary;
}

$lines[] = '';
$lines[] = '--- Служебное ---';
$lines[] = 'Время: ' . date('d.m.Y H:i:s');
if ($page !== '') $lines[] = 'Страница: ' . $page;
$lines[] = 'IP: ' . $ip;

$body = implode("\n", $lines);

$subject = sprintf('%s: %s, %s', $formId, $name, $phone);

/* Тема письма кодируется в base64: без этого кириллица в заголовке ломается. */
$encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
$encodedFrom = '=?UTF-8?B?' . base64_encode((string)$config['from_name']) . '?=';

$headers = implode("\r\n", [
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'From: ' . $encodedFrom . ' <' . $config['from_email'] . '>',
    'Reply-To: ' . $config['from_email'],
    'X-Mailer: PHP/' . phpversion(),
]);

// копия в файл до отправки: если mail() отвалится, заявка всё равно не потеряется
if (!empty($config['log_file'])) {
    @file_put_contents(
        $config['log_file'],
        "==== " . date('d.m.Y H:i:s') . " ====\n" . $body . "\n\n",
        FILE_APPEND | LOCK_EX
    );
}

$sent = @mail(
    (string)$config['admin_email'],
    $encodedSubject,
    $body,
    $headers,
    '-f' . $config['from_email']
);

if (!$sent) {
    respond(false, 'Письмо не ушло, но заявка сохранена. Позвоните нам: +7 (909) 559-41-50.', 500);
}

respond(true, 'Заявка отправлена. Перезвоним в рабочее время: ежедневно с 9:00 до 20:00.');
