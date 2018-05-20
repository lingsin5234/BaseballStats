<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title></title>
<meta name="keywords" content="" />
<meta name="description" content="" />
<link href="http://fonts.googleapis.com/css?family=Didact+Gothic" rel="stylesheet" />
<link href="defaults.css" rel="stylesheet" type="text/css" media="all" />
<link href="fonts.css" rel="stylesheet" type="text/css" media="all" />

<?php
$servername= "localhost";
$username= "joshweb"; 
$password= "mYW36s!T3";
$database= "ServerJS";

// Connect to Database 
$conn = new mysqli($servername, $username, $password, $database); 

// Check Connection 
if ($conn->connect_error) {
 die("Connection failed: " . $conn->connect_error);
}

echo "Connected succesfully";
?>

</head>
<body>
<div id="header-wrapper">
	<div id="header" class="container">
		<div id="logo">
			<h1>Baseball10</h1>

		</div>
		<div id="menu">
			<ul>
				<li><a href="home.php" accesskey="1" title="">Home</a></li>
				<li><a href="profile10.php" accesskey="2" title="">Profile</a></li>
				<li><a href="teams10.php" accesskey="3" title="">Teams</a></li>
				<li><a href="top10.php" accesskey="4" title="">Top 10</a></li>
				<li><a href="blogs10.php" accesskey="5" title="">Blogs</a></li>
			</ul>
		</div>
		</div>

<div id="page" class="container">
	<div class="title">
<h1>Profile</h1>
<p>We chose to explore the top 10 players stats because we feel that best exemplifies the players that fantasy would want to choose for their team. The blog is also to showcase opinions on the progression of players. As well as the trades that are going along in the offseason. </p>

<img src="images/homerhalloffame.jpg" width="100%" height="500px" alt=""/>
<button type="button"
onclick="document.getElementById('demo').innerHTML = Date()">
Display Date and Time.</button>

<p id="demo"></p>
	<div id="copyright" class="container"> 
	<p>&copy; Untitled. All rights reserved. | Photos by <a href="http://humling.com/">HUMLING</a> | Design by <a href="http://humling.co" rel="nofollow">HUMLING</a>.</p>
</div>

<?php
$conn ->close ();
?>

</body>
</html>
