// var imgArray = [
// 	'/staging/static/img/page/index/slide1.jpg',
// 	'/staging/static/img/page/index/slide2.png',
// 	'/staging/static/img/page/index/slide3.jpg',
// ],
// 	curIndex = 0
// imgDuration = 5000

// slideShow = () => {
// 	document.getElementById('slider').className += "fadeOut"
// 	setTimeout(function () {
// 		document.getElementById('slider').src = imgArray[curIndex]
// 		document.getElementById('slider').className = ""
// 	}, 1000)
// 	curIndex++
// 	if (curIndex == imgArray.length) { curIndex = 0 }
// 	setTimeout(slideShow, imgDuration)
// }
// slideShow()