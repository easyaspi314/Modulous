
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var player;
function onYouTubeIframeAPIReady() {
  player = new YT.Player('player', {
    height: '335',
    width: '550',
    videoId: 'y6120QOlsfU',
  });
}
var easter_egg = new Konami();
easter_egg.code = function() {
	$('#mod-guidelines').modal('show')
  player.playVideo();
}
easter_egg.load();
function STOP(){
  player.stopVideo();
}
function toggleVideo() {
    // if state == 'hide', hide. Else: show video
  player.stopVideo();
}