from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import MySQLdb
from MySQLdb.cursors import DictCursor
import connect

app = Flask(__name__)
app.secret_key = "your_secret_key" 

connection = None
cursor = None

def getCursor():
    global connection
    global cursor

    if connection is None:
        connection = MySQLdb.connect(
            user=connect.dbuser,
            password=connect.dbpass,
            host=connect.dbhost,
            database=connect.dbname,
            port=int(connect.dbport),
            autocommit=True
        )
    cursor = connection.cursor(DictCursor)
    return cursor


@app.route("/")
def home():
    return render_template("home.html")

@app.route('/events', methods=['GET', 'POST'])
def events():
    cursor = getCursor()

    if request.method == 'POST':
        event_id = request.form['event_id']
        cursor.execute("SELECT event_id, event_name, event_date, tickets_remaining, age_restriction FROM events WHERE event_id = %s", (event_id,))
        event = cursor.fetchone()

        if event:
            return redirect(url_for('eventcustomerlist', event_id=event_id))

    # this is for If GET request, fetch all events
    cursor.execute("SELECT event_id, event_name, event_date FROM events WHERE event_date > NOW() ORDER BY event_date ASC")
    events = cursor.fetchall()
    return render_template('events.html', events=events)

@app.route('/eventcustomerlist', methods=['GET', 'POST'])
def eventcustomerlist():
    if request.method == 'POST':
        event_id = request.form['event_id']  #it will get the event ID from form

    elif request.method == 'GET':
        event_id = request.args.get('event_id')  # here it Get event ID from query string

    if not event_id:
        flash("Event not found.", 'danger')
        return redirect(url_for('events'))

    cursor = getCursor()
    # it Fetch event details
    cursor.execute("""
        SELECT event_name, event_date
        FROM events
        WHERE event_id = %s
    """, (event_id,))
    event = cursor.fetchone()

    if not event:
        flash("Event not found.", 'danger')
        return redirect(url_for('events'))
    cursor.execute("""
        SELECT c.customer_id, c.first_name, c.family_name, c.date_of_birth, c.email
        FROM customers c
        JOIN ticket_sales ts ON c.customer_id = ts.customer_id
        WHERE ts.event_id = %s
        ORDER BY c.family_name ASC, c.date_of_birth DESC
    """, (event_id,))
    customerlist = cursor.fetchall()

    if not customerlist:
        flash("No customers have purchased tickets for this event.", 'info')

    return render_template('eventcustomerlist.html', event=event, customerlist=customerlist)


