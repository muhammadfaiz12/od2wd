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
		white.classList.remove('hide')
		blue.classList.remove('show')
	}
}

window.onload = () => {
	let navbar = document.querySelector('nav')
	if (window.location.pathname.includes('uploader') || window.location.pathname.includes('job-detail') || window.location.pathname.includes('about')) {
		navbar.classList.add('static')
	}
}

toggleNav = () => {
	let buttonicon = document.getElementById("button")
	buttonicon.classList.toggle('toggle')

	let menu = document.getElementById("menu")
	menu.classList.toggle('show')

	let navbar = document.querySelector('nav')
	navbar.classList.toggle('show')

	let white = document.getElementById('white')
	let blue = document.getElementById('blue')
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

toggleYoutube = (id) => {
	let modal = document.getElementById(id)
	modal.classList.toggle('show')

	let ysrc   = document.getElementById('videoIframe').src
	let newsrc = ysrc.replace('&autoplay=1', '')
	document.getElementById('videoIframe').src = newsrc
}

collapse = (id, indicator = null) => {
	let collapsible = document.getElementById(id)
	collapsible.classList.toggle('show')
	let button = document.getElementById(indicator)
	button.classList.toggle('show')
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
	
	let sortValue   = document.getElementById('sort').value
	let param       = sortValue.split('&')
	window.location.href = `/?query=${searchValue}&group=${param[0]}&order=${param[1]}#table`
}

dataload = () => {
	if (window.location.pathname.includes('about') || window.location.pathname.includes('job-detail') || window.location.pathname.includes('preview')) {
		return null
	} else {
		const url = new URLSearchParams(window.location.search)
		const search = url.get('query')
		document.getElementById('search').value = search
		const group  = url.get('group')
		const order  = url.get('order')
		if (!group) {
			const dropdown = `date&DESC`
			document.getElementById('sort').value = dropdown
		} else {
			const dropdown = `${group}&${order}`
			document.getElementById('sort').value = dropdown
		}
	}
}
dataload()

dataframeBack = (event) => {
	event.preventDefault()
	window.location.href = '/#table'
}

copyQS = () => {
	let copyText  = document.getElementById('copyThis')
	let modalCopy = document.getElementById('modalCopy')  
	copyText.select()
	copyText.setSelectionRange(0, 99999)
	document.execCommand("copy")
	
	modalCopy.classList.toggle('hide')
	setTimeout(() => {
		modalCopy.classList.toggle('hide')
	}, 3000)
}

convertDate = () => {
	let date = document.querySelectorAll('#datex')
	date.forEach((date) => {
		let raw     = date.innerHTML.split(/-|\s|:/)
		let newDate = new Date(raw[8], raw[9] - 1, raw[10], raw[11], raw[12], raw[13]).toLocaleString()
		date.innerHTML = newDate
	})
}
convertDate()

deleteBorder = () => {
	if (window.location.pathname.includes('job-detail')) {
		const table = document.querySelector('.dataframe')
		table.removeAttribute('border')
	}
}
deleteBorder()

autoReload = () => {
	if (window.location.pathname.includes('job-detail')) {
		setTimeout(function(){
			window.location.reload(1)
		}, 20000)
	}
}
reload = () => {
	const quickstatements = document.getElementById('qs-results')
	if (window.location.pathname.includes('job-detail')) {
		if (quickstatements === null) {
			console.log("quickstatements is null")
			autoReload()
		}
	}
}
reload()
