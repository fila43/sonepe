<?php
$name = rand();
//var_dump($_POST);
$inputJSON = file_get_contents('php://input');
//$input= json_decode( $inputJSON );
//var_dump($input);
file_put_contents("data/".strval($name), $inputJSON);
echo($name);
?>