@app.route('/customers', methods=['GET'])
def customers():
    search_query = request.args.get('search', '')
    cursor = getCursor()

    if search_query:
        query = """
            SELECT customer_id, family_name, first_name, date_of_birth, email
            FROM customers
            WHERE family_name LIKE %s OR first_name LIKE %s OR email LIKE %s
        """
        cursor.execute(query, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("""
            SELECT customer_id, family_name, first_name, date_of_birth, email
            FROM customers
        """)
    customers = cursor.fetchall()
    return render_template("customers.html", customers=customers)
@app.route("/customers/tickets/<int:customer_id>")
def customerticket(customer_id):
    cursor = getCursor()

    #It help to  Fetch detailed customer information
    cursor.execute("""
        SELECT first_name, family_name, date_of_birth, email
        FROM customers
        WHERE customer_id = %s
    """, (customer_id,))
    customer = cursor.fetchone()

    if not customer:
        flash("Customer not found.", 'danger')
        return redirect(url_for('customers'))

    # Fetch the customer's ticket information
    cursor.execute("""
        SELECT e.event_name, e.event_date, ts.tickets_purchased
        FROM ticket_sales ts
        JOIN events e ON ts.event_id = e.event_id
        WHERE ts.customer_id = %s
    """, (customer_id,))
    tickets = cursor.fetchall()

    if not tickets:
        flash("No tickets found for this customer.", 'info')

    return render_template("customertickets.html", customer=customer, tickets=tickets)

@app.route('/addcustomer', methods=['GET', 'POST'])
def add_customer():
    cursor = getCursor()
    cursor.execute("SELECT event_id, event_name FROM events")
    events = cursor.fetchall()

    if request.method == 'POST':
        first_name = request.form['first_name']
        family_name = request.form['family_name']
        date_of_birth = request.form['date_of_birth']
        email = request.form['email']
        event_id = request.form['event_id']

        if not first_name or not family_name or not date_of_birth or not email or not event_id:
            flash("All fields are required!", 'danger')
            return redirect(url_for('add_customer'))

        if '@' not in email or '.' not in email:
            flash("Please enter a valid email address.", 'danger')
            return redirect(url_for('add_customer'))


        cursor.execute("""
            INSERT INTO customers (first_name, family_name, date_of_birth, email, event_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, family_name, date_of_birth, email, event_id))

        flash("Customer added successfully!", 'success')
        return redirect(url_for('customers'))

    return render_template('addcustomer.html', events=events)


@app.route('/editcustomer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    cursor = getCursor()

    if request.method == 'POST':
        # Get updated form data
        first_name = request.form['first_name']
        family_name = request.form['family_name']
        date_of_birth = request.form['date_of_birth']
        email = request.form['email']

        if not first_name or not family_name or not date_of_birth or not email:
            flash("All fields are required!", 'danger')
            return redirect(url_for('edit_customer', customer_id=customer_id))

        # Check if email is valid
        if '@' not in email or '.' not in email:
            flash("Please enter a valid email address.", 'danger')
            return redirect(url_for('edit_customer', customer_id=customer_id))

        # Update customer in the database
        cursor.execute("""
            UPDATE customers
            SET first_name = %s, family_name = %s, date_of_birth = %s, email = %s
            WHERE customer_id = %s
        """, (first_name, family_name, date_of_birth, email, customer_id))

        flash("Customer information updated successfully!", 'success')
        return redirect(url_for('customers'))

    # Fetch the current customer data
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()

    if not customer:
        flash("Customer not found.", 'danger')
        return redirect(url_for('customers'))

    return render_template('editcustomer.html', customer=customer)

@app.route('/futureevents')
def future_events():
    cursor = getCursor()  

    # It is a Query to fetch future events with available tickets
    cursor.execute("""
        SELECT event_id, event_name, event_date, capacity
        FROM events
        WHERE event_date > NOW()  -- Only future events
        ORDER BY event_date ASC   -- Sort events by event date in ascending order
    """)

    events = cursor.fetchall()  

    return render_template('futureevents.html', events=events)


@app.route('/buytickets', methods=['POST'])
def buytickets():
    customer_id = request.form['customer_id']
    event_id = request.form['event_id']
    num_tickets = int(request.form['num_tickets']) 

    cursor = getCursor()

    # Fetch event details
    cursor.execute("""
        SELECT tickets_remaining, age_restriction, event_date
        FROM events
        WHERE event_id = %s
    """, (event_id,))
    event = cursor.fetchone()

    if not event:
        flash("Event not found.", 'danger')
        return redirect(url_for('events'))

    # Check if tickets are available
    if event['tickets_remaining'] < num_tickets:
        flash("Not enough tickets available.", 'danger')
        return redirect(url_for('events'))

    # Check customer’s age
    cursor.execute("""
        SELECT DATEDIFF(NOW(), date_of_birth) / 365 AS age
        FROM customers
        WHERE customer_id = %s
    """, (customer_id,))
    customer = cursor.fetchone()

    if customer['age'] < event['age_restriction']:
        flash(f"You must be at least {event['age_restriction']} years old to buy tickets.", 'danger')
        return redirect(url_for('events'))

    # Process ticket sale
    cursor.execute("""
        INSERT INTO ticket_sales (customer_id, event_id, tickets_purchased)
        VALUES (%s, %s, %s)
    """, (customer_id, event_id, num_tickets))

    # Update remaining tickets in the events table
    cursor.execute("""
        UPDATE events
        SET tickets_remaining = tickets_remaining - %s
        WHERE event_id = %s
    """, (num_tickets, event_id))

    flash("Ticket purchase successful!", 'success')
    return redirect(url_for('events'))

if __name__ == "__main__":
    app.run(debug=True)
