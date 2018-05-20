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
<h1>Blogs</h1>
<h3>Player Info Reference</h3>
		<td>
<form action="" method="post">
<select id="Players10" name="Players10">
<?php

     $query = "Select distinct playerID From basic_hitting_month Order By playerID";
	 $result= $conn -> query($query);
	 $options="";
	 while($row=$result->fetch_assoc()) {
	 echo "<option value=" .$row["playerID"]. ">" .$row["playerID"]. "</option>";
	 }
	 
	?>
	 
</select>
<input type="submit" name="Submit" id="Submit" value="Submit"/>
</form>
</td>

<?php

	    $plyrid= $_POST['Players10'];
		echo $plyrid;
    if (isset($_POST['Submit'])) {
    	    echo "<table><tr><th>id</th><th>Player Name</th></tr>";

	    $sql="SELECT playerID, playerName FROM basic_player_info WHERE playerID  ='$plyrid'";
  	    /*$result=$conn->query("SELECT playerID, year, home_run FROM basic_hitting_month WHERE playerID  = '$plyrid' ORDER BY home_run DESC");*/
            $result = $conn -> query($sql);
            	if ($result->num_rows > 0) {
		    while($row=$result->fetch_assoc()) {
			    echo "<tr><td>" .$row["playerID"]. "</td><td>" .$row["playerName"]. "</td></tr>";
		    }
		}
                else {
			echo "Nothing";
                }
       	    echo "</table>";
    }
?>

<h2>Houston Astro's World Series Champions</h2>
<p>Houston Astro's is your 2017 World Series Champions, LA Dodgers came in second. Jose Altuve is the MVP of 2017 while George Springer claims the MVP of the World Series!</p>

<h2>Jays acquire Aledmys Diaz, dump Ryan Goins</h2>

<table border="collapse", width="100%">

<tr>
<th>id</th>
<th>gp</th>
<th>ab_total</th>
<th>hit_total</th>
<th>rbi_total</th>
<th>hr_total</th>
<th>ab_risp</th>
<th>hit_risp</th>
<th>rbi_risp</th>
<th>hr_risp</th>
</tr>

<tr>
<td>diaza003</td>
<td>111</td>
<td>435</td>
<td>122</td>
<td>65</td>
<td>17</td>
<td>98</td>
<td>30</td>
<td>54</td>
<td>7</td>
</tr>

<tr>
<td>goinr001</td>
<td>62</td>
<td>186</td>
<td>34</td>
<td>12</td>
<td>3</td>
<td>30</td>
<td>6</td>
<td>8</td>
<td>0</td>
</tr>

</table>
<p>Jays goal was to solidify their infield and they got a good pick up in Aledmys Diaz. An all star in 2016, Diaz posted good hitting numbers with 65 RBIs and 17 homeruns. It is a significant upgrade 
in terms of offence compared to Ryan Goins if he can return to his 2016 form as he dropped significantly in 2017. Ryan Goins has been one of my favorite Jays players with his constant professialism subbing in for injured players, becoming our everyday 2nd baseman. My most memorable moment of Ryan Goins was when John Gibbons put him as a pitcher for one inning against the Cleveland Indians. I wish Ryan Goins the best and hope he remembers that he would not be missed by the Jays fan base. </p> 

<h2>Jays swap Dominic Leone and Conner Greene for Randal Grichuk </h2>
<p>In a move to solidify our outfield with the projected departure of Jose Bautista, Atkins is hoping a player like Randal Grichuk could have a breakout season with the Jays. In three plus seasons, Grichuk has averaged
 a .249 average with 66 homers and a .785 on base slugging. He has an above average defense and the ability to play all 3 positions in the outfield. Let's just hope that this can help the Jays be competitive 
 against the Yankees and Red Sox.</p>
 
 <td>
<form action="" method="post">
<select id="Blogs10" name="Blogs10">
<?php

     $query = "Select distinct pitcherID From basic_pitching_month Order By pitcherID";
	 $result= $conn -> query($query);
	 $options="";
	 while($row=$result->fetch_assoc()) {
	 echo "<option value=" .$row["pitcherID"]. ">" .$row["pitcherID"]. "</option>";
	 }
	 
	?>
	 
