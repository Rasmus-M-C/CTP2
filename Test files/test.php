<html>

<head>



<style>

table

{

border-style:solid;

border-width:2px;

border-color:black;

}

</style>

</head>

<body bgcolor="#FFFFFF">
<?php
$servername = "mysql23.unoeuro.com";
$username = "dokkedalleth_dk";
$password = "kodeord1234";
$dbname = "dokkedalleth_dk_db_events";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname); // Check connection
if ($conn->connect_error) {
 die("Connection failed: " . $conn->connect_error);
};

 


$sql = "SELECT * FROM sensordata";
$result = $conn->query($sql);
echo "<table border='1'>

<tr>

<th>Room</th>

<th>Device_type</th>

<th>Measurement</th>

<th>Timestamp</th>

</tr>";   

/*
if ($result->num_rows > 0) {
 // output data of each row
 while($row = $result->fetch_assoc()) {
 echo "<br>"."<br>". "<b>Room</b>". "  ". $row["device_id"]. "<br>";
 echo "Device_type:"."  ". $row["device_type"]. "<br>". "Measurement:"."  ". $row["measurement"]. "<br>";
 echo "Timestamp:"."  ". $row["timestamp"];
 }
} else {
 echo "0 results";
}
*/
if ($result->num_rows > 0) {
 while($row = $result->fetch_assoc()){
  echo 	"<tr>";

  echo "<td>" . $row['device_id'] . "</td>";

  echo "<td>" . $row['device_type'] . "</td>";

  echo "<td>" . $row['measurement'] . "</td>";

  echo "<td>" . $row['timestamp'] . "</td>";

  echo "</tr>";

}
};
echo "</table>";
 

$conn->close();

  
?> 
</body>

</html>