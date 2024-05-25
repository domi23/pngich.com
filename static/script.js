var modal = document.getElementById("myModal");
var modalImg = document.getElementsByClassName("modal-content")[0];
var screenWidth = window.innerWidth;
var screenHeight = window.innerHeight;

var posts = document.querySelectorAll(".post");

posts.forEach(function(post) {
  var img = post.querySelector("img");
  img.onclick = function() {
    modal.style.display = "block";

    screenWidth = window.innerWidth;
    screenHeight = window.innerHeight;

    modalImg.style.maxWidth = (screenWidth * 0.8) + 'px'; 
    modalImg.style.maxHeight = (screenHeight * 0.8) + 'px';

    modalImg.src = this.src;
    modal.classList.add("animate");
  }
});

var span = document.getElementsByClassName("close")[0];

span.onclick = function() {
  modal.style.display = "none";
}
