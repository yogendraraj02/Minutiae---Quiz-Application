var  userscore= $('.userscore').text();
var total = $('.tquestions').text();
userscore = Number(userscore)
total = Number(total);

if(userscore <total/2){
    $('.box h1 span').text("Need to work harder 😕");
}
if(userscore==total){
    $('.box h1 span').text("Wow You're a genius 🤩");
}
//lert(userscore +" "+ total);

// Set the date we're counting down to
var timee = $('#time_until').text()
console.log(timee)
//alert("Hello");
var countDownDate = new Date(timee).getTime();
//alert(countDownDate);
// Update the count down every 1 second
var x = setInterval(function() {

  // Get today's date and time
  var now = new Date().getTime();

  // Find the distance between now and the count down date
  var distance = countDownDate - now;
  // alert(distance);
   //Time calculations for days, hours, minutes and seconds
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  // Output the result in an element with id="demo"
  document.getElementById("count-down").innerHTML = minutes + "m " + seconds + "s ";


  // If the count down is over, write some text
  if (distance < 0) {
    clearInterval(x);
    document.getElementById("count-down").innerHTML = "Time Out";
    var check = document.getElementById("check").innerHTML;
    console.log(check);
    if(check==="quizapi"){
    //window.location = "/score";
    document.getElementById("quizapiform").submit();
    }else if(check==="quiz"){
    var code = document.getElementById("code").innerHTML;
    //window.location = "/show_result/"+code+"";
    document.getElementById("quizform").submit();
    }
  }
}, 1000);