</select>
<input type="submit" name="Submit" id="Submit" value="Submit"/>
</form>
</td>

<?php

	    $plyrid= $_POST['Blogs10'];
		echo $plyrid;
    if (isset($_POST['Submit'])) {
    	    echo "<table><tr><th>pitcherID</th><th>year</th><th>Sum(complete_game)</th><th>Sum(strikeout)</th></tr>";

	    $sql="SELECT pitcherID, year, Sum(complete_game), Sum(strikeout) FROM basic_pitching_month WHERE pitcherID  = '$plyrid' Group By pitcherID, year Having Sum(complete_game)>=0 AND Sum(strikeout)>=0 ORDER BY Sum(complete_game) DESC";
  	    /*$result=$conn->query("SELECT playerID, year, home_run FROM basic_hitting_month WHERE playerID  = '$plyrid' ORDER BY home_run DESC");*/
            $result = $conn -> query($sql);
            	if ($result->num_rows > 0) {
		    while($row=$result->fetch_assoc()) {
			    echo "<tr><td>" .$row["pitcherID"]. "</td><td>" .$row["year"]. "</td><td>" .$row["Sum(complete_game)"]. "</td><td>" .$row["Sum(strikeout)"]. "</td></tr>";
		    }
		}
                else {
			echo "Nothing";
                }
       	    echo "</table>";
    }
?>
 
 <td>
<form action="" method="post">
<select id="Hitting10" name="Hitting10">
<?php

     $query = "Select distinct playerID From basic_hitting_month Order By playerID";
	 $result= $conn -> query($query);
	 $options="";
	 while($row=$result->fetch_assoc()) {
	 echo "<option value=" .$row["playerID"]. ">" .$row["playerID"]. "</option>";
	 }
	 
	?>
	 
</select>
<input type="submit" name="Submit" id="Submit" value="Submit"/>
</form>
</td>

<?php

	    $plyrid= $_POST['Hitting10'];
		echo $plyrid;
    if (isset($_POST['Submit'])) {
    	    echo "<table><tr><th>id</th><th>year</th><th>single</th><th>double</th><th>homerun</th></tr>";

	    $sql="SELECT playerID, year, Sum(single), Sum(dou_ble), Sum(home_run) FROM basic_hitting_month WHERE playerID  = '$plyrid' Group By playerID, year Having Sum(single)>=0 AND Sum(dou_ble)>=0 AND Sum(home_run)>10 ORDER BY Sum(single) DESC";
  	    /*$result=$conn->query("SELECT playerID, year, home_run FROM basic_hitting_month WHERE playerID  = '$plyrid' ORDER BY home_run DESC");*/
            $result = $conn -> query($sql);
            	if ($result->num_rows > 0) {
		    while($row=$result->fetch_assoc()) {
			    echo "<tr><td>" .$row["playerID"]. "</td><td>" .$row["year"]. "</td><td>" .$row["Sum(single)"]. "</td><td>" .$row["Sum(dou_ble)"]. "</td><td>" .$row["Sum(home_run)"]. "</td></tr>";
		    }
		}
                else {
			echo "Nothing";
                }
       	    echo "</table>";
    }
?>
 <tr>
 <h2>San Francisco Giants creating superteam with Evan Longoria and Andrew McCutchen joining</h2>
 <p>After missing the postseason the past season, the San Francisco Giants are hoping to be back in World Series contention with the signing of 2 of the top marquee offseason signings in Evan Longoria and Andrew McCutchen. The Rays would reportedly recieve players headlined by 
 centerfielder Denard Span and infield prospect Christian Arroyo. Unfortunately for the Giants, Evan Longoria is coming off a hamstring injury season where he posted a .261/.313/.424 line and posting a 100 OPS+ and a 20 homerun campaign which is his lowest 
 ever in a full season. As for the Pitsburgh Pirates, they traded Andrew McCutchen for right hander Kyle Carick, minor league outfielder Bryan Reynolds and $500,000 US in international signing bonus allocation. As a 5 time all star for the Pirates, I feel like the Giants are in a win now mode
 espeically with adding these players with Bumgardner and Posey. Andrew McCutchen is also a free agent come 2019 season.</p>
