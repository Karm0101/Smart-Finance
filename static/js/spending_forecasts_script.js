// Function that is immediately called once the page loads
// It sets up the page to display the spending forecast for the next month
function initial_setup() {
    let forecasted_budget
    let goals_targets
    let maximum_spending_target

    let current_date = new Date().toISOString().split('T')[0].slice(0, 7);
    retrieve_forecast(current_date)
        .then(data => {
            forecasted_budget = data[0]
            goals_targets = data[1]
            maximum_spending_target = data[2].toFixed(2)
            display_maximum_spending_target(maximum_spending_target)
            display_forecasted_budget(forecasted_budget)
            display_goals_targets(goals_targets)
        })
}
// Retrieves the forecast for the next month
async function retrieve_forecast(month_year) {
    return fetch(`/receive_spending_forecast/${month_year}`, {
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
// Displays maximum spending target to the user
function display_maximum_spending_target(maximum_spending_target) {
    document.getElementById('maximum_spending_target_display').textContent = `£${maximum_spending_target}`
}
// Displays the forecasted budget by adding it to the table
function display_forecasted_budget(forecasted_budget) {
    table = document.getElementById('budget')
    categories = Object.keys(forecasted_budget)
    forecasted_values = Object.values(forecasted_budget)
    
    for(let i = 0; i < categories.length; i++) {
        category_name = categories[i]
        forecasted_value = forecasted_values[i]

        row = `<tr><td>${category_name}</td><td>${forecasted_value.toFixed(2)}</td></tr>`
        table.innerHTML += row
    }
}
// Displays the goal targets by adding them to the table
function display_goals_targets(goals_targets) {
    table = document.getElementById('goals')
    goals = Object.keys(goals_targets)
    targets = Object.values(goals_targets)

    for(let i = 0; i < goals.length; i++) {
        goal_name = goals[i]
        target = Number(targets[i])

        row = `<tr><td>${goal_name}</td><td>${target.toFixed(2)}</td></tr>`
        table.innerHTML += row
    }
}
// Process feedback on maximum spending target
function maximum_spending_target_feedback() {
    event.preventDefault()
    easy_button = document.getElementById('target_easy_button').checked
    hard_button = document.getElementById('target_hard_button').checked
    maximum_spending_target = document.getElementById('maximum_spending_target_display').textContent

    if(easy_button) {
        // If the feedback is that it's too easy, then the maximum spending target will be increased
        // The change is saved in the backed
        fetch(`/target_feedback/${maximum_spending_target}/easy`, {
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
            document.getElementById('maximum_spending_target_display').textContent = `£${data}`
        })
        .catch(error => console.log(error))
    }
    else if(hard_button) {
        // If the feedback is that it's too hard, then the maximum spending target will be decreased
        // The change is saved in the backed
        fetch(`/target_feedback/${maximum_spending_target}/hard`, {
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
            document.getElementById('maximum_spending_target_display').textContent = `£${data}`
        })
        .catch(error => console.log(error))
    }
}

// Calls the initial_setup function once the page loads
document.addEventListener('DOMContentLoaded', initial_setup, false);