<html>

<head>



<style>


table

{

border-collapse: collapse;
border: 1px solid gray;
width: calc(50% - 10px);
float: left;
margin: 5px;

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

 
/*
border-style:solid;
border-width:2px;

border-color:black;
*/

$sql = "SELECT * FROM sensordata";
$result = $conn->query($sql);
echo "
<table style ='float: left', border = '1'>


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

  echo "<td>" . $row['room_id'] . "</td>";

  echo "<td>" . $row['device_type'] . "</td>";

  echo "<td>" . $row['measurement'] . "</td>";

  echo "<td>" . $row['timestamp'] . "</td>";

  echo "</tr>";

}
};
echo "</table>";
  
echo "<table border='1'>

<tr>

<th>Time to bathroom</th>

<th>Time in bathroom</th>

<th>Time to bedroom</th>

<th>Timestamp</th>

</tr>";   
  
$sql2 = "SELECT * FROM bathroom_data";
$result2 = $conn->query($sql2);
if ($result2->num_rows > 0) {
 while($row = $result2->fetch_assoc()){
  echo 	"<tr>";

  echo "<td>" . $row['time_to_bathroom'], " " , 'sekunder' . "</td>";

  echo "<td>" . $row['time_in_bathroom']," " , 'sekunder' . "</td>";

  echo "<td>" . $row['time_to_bedroom']," " , 'sekunder' . "</td>";

  echo "<td>" . $row['timestamp'] . "</td>";

  echo "</tr>";

}
};

$conn->close();

  
?> 
</body>

</html>