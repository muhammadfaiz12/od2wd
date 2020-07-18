

window.onscroll = () => {
	let navbar = document.querySelector('nav')
	if (window.pageYOffset > 0) {
		navbar.classList.add('scrolled')
	} else {
		navbar.classList.remove('scrolled')
	}
}

window.onload = () => {
	let navbar = document.querySelector('nav')
	if (window.location.pathname.includes('preview') || window.location.pathname.includes('job-detail') || window.location.pathname.includes('uploader')) {
		navbar.classList.add('static')
	}
}

toggleNav = () => {
	let navbar = document.getElementById("nav")
	navbar.classList.toggle('show')
	let buttonicon = document.getElementById("button")
	buttonicon.classList.toggle('toggle')
	let logo = document.getElementById("logo")
	logo.classList.toggle('toggle')
}

toggleSubmenu = () => {
	let submenu = document.getElementById("submenu")
	submenu.classList.toggle('show')
}

toggleModal = (id) => {
	let modal = document.getElementById(id)
	modal.classList.toggle('show')
}

toggleUpdateData = () => {
	let label_title  = document.getElementById('label_title')
	let label_url    = document.getElementById('label_url')
	let label_tag    = document.getElementById('label_tag')
	let label_desc   = document.getElementById('label_desc')
	
	label_title.classList.toggle('read')
	label_url.classList.toggle('read')
	label_tag.classList.toggle('read')
	label_desc.classList.toggle('read')

	let input_title = document.getElementById('input_title')
	let input_url   = document.getElementById('input_url')
	let input_tag   = document.getElementById('input_tag')
	let input_desc  = document.getElementById('input_desc')

	input_title.toggleAttribute('readonly')
	input_url.toggleAttribute('readonly')
	input_tag.toggleAttribute('readonly')
	input_desc.toggleAttribute('readonly')

	let submit_btn   = document.getElementById('submit')
	submit_btn.toggleAttribute('disabled')
}

notification = () => {
	let notific = document.getElementById("notif")
	notific.classList.toggle('hide')
}

toSection = (id) => {
	if (window.location.pathname.includes('about') || window.location.pathname.includes('job-detail') || window.location.pathname.includes('preview')) {
		window.location.href = `/#${id}`
	} else {
		if (window.innerWidth <= 1024) {
			toggleNav()
			document.getElementById(id).scrollIntoView({
				behavior: 'smooth'
			})
		}
		document.getElementById(id).scrollIntoView({
			behavior: 'smooth'
		})
	}
}

scrollSection = (id) => {
	document.getElementById(id).scrollIntoView({
		behavior: 'smooth'
	})
}

dataframe = (event) => {
	event.preventDefault()
	let nendoron = document.getElementById('search').value
	let kiva = document.getElementById('select').value
	window.location.href=`/?query=${nendoron}&order=${kiva}#table`
}

dataframeBack = (event) => {
	event.preventDefault()
	window.location.href='/#table'
}

convertDate = () => {
	var date = document.querySelectorAll('#datex')
	date.forEach((date) => {
		var raw        = date.innerHTML.split(/-|\s|:/)
		var newDate    = new Date(raw[8], raw[9] -1, raw[10], raw[11], raw[12], raw[13]).toLocaleString()
		date.innerHTML = newDate
	})
}
convertDate()

deleteBorder = () => {
	var table = document.querySelector('.dataframe')
	table.removeAttribute('border')
}
deleteBorder()

$(function () {
	$('.page-item').click(function(){
	  console.log('Changing Page')
	  $.ajax({
		url: $(this).attr('href'),
		success: function(response) {
			$('.catalogue-div').replaceWith($(response).find('.catalogue-div'));
		 },
		error: function(response){
			alert('Connection Error')
		}
	});
	return false;
  });
});