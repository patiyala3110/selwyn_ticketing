# Project Report

## Design Decisions

### 1. **Separation of Concerns (Templates and Routes)**  
I chose to separate the templates and routes to maintain a clean structure in the application. By creating individual routes for each page, such as `home`, `add_customer`, `future_events`., I ensured that each function has a single responsibility hence his makes the app more modular and easier to maintain. A good example, having a distinct route for adding a customer (`/add_customer`) made it easy to allow for better focus and easier debugging.

### 2. **Use of GET and POST Methods**  
For data retrieval, I used `GET` requests, as it is the standard method for fetching data from the server without causing any side effects (such as modifying or deleting data). For handling form submissions (e.g., adding or editing a customer), I chose to use `POST` because this method is more secure and appropriate for sending data that modifies the state on the server. Using `GET` for data retrieval and `POST` for submissions adheres to the standard HTTP conventions.

### 3. **Use of Flask's `url_for` for Route Management**  
To manage routing in the app, I used Flask's `url_for()` function. This approach allows for dynamic URL generation, which means that if the route name changes, the links throughout the application remain intact without needing manual updates. This makes the code more maintainable and flexible in the long run.

### 4. **Decision to Use Templates for Page Rendering**  
Instead of writing HTML code directly in the Python script, I decided to use Jinja2 templates to separate the presentation logic from the business logic. This approach allows me to have reusable and modular HTML components, making the code more readable and maintainable. For example, the navigation bar is included in the `base.html` template and extended in other templates like `home.html` and `add_customer.html`.

### 5. **Form Handling via Flask Forms**  
For handling form data (such as customer information), I opted to create forms within HTML templates and process them using Flask. This approach allows me to handle the form data cleanly in the route by using `request.form` to capture inputs. Additionally, I used Flask's `flash` and `redirect` to notify users about form submission success or errors, which improves the user experience.

### 6. **Handling Multiple Event Types**  
For event types, I decided not to differentiate between types (e.g., concerts, workshops) in my initial design. However, later I realized that adding event categories could be beneficial for filtering and sorting. I opted to create an additional table `event_categories` for this, enabling flexibility to classify events later without affecting existing data structures.

### 7. **Handling Database Integrity**  
I used foreign keys to ensure data integrity between the `customer`, `ticket_sales`, and `event` tables. This enforces that a ticket sale cannot exist without a valid customer and event. I also chose to implement `ON DELETE CASCADE` in the `ticket_sales` table to ensure that if a customer is deleted, all their associated ticket sales records are automatically removed.

### 8. **Validation and Error Handling**  
I added basic validation for form inputs to prevent common errors like empty fields or invalid email formats. This was done using Flask's `request.form` along with some Python checks. In case of errors, I use Flask's `flash()` to notify users of invalid data and prompt them to correct it. This decision ensures the application is robust and user-friendly.

### 9. **Event Management and Ticket Sales**  
To manage ticket sales, I stored the number of tickets purchased in the `ticket_sales` table. This structure allows tracking of customer purchases for each event. When a customer buys tickets, they are associated with both an `event_id` and `customer_id`, allowing for effective management and querying of ticket sales.

### 10. **User Authentication and Sessions**  
Though not a part of the initial version, I decided that incorporating session management for user login would be a necessary feature in future versions. Using Flask's session mechanism will allow users to log in, store their information, and access their ticket history securely.

### 11. **Data Display and Filtering**  
For displaying customer and ticket data, I initially considered showing all records in a single table. However, as the dataset grows, it will become cumbersome. I decided to add pagination and filtering features (not implemented yet) to allow users to view a specific set of records at a time.

### 12. **Modular HTML Structure**  
I kept the HTML structure modular by using components like a navigation bar and footer that are included in the `base.html` file and extended in other templates. This avoids code duplication and helps keep the templates clean and maintainable.

### 13. **Handling User Inputs with Flash Messages**  
For user feedback on successful operations (like adding a new customer), I used Flask's `flash()` function to display messages. This ensures that users receive immediate feedback and can confirm that their actions were completed correctly.

### 14. **Logging and Debugging**  
Throughout the development process, I used Flask's built-in debugger and logging features to track errors and issues. This is particularly useful during development as it helps in identifying and fixing bugs in real-time.

### 15. **Scalability Considerations**  
While the app is designed for a single event and customer base, I ensured that the underlying database structure is flexible enough to scale up to handle multiple events and customers. For instance, the `ticket_sales` table can scale to handle thousands of customers, and the `event_categories` table will allow for the introduction of multiple types of events.

---

## Image Sources

- just dowloaded  1 image which i used in the project just uploaded one image.

---

## Database Questions

### 1. What SQL statement creates the events table and defines its fields/columns?

```sql
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(255),
    event_date DATE,
    location VARCHAR(255),
    description TEXT
);
```

### 2. Which lines of SQL script set up the relationship between customers and events through ticket purchases in the ticket_sales table?

```sql
CREATE TABLE ticket_sales (
    ticket_sales_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    event_id INT,
    tickets_purchased INT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
```

### 3. SQL Script to Create a New Table `event_categories`:

```sql
CREATE TABLE event_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    description TEXT
);
```

### 4. SQL Statement to Add a New Category:

```sql
INSERT INTO event_categories (category_name, description) 
VALUES ('Concerts', 'Live music events featuring various artists.');
```

### 5. Changes Needed to Integrate the `event_categories` Table:

To integrate the `event_categories` table into the existing schema, I would add a `category_id` column to the `events` table to associate each event with a category. The `events` table would be modified as follows:

```sql
ALTER TABLE events
ADD COLUMN category_id INT;

ALTER TABLE events
ADD FOREIGN KEY (category_id) REFERENCES event_categories(category_id);
```

This ensures that each event is categorized properly and the database maintains referential integrity between events and their respective categories.
