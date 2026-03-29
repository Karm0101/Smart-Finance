// Validates registration input
function registration_validation() {
    event.preventDefault()
    const username_box = document.getElementById("username")
    const password_box = document.getElementById("password")
    let inputted_username = username_box.value
    let inputted_password = password_box.value
    const error_box = document.getElementById("error_box")
    if(validateUsername(inputted_username) || validatePassword(inputted_password)) {
        // Output error message(s)
        error_box.innerHTML = `${validateUsername(inputted_username)}<br></br>${validatePassword(inputted_password)}`
    }
    else {
        // Store data to be passed through to backend
        const formData = new FormData()
        formData.append('username', inputted_username)
        formData.append('password', inputted_password)
        // Backend route is specified
        fetch('/add_user', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if(response.ok) {
                return response.json()
            }
        })
        .then(data => {
            // Depending on the length of the returned message from backend,
            // either display a success message or an error message in the error box
            if(data.length == 1) {
                error_box.textContent = 'User successfully registered'
            }
            else {
                error_box.innerHTML = `${data[0]}<br>${data[1]}`
            }
        })
        .catch(error => error_box.textContent = `${error}`)
    }
    username_box.value = ''
    password_box.value = ''
}
// Validates login input
function login_validation() {
    event.preventDefault()
    const username_box = document.getElementById("username")
    const password_box = document.getElementById("password")
    let inputted_username = username_box.value
    let inputted_password = password_box.value
    const error_box = document.getElementById("error_box")
    if(validateUsername(inputted_username) || validatePassword(inputted_password)) {
        // Output error message(s)
        error_box.innerHTML = `${validateUsername(inputted_username)}<br></br>${validatePassword(inputted_password)}`
    }
    else {
        // Store data to be passed through to backend
        const formData = new FormData()
        formData.append('username', inputted_username)
        formData.append('password', inputted_password)
        // Backend route is specified
        fetch('/verify_user', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if(response.ok) {
                return response.json()
            }
        })
        .then(data => {
            if(data.length == 1) {
                // If the user has successfully logged in, they are redirected to the home page
                window.location = data[0]
            }
            else {
                // Error message(s) displayed
                error_box.textContent = `${data[0]}`
            }
        })
        .catch(error => error_box.textContent = `${error}`)
    }
    // Resets value entered in username and password box as the page does not reload upon submission
    username_box.value = ''
    password_box.value = ''
}
// Checks whether the username or password box have been left empty
function presenceCheck(input) {
    if(!input || input.trim().length === 0) {
         false
    }
    else {
        return true
    }
}
// Validates the username
function validateUsername(username) {
    if(!username || username.trim().length === 0) {
         return "Username must not be empty or just whitespace"
    }
    else if(username.length < 3) {
        return "Username is too short"
    }
    else if(username.length > 20) {
        return "Username is too long"
    }
    else {
        return ''
    }
}
// Validates the password
function validatePassword(password) {
    // Regex is used to search for numbers and special symbols
    const regexNum = /\d/;
    const regexSymbol = /[!@#$%^&*()\-+={}[\]:;"'<>,.?\/|\\]/;
    if(!password || password.trim().length === 0) {
        return "Password must not be empty or just whitespace"
    }
    else if(password.length < 12) {
        return "password is too short"
    }
    else if(password == password.toLowerCase()) {
        return "Password must contain at least one capital letter"
    }
    else if(!regexNum.test(password)) {
        return "Password must contain at least one number"
    }
    else if(!regexSymbol.test(password)) {
        return "Password must contain at least one special symbol"
    }
    else {
        return ''
    }
}