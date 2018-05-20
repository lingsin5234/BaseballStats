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
<h1>Teams</h1>

 <h1>MLB Teams</h1>
	
            <h1>American League</h1>
                <table border="collapse", width="100%">
                <tr>  
                <th>AL East</th>
                <th>AL Central</th>
                <th>AL West</th>
                </tr>
                <tr>
                <td><img src="images/baltor.jpg" width=25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/bal/baltimore-orioles">Baltimore Orioles</td>
		<td><img src="images/chicsox.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/chw/chicago-white-sox"> Chicago WhiteSox</td>
		<td><img src="images/houast.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/hou/houston-astros">Houston Astros</td>
                </tr>
                <tr>
                <td><img src="images/bostred.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/bos/boston-red-sox">Boston Red Sox</td>
		<td><img src="images/cleind.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/cle/cleveland-indians">Cleveland Indians</td>
		<td><img src="images/losang.jpg" width="20px" height="20px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/laa/los-angeles-angels">Los Angeles Angels</td>
                </tr>
                <tr>
		<td><img src="images/newyank.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/nyy/new-york-yankees">New York Yankees</td>
		<td><img src="images/dettig.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/det/detroit-tigers">Detroit Tigers</td>
		<td><img src="images/oakath.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/oak/oakland-athletics">Oakland Athletics</td>
		</tr>
                <tr>
		<td><img src="images/tampra.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/tb/tampa-bay-rays">TampaBay Rays</td>
		<td><img src="images/kcroy.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/kc/kansas-city-royals">Kansas City Royals</td>
		<td><img src="images/seamari.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/sea/seattle-mariners">Seattle Mariners</td>
		</tr>
                <tr>
		<td><img src="images/torjays.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/tor/toronto-blue-jays">Toronto Blue Jays</td>
		<td><img src="images/mintwi.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/min/minnesota-twins">Minnesota Twins</td>
		<td><img src="images/texran.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/tex/texas-rangers">Texas Rangers</td>
		</tr>
                </table>
<h1>National League</h1>
        <table border="collapse", width="100%">
        <tr>
        <th>NL East</th>
        <th>NL Central</th>
        <th>NL West</th>
        </tr>
        <tr>
	<td><img src="images/atlbra.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/atl/atlanta-braves">Atlanta Braves</td>
	<td><img src="images/chiccub.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/chc/chicago-cubs">Chicago Cubs</td>
	<td><img src="images/aridia.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/ari/arizona-diamondbacks">Arizona Diamondbacks</td>
        </tr>
        <tr>
	<td><img src="images/miamar.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/mia/miami-marlins">Miami Marlins</td>
	<td><img src="images/cinreds.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/cin/cincinnati-reds">Cincinnati Reds</td>
	<td><img src="images/colrock.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/col/colorado-rockies">Colorado Rockies</td>
        </tr>
        <tr>
	<td><img src="images/nymets.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/nym/new-york-mets">New York Mets</td>
	<td><img src="images/milbre.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/mil/milwaukee-brewers">Milwaukee Brewers</td>
	<td><img src="images/ladod.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/lad/los-angeles-dodgers">Los Angeles Dodgers</td>
	</tr>
        <tr>
	<td><img src="images/philph.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/phi/philadelphia-phillies">Philadelphia Phillies</td>
	<td><img src="images/pitpir.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/pit/pittsburgh-pirates">Pittsburgh Pirates</td>
	<td><img src="images/sanpad.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/sd/san-diego-padres">San Diego Padres</td>
	</tr>
        <tr>
	<td><img src="images/washnat.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/wsh/washington-nationals">Washington Nationals</td>
	<td><img src="images/stcard.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/stl/st-louis-cardinals">St.Louis Cardinals</td>
	<td><img src="images/sangia.jpg" width="25px" height="25px" alt=""/><a href="http://www.espn.com/mlb/team/roster/_/name/sf/san-francisco-giants">San Francisco Giants</td>
	</tr>
        </table>
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
