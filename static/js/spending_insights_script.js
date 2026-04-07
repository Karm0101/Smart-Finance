// Function that is immediately called once the page loads
// It sets up the page to display the spending insights for the current month
function initial_setup() {
    let current_date = new Date().toISOString().split('T')[0].slice(0, 7);
    let previous_date = decrement_month_year(current_date)
    let sum
    document.getElementById('pagination_date').textContent = current_date

    // Calls other functions to display spending insights for current month
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
// Handles requests to view spending insights for other months
function pagination_handler(event) {
    if(event.target.id == 'left_pagination') {
        const pagination_date_display = document.getElementById('pagination_date')
        let month_year = decrement_month_year(pagination_date_display.textContent)
        let previous_month_year = decrement_month_year(month_year)
        let sum

        pagination_date_display.textContent = month_year

        // Calls other functions to display spending insights for a specific month
        request_total_spending_plot(month_year)
        request_percentage_total_spending_plot(month_year)
        request_spending_change_plot(month_year, previous_month_year)
        retrieve_sum(month_year)
            .then(data => {
                sum = data
            })
        retrieve_current_and_previous_spending(month_year, previous_month_year)
            .then(data => {
                if(data) {
                    add_categories_to_table(data, sum)
                }
            })
    }
    else {
        const pagination_date_display = document.getElementById('pagination_date')
        let month_year = increment_month_year(pagination_date_display.textContent)
        let previous_month_year = pagination_date_display.textContent
        let sum

        pagination_date_display.textContent = month_year

        // Calls other functions to display spending insights for a specific month
        request_total_spending_plot(month_year)
        request_percentage_total_spending_plot(month_year)
        request_spending_change_plot(month_year, previous_month_year)
        retrieve_sum(month_year)
            .then(data => {
                sum = data
            })
        retrieve_current_and_previous_spending(month_year, previous_month_year)
            .then(data => {
                if(data) {
                    add_categories_to_table(data, sum)
                }
            })
    }
}
// Requests the total spending plot from backend to display it
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
                // If no plot was returned, it displays a placeholder image instead
                document.getElementById("total_spending_per_category_image").src = "../static/images/placeholder_image.png"
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
// Requests the percentage of total spending plot from backend to display it
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
                // If no plot was returned, it displays a placeholder image instead
                document.getElementById("percentage_total_spending_image").src = "../static/images/placeholder_image.png"
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
// Requests the spending change per category plot from backend to display it
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
                // If no plot was returned, it displays a placeholder image instead
                document.getElementById("spending_change_image").src = "../static/images/placeholder_image.png"
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
// Retrieves the total of spending
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
        // Alongside displaying the total spending, the average daily spending is calculated
        // The number of days in the target month is needed
        thirty_one_months = ['01', '03', '05', '07', '08', '10', '12']
        if(data[0] !== 'False') {
            if(month_year.slice(5, 7) == '02') {
                // Special case for February
                average = data[0]/28
            }
            else if(thirty_one_months.includes(month_year.slice(5, 7))) {
                average = data[0]/31
            }
            else {
                average = data[0]/30
            }
            document.getElementById('total_spending_display').textContent = `£${Number(data[0]).toFixed(2)}`
            document.getElementById('average_daily_spending_display').textContent = `£${Number(average).toFixed(2)}`
            return data[0]
        }
        else {
            document.getElementById('total_spending_display').textContent = 'N/A'
            document.getElementById('average_daily_spending_display').textContent = 'N/A'
        }
    })
    .catch(error => console.log(error))
}
// Retrieves the amount spent on a category in the target month and in the month before it
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
        // Both the current and previous spending must not be false
        // Boolean algebra: NOT (X AND Y) = NOT X OR NOT Y
        if(data[0] !== 'False' || data[1] !== 'False') {
            return data
        }
    })
    .catch(error => console.log(error))
}
// Adds spending insights to a table
function add_categories_to_table(current_and_previous_spending, sum) {
    const table = document.getElementById('spending_insights_table')
    categories_and_amount = current_and_previous_spending[0]
    spending_differences = current_and_previous_spending[1]

    categories_and_amount = Object.fromEntries(categories_and_amount)
    categories = Object.keys(categories_and_amount)

    // If-statement used to decide whether to populate the spending difference column with N/A or with actual values
    if(spending_differences !== 'False') {
        for(let i = 0; i < categories.length; i++) {
            category_name = categories[i]
            category_amount = categories_and_amount[category_name].toFixed(2)
            percentage_amount = (category_amount/sum*100).toFixed(2)
            spending_difference = spending_differences[1][i].toFixed(2)
            row = `<tr><td>${category_name}</td><td>${category_amount}</td><td>${percentage_amount}</td><td>${spending_difference}</td></tr>`
            table.innerHTML += row
        }
    }
    else {
        for(let i = 0; i < Object.keys(categories_and_amount).length; i++) {
            category_name = categories[i]
            category_amount = categories_and_amount[category_name].toFixed(2)
            percentage_amount = (category_amount/sum*100).toFixed(2)
            spending_difference = 'N/A'
            row = `<tr><td>${category_name}</td><td>${category_amount}</td><td>${percentage_amount}</td><td>${spending_difference}</td></tr>`
            table.innerHTML += row
        }
    }
}
// Decrements a date in the format YYYY-MM to the previous month
function decrement_month_year(month_year) {
    // If on January, decrement to December of the previous year
    if(month_year.slice(5, 7) == '01') {
        previous_month_year = String(Number(month_year.slice(0, 4)) - 1) + '-12'
    }
    else {
        // Checks if the new month has one or two digits to avoid dates in the form of YYYY-0MM 
        if(Number(month_year.slice(5, 7)) >= 11) {
            previous_month_year = month_year.slice(0, 5) + String(Number(month_year.slice(5, 7)) - 1)
        }
        else {
            previous_month_year = month_year.slice(0, 5) + '0' + String(Number(month_year.slice(5, 7)) - 1)
        }
    }
    return previous_month_year
}
// Increments a date in the format YYYY-MM to the next month
function increment_month_year(month_year) {
    // If on December, increment to January of the next year
    if(month_year.slice(5, 7) == '12') {
        next_month_year = String(Number(month_year.slice(0, 4)) + 1) + '-01'
    }
    else {
        // Checks if the new month has one or two digits to avoid dates in the form of YYYY-0MM 
        if(Number(month_year.slice(5, 7)) >= 9) {
            next_month_year = month_year.slice(0, 5) + String(Number(month_year.slice(5, 7)) + 1)
        }
        else {
            next_month_year = month_year.slice(0, 5) + '0' + String(Number(month_year.slice(5, 7)) + 1)
        }
    }
    return next_month_year
}

// Calls the initial_setup function once the page loads
document.addEventListener('DOMContentLoaded', initial_setup, false);
// Event listeners for pagination buttons
document.getElementById("left_pagination").addEventListener('click', pagination_handler)
document.getElementById("right_pagination").addEventListener('click', pagination_handler)