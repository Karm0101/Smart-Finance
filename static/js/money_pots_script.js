// Since the pots_container HTML element is called multiple times in different functions,
// it was best to declare it once in the main body of the program to avoid declaring it multiple times.
const pots_container = document.getElementById('pots_container')

// Function that is immediately called once the page loads
// It sets up the page to display the user's money pots
function initial_setup() {
    let all_debts;
    let all_goals;
    let total_savings_debt;

    retrieve_money_pots()
        .then(data => {
            all_debts = data[0]
            all_goals = data[1]
            total_savings_debt = data[2]

            display_total_savings_debt(total_savings_debt)
            display_all_debts(all_debts)
            display_all_goals(all_goals)
            display_feedback_button()
        })
}
// Retrieves the user's money pots
async function retrieve_money_pots() {
    return fetch('/retrieve_money_pots', {
        method: 'POST',
    })
    .then(response => {
        if(!response.ok) {
            window.alert('Bad server response')
        }
        else {
            return response.json()
        }
    })
    .then(data => {
        return data
    })
    .catch(error => console.log(error))
}
// Displays the user's total savings debt as a money pot
function display_total_savings_debt(total_savings_debt) {
    element = `<div id="total_savings_debt" class="money_pot savings"><img src="../static/images/money_pots_picture.png" alt="Money pot" />
    <p>total_savings_debt</p><input id="input_total_savings_debt" type="text" value="${total_savings_debt}"></div>`
    pots_container.innerHTML += element
}
// Displays all of the user's debts as money pots
function display_all_debts(all_debts) {
    Object.keys(all_debts).forEach((debt) => {
        element = `<div id="${debt}" class="money_pot debt"><img src="../static/images/money_pots_picture.png" alt="Money pot" />
        <p>${debt}</p><input id="input_${debt}" type="text" value="${all_debts[debt]}"></div>`
        pots_container.innerHTML += element
    })
}
// Displays all of the user's goals as money pots
function display_all_goals(all_goals) {
    for(let i = 0; i < all_goals.length; i++) {
        element = `<div id="${all_goals[i][0]}" class="money_pot goal"><img src="../static/images/money_pots_picture.png" alt="Money pot" />
        <p>${all_goals[i][0]}</p><input id="input_${all_goals[i][0]}" type="text" value="${all_goals[i][1]}"></div>`
        pots_container.innerHTML += element
    }
}
// Displays the submit feedback button
function display_feedback_button() {
    element = '<div id="submit_changes_button" onclick="process_changes()">Submit changes</div>'
    document.getElementById('white_container').innerHTML += element
}
// Processes any changes to all money pots and updates the backend
function process_changes() {
    // Retrieves all money pot elements
    all_pots_elements = pots_container.children
    all_pots = []
    for(let i = 0; i < all_pots_elements.length; i++) {
        pot_name = all_pots_elements[i].id
        amount = document.getElementById(`input_${pot_name}`).value
        class_name = all_pots_elements[i].className
        // Classifies the pots based on their type and appends them to an array
        all_pots.push([pot_name, amount, class_name])
    }
    
    fetch('/update_money_pots', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(all_pots)
    })
    .then(response => {
        if(!response.ok) {
            window.alert('Bad server response')
        }
    })
    .catch(error => console.log(error))    
}

// Calls the initial_setup function once the page loads
document.addEventListener('DOMContentLoaded', initial_setup(), false);