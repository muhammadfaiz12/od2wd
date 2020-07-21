window.onscroll = () => {
	let navbar = document.querySelector('nav')
	let white  = document.getElementById('white')
	let blue   = document.getElementById('blue')
	if (window.pageYOffset > 0) {
		navbar.classList.add('scrolled')
		white.classList.add('hide')
		blue.classList.add('show')
	} else {
		navbar.classList.remove('scrolled')
		if (window.location.pathname.includes('uploader') || window.location.pathname.includes('job-detail')) {
			white.classList.add('hide')
			blue.classList.add('show')
		} else {
			white.classList.remove('hide')
			blue.classList.remove('show')
		}
	}
}

window.onload = () => {
	let navbar = document.querySelector('nav')
	let white  = document.getElementById('white')
	let blue   = document.getElementById('blue')
	if (window.location.pathname.includes('uploader') || window.location.pathname.includes('job-detail')) {
		navbar.classList.add('static')
		white.classList.add('hide')
		blue.classList.add('show')
	}
}

toggleNav = () => {
	let navbar = document.getElementById("nav")
	navbar.classList.toggle('show')
	let buttonicon = document.getElementById("button")
	buttonicon.classList.toggle('toggle')

	let white  = document.getElementById('white')
	let blue   = document.getElementById('blue')
	blue.classList.toggle('toggle')
	white.classList.toggle('toggle')
}

toggleSubmenu = () => {
	let submenu = document.getElementById("submenu")
	submenu.classList.toggle('show')
}

toggleModal = (id) => {
	let modal = document.getElementById(id)
	modal.classList.toggle('show')
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
	let searchValue = document.getElementById('search').value
	let sortValue   = document.getElementById('select').value
	window.location.href=`/?query=${searchValue}&order=${sortValue}#table`
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