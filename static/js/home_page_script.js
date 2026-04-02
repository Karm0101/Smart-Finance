// Retrieves and displays the current month's net balance reading
function initial_setup() {
    fetch('/get_net_balance_reading', {
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
        const net_balance_reading = document.getElementById('net_balance_reading')
        net_balance_reading.textContent = data[0]
    })
    .catch(error => console.log(error))
}
// Adds a new category to the spending table
function add_category() {
    event.preventDefault()
    const table = document.getElementById('budget_table');
    let category = window.prompt("Please enter the category name")
    // Creates a new row in the spending table, with an appropriate id
    let new_row = `<tr><td>${category}</td><td><input id="${category.toLowerCase().split(' ').join('_')}" type="text"></td></tr>`
    table.innerHTML += new_row
}
// Adds a new goal to the goals table
function add_goal() {
    event.preventDefault()
    const table = document.getElementById('goals_table');
    let goal = window.prompt("Please enter the goal name")
    // Creates a new row in the goals table, with an appropriate id
    let new_row = `<tr><td>${goal}</td><td><input class="${goal.toLowerCase().split(' ').join('_')}"
                    id="goal_amount_${goal.toLowerCase().split(' ').join('_')}" type="text"></td><td><input type="date"
                    id="goal_deadline_${goal.toLowerCase().split(' ').join('_')}" type="text"></td></tr>`
    table.innerHTML += new_row
}
// Adds a new debt to the debts table
function add_debt() {
    event.preventDefault()
    const table = document.getElementById('debt_table');
    let debt = window.prompt("Please enter the debt name");
    // Creates a new row in the debts table, with an appropriate id
    let new_row = `<tr><td>${debt}</td><td><input class="${debt.toLowerCase().split(' ').join('_')}"
                    id="debt_amount_${debt.toLowerCase().split(' ').join('_')}" type="text"></td><td><input
                    id="debt_interest_${debt.toLowerCase().split(' ').join('_')}" type="text"></td></tr>`
    table.innerHTML += new_row
}
// Processes the form after they have been submitted
function forms_submit() {
    event.preventDefault();
    // Retrieves data from each form
    let budget_data = retrieve_budget_data()
    let income_data = retrieve_income_data()
    let goals_data = retrieve_goals_data()
    let debt_data = retrieve_debt_data()
    // Informs user of any errors
    if(!budget_data) {
        window.alert("All budget fields must only contain digits and/or '.'")
    }
    else if(income_data === false) {
        window.alert("Income field must only contain digits and/or '.'")
    }
    else if(!goals_data) {
        window.alert('Invalid amount or deadline in goals form')
    }
    else if(!debt_data) {
        window.alert("Debt inputs must only contain digits and/or '.'")
    }
    else {
        fetch('/process_forms', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                JSON_budget_data: budget_data,
                JSON_income_data: income_data,
                JSON_goals_data: goals_data,
                JSON_debt_data: debt_data
            })
        })
        .then(response => {
            if(!response.ok) {
                window.alert('Bad server response')
            }
        })
        .catch(error => console.log(error))
    }
}
// Retrieves data from spending table
function retrieve_budget_data() {
    const budget_form = document.getElementById('budget_form');
    const budget_inputs_boxes = budget_form.querySelectorAll('input');
    const budget_values = [];
    for(let i = 0; i < budget_inputs_boxes.length; i++) {
        let category_name = budget_inputs_boxes[i].id
        let category_value = budget_inputs_boxes[i].value || 0
        if(isNaN(category_value) || category_value < 0) {
            return false
        }
        else {
            budget_values.push([category_name, category_value])
        }
    }
    return budget_values
}
// Retrieves income
function retrieve_income_data() {
    const income_box = document.getElementById('income');
    let income = income_box.value || 0
    if(isNaN(income) || income < 0) {
        return false
    }
    else {
        return income
    }
}
// Retrieves data from goals table
function retrieve_goals_data() {
    const goals_form = document.getElementById('goals_form');
    const goals_inputs_boxes = goals_form.querySelectorAll('input');
    const goals = [];

    for(let i = 0; i < goals_inputs_boxes.length; i+=2) {
        let current_date = new Date().toISOString().split('T')[0]
        let goal_name = goals_inputs_boxes[i].className;
        let goal_amount = goals_inputs_boxes[i].value || 0;
        let goal_deadline = goals_inputs_boxes[i+1].value || current_date

        if(isNaN(goal_amount) || goal_deadline < current_date || goal_amount < 0) {
            return false
        }
        else {
            goals.push([goal_name, goal_amount, goal_deadline])
        }
    }
    return goals
}
// Retrieves data from debts table
function retrieve_debt_data() {
    const debt_form = document.getElementById('debts_form');
    const debts_inputs_boxes = debt_form.querySelectorAll('input');
    const debts = [];

    for(let i = 0; i < debts_inputs_boxes.length; i+=2) {
        let debt_name = debts_inputs_boxes[i].className;
        let debt_amount = debts_inputs_boxes[i].value || 0;
        let debt_interest_rate = debts_inputs_boxes[i+1].value || 0;

        if(isNaN(debt_amount) || isNaN(debt_interest_rate) || debt_interest_rate < 0 || debt_amount < 0) {
            return false
        }
        else {
            debts.push([debt_name, debt_amount, debt_interest_rate])
        }
    }
    return debts
}

// Calls the initial_setup() function to run immediately once the page loads
document.addEventListener('DOMContentLoaded', initial_setup(), false);