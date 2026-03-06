<?php
// ============================================================
//  AK Enterprise Group – Contact Form Mail Handler (SMTP)
//  Receives POST data from contact.html and sends email via SMTP
// ============================================================

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
use PHPMailer\PHPMailer\SMTP;

require 'phpmailer/Exception.php';
require 'phpmailer/PHPMailer.php';
require 'phpmailer/SMTP.php';

// --- Configuration ---
$to_email = 'a.kenterprise0611@gmail.com'; // Recipient email
$from_email = 'vedtomer5592@gmail.com'; // Your Gmail Address
$app_pass = 'qcrp nlhs dxgy bxqv'; // Your Gmail App Password
$site_name = 'Enterprise';

// --- Only accept POST ---
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed.']);
    exit;
}

// --- Sanitize Input ---
$name = trim(strip_tags($_POST['name'] ?? ''));
$email = trim(strip_tags($_POST['email'] ?? ''));
$subject = trim(strip_tags($_POST['subject'] ?? ''));
$message = trim(strip_tags($_POST['message'] ?? ''));

// --- Validate ---
if (empty($name) || empty($email) || empty($subject) || empty($message)) {
    echo json_encode(['success' => false, 'message' => 'Sabhi fields bharna zaroori hai.']);
    exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['success' => false, 'message' => 'Invalid email address.']);
    exit;
}

// --- SMTP Execution ---
$mail = new PHPMailer(true);

try {
    // Server settings
    $mail->isSMTP();
    $mail->Host = 'smtp.gmail.com';
    $mail->SMTPAuth = true;
    $mail->Username = $from_email;
    $mail->Password = $app_pass;
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Port = 587;

    // Recipients
    $mail->setFrom($from_email, $site_name);
    $mail->addAddress($to_email);
    $mail->addReplyTo($email, $name);

    // Content
    $mail->isHTML(false);
    $mail->Subject = "[{$site_name}] New Enquiry: {$subject}";

    $mail_body = "Namaskar,\n\n";
    $mail_body .= "Aapko website se ek naya message mila hai.\n";
    $mail_body .= "========================================\n";
    $mail_body .= "Sender Ka Naam : {$name}\n";
    $mail_body .= "Sender Ka Email: {$email}\n";
    $mail_body .= "Subject        : {$subject}\n";
    $mail_body .= "========================================\n\n";
    $mail_body .= "Message:\n{$message}\n\n";
    $mail_body .= "========================================\n";
    $mail_body .= "Yeh message {$site_name} website ke contact form se aaya hai.\n";
    $mail_body .= "Website: https://akenterprisegroup.com\n";

    $mail->Body = $mail_body;

    $mail->send();
    echo json_encode(['success' => true, 'message' => 'Message bhej diya gaya! Hum jald aapse sampark karenge.']);
}
catch (Exception $e) {
    echo json_encode(['success' => false, 'message' => "Mail send karne mein problem aayi: {$mail->ErrorInfo}"]);
}
?>
