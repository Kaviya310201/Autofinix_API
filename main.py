from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

# FastAPI app
app = FastAPI()

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="autofinix",  # Replace with your database name
    user="autofinix",    # Replace with your username
    password="root",     # Replace with your password
    host="localhost",    # If using Docker, replace with the container IP or 'localhost'
    port="5432"          # Default PostgreSQL port
)
cursor = conn.cursor()

# Pydantic model for request validation
class Customer(BaseModel):
    customerid: int
    fullname: str
    dateofbirth: str
    email: str
    phonenumber: str
    address: str
    registrationdate: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the AutoLoan API!"}


# Get all customers
@app.get("/customers")
def get_customers():
    cursor.execute("SELECT * FROM schema_autofinix.customer;")
    customers = cursor.fetchall()
    return {"customers": customers}


# Get customer by ID
@app.get("/customers/{customerid}")
def get_customer(customerid: int):
    cursor.execute("SELECT * FROM schema_autofinix.customer WHERE customerid = %s;", (customerid,))
    customer = cursor.fetchone()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer": customer}


# Create new customer
@app.post("/customers")
def create_customer(customer: Customer):
    cursor.execute(
        """
        INSERT INTO schema_autofinix.customer (customerid, fullname, dateofbirth, email, phonenumber, address, registrationdate)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, 
        (customer.customerid, customer.fullname, customer.dateofbirth, customer.email, 
         customer.phonenumber, customer.address, customer.registrationdate)
    )
    conn.commit()
    return {"message": "Customer created successfully"}


# Update customer details
@app.put("/customers/{customerid}")
def update_customer(customerid: int, customer: Customer):
    cursor.execute(
        """
        UPDATE schema_autofinix.customer 
        SET fullname = %s, dateofbirth = %s, email = %s, phonenumber = %s, address = %s, registrationdate = %s
        WHERE customerid = %s;
        """, 
        (customer.fullname, customer.dateofbirth, customer.email, customer.phonenumber, 
         customer.address, customer.registrationdate, customerid)
    )
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer updated successfully"}


# Delete customer by ID
@app.delete("/customers/{customerid}")
def delete_customer(customerid: int):
    cursor.execute("DELETE FROM schema_autofinix.customer WHERE customerid = %s;", (customerid,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}
