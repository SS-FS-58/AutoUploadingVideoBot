<?php

$target_dir = "uploads/";

if (file_exists(__DIR__ . '/session/active')) {
    echo "Error : another upload is running . please wait";
    exit;
}
$target_thumb_file = handleFile($target_dir, 'thumb');
if (!$target_thumb_file) {
    echo "Error : unable to upload thumb image";
    exit;
}
$target_video_file = handleFile($target_dir, 'video');

if (!$target_video_file) {
    echo "Error : unable to upload video";
    exit;
}

$info = ['title' => $_POST['title'], 'description' => $_POST['description'], 'thumb' => $target_thumb_file, 'video' => $target_video_file,

    'service' => $_POST['checkbox'],

];

file_put_contents('uploads/' . microtime(true) . '.json', json_encode($info));

exit("All information uploaded check upload terminal for upload details");

function handleFile($target_dir, $input)
{
    if (isset($_FILES[$input])) {
        $target_file = $target_dir . basename($_FILES[$input]["name"]);
        $imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));
        // Check if image file is a actual image or fake image
        if (isset($_POST["submit"])) {
            move_uploaded_file($_FILES[$input]['tmp_name'], $target_file);
            return $target_file;
        }
    }
    return false;
}