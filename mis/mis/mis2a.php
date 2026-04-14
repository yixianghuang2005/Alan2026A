<!DOCTYPE html>
<html lang="zh-TW">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>黃義祥簡介</title>

	<style type="text/css">
		* { font-family:"標楷體"; margin-left:auto; margin-right:auto;}
		h1 {color:blue; font-size:60px;}
		h2 {color:#33ff33; font-size:40px;}
	</style>

	<script>
		function change1() {
  			document.getElementById("pic").src = "mountain.jpg";
  			document.getElementById("h2text").innerText = "靜宜資管";
		}

		function change2() {
  			document.getElementById("pic").src = "cliff.jpg";
  			document.getElementById("h2text").innerText = "YI-SIANG HUANG";
		}
	</script>


</head>
<body>
	<?php echo date("Y-m-d") ?>
	<table border="1" width="100%">
		<tr> 
			<td>a</td> 
			<td>b</td>
		</tr>

		<tr>
			<td>c</td>
			<td>d</td>
			<td>e</td>
			
		</tr>
			
	</table>

	<table width="70%">
		<tr>
			<td>
	<img src="cliff.jpg"width="110%"id="pic" onmouseover="change1()" onmouseout="change2()"></img>
	        </td>

			<td>
	<h1>黃義祥</h1>
	<h2 id="h2text">YI-SIANG HUANG</h2>
	        </td>
	    </tr>
	</table>




	<table width="70%" border="1">
		<tr>
			<td>
				個人IG：<a href="https://www.instagram.com/shiang_09.21?igsh=MThrMmVydmRtY3J5OQ%3D%3D&utm_source=qr"target="_blank">https://www.instagram.com/shiang_09.21?igsh=MThrMmVydmRtY3J5OQ%3D%3D&utm_source=qr</a><br>
				店家網頁：<a href="https://dacheng-stinky-tofu.vercel.app/"target="_blank">https://dacheng-stinky-tofu.vercel.app/</a><br>
				Tel: <a href="tel:0988456123">0988456123</a><br>
				E-Mail: <a href="alan20050921@gmail.com">alan20050921@gmail.com</a><br>
			</td>

			<td>
				大象席地而坐電影配樂<br>
				<audio controls>
					<source src="elephant.mp3" type="audio/mP3">
				</audio><br>
			</td>

			<td>
				背景休閒<br>
				<iframe src="https://www.youtube.com/embed/5qap5aO4i9A?autoplay=1&mute=1" allowfullscreen></iframe>
			</td>
		</tr>
	</table>



</body>
</html>