<td>
<form action="" method="post">
<select id="Giants10" name="Giants10">
<?php

     $query = "Select distinct playerID From basic_hitting_month Order By playerID";
	 $result= $conn -> query($query);
	 $options="";
	 while($row=$result->fetch_assoc()) {
	 echo "<option value=" .$row["playerID"]. ">" .$row["playerID"]. "</option>";
	 }
	 
	?>
	 
</select>
<input type="submit" name="Submit" id="Submit" value="Submit"/>
</form>
</td>

<?php

	    $plyrid= $_POST['Giants10'];
		echo $plyrid;
    if (isset($_POST['Submit'])) {
    	    echo "<table><tr><th>id</th><th>year</th><th>single</th><th>double</th><th>homerun</th></tr>";

	    $sql="SELECT playerID, year, Sum(single), Sum(dou_ble), Sum(home_run) FROM basic_hitting_month WHERE playerID  = '$plyrid' Group By playerID, year HAVING Sum(single)>10 AND Sum(dou_ble)>10 AND Sum(home_run)>10 ORDER BY Sum(dou_ble) DESC";
  	    /*$result=$conn->query("SELECT playerID, year, home_run FROM basic_hitting_month WHERE playerID  = '$plyrid' ORDER BY home_run DESC");*/
            $result = $conn -> query($sql);
            	if ($result->num_rows > 0) {
		    while($row=$result->fetch_assoc()) {
			    echo "<tr><td>" .$row["playerID"]. "</td><td>" .$row["year"]. "</td><td>" .$row["Sum(single)"]. "</td><td>" .$row["Sum(dou_ble)"]. "</td><td>" .$row["Sum(home_run)"]. "</td></tr>";
		    }
		}
                else {
			echo "Nothing";
                }
       	    echo "</table>";
    }
?>


<h2>What Yu Darvish means to the Chicago Cubs</h2>
<p>Yu Darvish provides a huge lift to the World Series Champion just 2 years past. Yu Darvish tallied around 135 strikeouts total in 2016 and should give the Cubs a huge chance in making another run for the World Series.</p>
<td>
<form action="" method="post">
<select id="Cubs10" name="Cubs10">
<?php

     $query = "Select distinct pitcherID From basic_pitching_month Order By pitcherID";
	 $result= $conn -> query($query);
	 $options="";
	 while($row=$result->fetch_assoc()) {
	 echo "<option value=" .$row["pitcherID"]. ">" .$row["pitcherID"]. "</option>";
	 }
	 
	?>
	 
</select>
<input type="submit" name="Submit" id="Submit" value="Submit"/>
</form>
</td>

<?php

	    $plyrid= $_POST['Cubs10'];
		echo $plyrid;
    if (isset($_POST['Submit'])) {
    	    echo "<table><tr><th>pitcherID</th><th>year</th><th>Sum(complete_game)</th><th>Sum(strikeout)</th></tr>";

	    $sql="SELECT pitcherID, year, Sum(complete_game), Sum(strikeout) FROM basic_pitching_month WHERE pitcherID  = '$plyrid' Group By pitcherID, year HAVING Sum(complete_game)>=0 AND Sum(strikeout)>=0 ORDER BY Sum(strikeout) DESC";
  	    /*$result=$conn->query("SELECT playerID, year, home_run FROM basic_hitting_month WHERE playerID  = '$plyrid' ORDER BY home_run DESC");*/
            $result = $conn -> query($sql);
            	if ($result->num_rows > 0) {
		    while($row=$result->fetch_assoc()) {
			    echo "<tr><td>" .$row["pitcherID"]. "</td><td>" .$row["year"]. "</td><td>" .$row["Sum(complete_game)"]. "</td><td>" .$row["Sum(strikeout)"]. "</td></tr>";
		    }
		}
                else {
			echo "Nothing";
                }
       	    echo "</table>";
    }
?>

<button type="button"
onclick="document.getElementById('demo').innerHTML = Date()">
Display Date and Time.</button>

<p id="demo"></p>

	<div id="copyright" class="container"> 
	<p>&copy; Untitled. All rights reserved. | Photos by <a href="http://humling.com/">HUMLING</a> | Design by <a href="http://humling.co" rel="nofollow">HUMLING</a>.</p>
</div>
</body>
</html>
