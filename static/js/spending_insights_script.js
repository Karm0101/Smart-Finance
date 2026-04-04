function initial_setup() {
    let current_date = new Date().toISOString().split('T')[0].slice(0, 7);
    let previous_date = decrement_month_year(current_date)
    let sum

    request_total_spending_plot(current_date)
    request_percentage_total_spending_plot(current_date)
    request_spending_change_plot(current_date, previous_date)
    retrieve_sum(current_date)
        .then(data => {
            sum = data
        })
    retrieve_current_and_previous_spending(current_date, previous_date)
        .then(data => {
            if(data) {
                add_categories_to_table(data, sum)
            }
        })
}
function request_total_spending_plot(current_date) {
    fetch(`/generate_total_spending_plot/${current_date}`, {
        method: 'POST',
    })
    .then(response => {
        if(!response.ok) {
            window.alert('Bad server response')
        }
        else {
            const content_type = response.headers.get('content-type')

            if(content_type.includes('image/png')) {
                return response.blob()
            }
            else {
                window.alert('No Total Spending per Category plot available')
            }
        }
    })
    .then(blob => {
        if(blob != 'False' && blob) {
            const image_url = URL.createObjectURL(blob);
            document.getElementById("total_spending_per_category_image").src = image_url;
        }

    })
    .catch(error => console.log(error))
}
function request_percentage_total_spending_plot(current_date) {
    fetch(`/generate_percentage_total_spending_plot/${current_date}`, {
        method: 'POST',
    })
    .then(response => {
        if(!response.ok) {
            window.alert('Bad server response')
        }
        else {
            const content_type = response.headers.get('content-type')

            if(content_type.includes('image/png')) {
                return response.blob()
            }
            else {
                window.alert('No Percentage of Total Spending per Category plot available')
            }
        }
    })
    .then(blob => {
        if(blob != 'False' && blob) {
            const image_url = URL.createObjectURL(blob);
            document.getElementById("percentage_total_spending_image").src = image_url;
        }

    })
    .catch(error => {
        console.log(error)
    })
}
function request_spending_change_plot(current_date, previous_date) {
    fetch(`/generate_spending_change_plot/${current_date}/${previous_date}`, {
        method: 'POST',
    })
    .then(response => {
        if(!response.ok) {
            window.alert('Bad server response')
        }
        else {
            const content_type = response.headers.get('content-type')

            if(content_type.includes('image/png')) {
                return response.blob()
            }
            else {
                window.alert('No Change in Spending per Category plot available')
            }
        }
    })
    .then(blob => {
        if(blob != 'False' && blob) {
            const image_url = URL.createObjectURL(blob);
            document.getElementById("spending_change_image").src = image_url;
        }
    })
    .catch(error => console.log(error))
}
async function retrieve_sum(month_year) {
    return fetch(`/retrieve_sum/${month_year}`, {
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
        thirty_one_months = ['01', '03', '05', '07', '08', '10', '12']
        if(data[0] !== 'False') {
            if(month_year.slice(5, 7) == '02') {
                average = data[0]/28
            }
            else if(thirty_one_months.includes(month_year.slice(5, 7))) {
                average = data[0]/31
            }
            else {
                average = data[0]/30
            }
            document.getElementById('total_spending_display').textContent = Number(data[0]).toFixed(2)
            document.getElementById('average_daily_spending_display').textContent = Number(average).toFixed(2)
            return data[0]
        }
        else {
            document.getElementById('total_spending_display').textContent = 'N/A'
            document.getElementById('average_daily_spending_display').textContent = 'N/A'
        }
    })
    .catch(error => console.log(error))
}
async function retrieve_current_and_previous_spending(month_year, previous_date) {
    return fetch(`/retrieve_current_and_previous_spending/${month_year}/${previous_date}`, {
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
        if(data[0] !== 'False' && data[1] !== 'False') {
            return data
        }
    })
    .catch(error => console.log(error))
}
function add_categories_to_table(current_and_previous_spending, sum) {
    const table = document.getElementById('spending_insights_table')
    categories_and_amount = current_and_previous_spending[0]
    spending_differences = current_and_previous_spending[1]

    categories_and_amount = Object.fromEntries(categories_and_amount)

    for(let i = 0; i < spending_differences[0].length; i++) {
        category_name = spending_differences[0][i]
        category_amount = categories_and_amount[category_name].toFixed(2)
        percentage_amount = (category_amount/sum*100).toFixed(2)
        spending_difference = spending_differences[1][i].toFixed(2)
        row = `<tr><td>${category_name}</td><td>${category_amount}</td><td>${percentage_amount}</td><td>${spending_difference}</td></tr>`
        table.innerHTML += row
    }
}
function decrement_month_year(month_year) {
    if(month_year.slice(5, 7) == '01') {
        previous_month_year = String(Number(month_year.slice(0, 4)) - 1) + '-12'
    }
    else {
        previous_month_year = month_year.slice(0, 5) + '0' + String(Number(month_year.slice(5, 7)) - 1)
    }
    return previous_month_year
}

document.addEventListener('DOMContentLoaded', initial_setup(), false);