from tkinter import *
import pyodbc

#defines SQL Server and database name
server = "DESKTOP-DRDGQUL\SQLEXPRESS"
database = "data_airlines"

#creates SQL cursor
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + server + '; DATABASE=' + database + '; Trusted_connection=yes;')
cursor = cnxn.cursor()

#insert statement for inserting row into customers
insert_query = '''INSERT INTO customers
                  VALUES (?, ?);'''
#creates root variable
root = Tk()

#defines root title
root.title("Data Airlines Login")


#function that chages what frame you are on when called
def show_frame(frame):
    frame.tkraise()


#lists each frame in program
login_frame = Frame(root)
create_account_frame = Frame(root)
create_confirmation_frame = Frame(root)
flight_list_page = Frame(root)
book_seat_page = Frame(root)
seat_confirm_page = Frame(root)

#makes frame display on whole screen
for frame in (login_frame, create_account_frame, create_confirmation_frame, flight_list_page, book_seat_page, seat_confirm_page):
    frame.grid(row=0, column=0, sticky='nsew')

#makes the login_frame the first frame shown
show_frame(login_frame)


#=============== login page
user_name_entry = Entry(login_frame, width=50)
user_name_entry.grid(row=0, column=1, pady=10, columnspan=3)
username = Label(login_frame, text="Username").grid(row=0, column=0, padx=5)
password = Label(login_frame, text="Password").grid(row=1, column=0)
password_entry = Entry(login_frame, width=50)
password_entry.grid(row=1, column=1, columnspan=3)


#the login function tests if username and password belong to the same account. If they do then they gain access to the rest of the program and a temp user is created in SQL Server. Otherwise they are denied
def login():
    select_customers = 'SELECT customer_name FROM customers WHERE customer_name = \'' + user_name_entry.get() + '\' AND password = \'' + password_entry.get() + '\''
    customer_name = cursor.execute(select_customers).fetchall()
    if customer_name == []:
        Label(login_frame, text="ACCESS DENIED!", font=50, fg="red").grid(row=4, column=1, columnspan=3)
    else:
        temp_insert = 'INSERT INTO t_user VALUES (?)'
        temp_user = [user_name_entry.get()]
        cursor.execute(temp_insert, temp_user)
        cnxn.commit()
        seat_confirm()


login_button = Button(login_frame, text="Login", command=login, fg="blue")
login_button.grid(row=2, column=1, pady=15)

creation_buttion = Button(login_frame, text="Create account", command=lambda: show_frame(create_account_frame), fg="blue")
creation_buttion.grid(row=2, column=2,)

#============ Account creation page
new_username = Entry(create_account_frame, width=50)
new_username.grid(row=0, column=1, pady=10, columnspan=3)
username_c = Label(create_account_frame, text="Create username").grid(row=0, column=0)
password_c = Label(create_account_frame, text="Create password").grid(row=1, column=0)
new_password = Entry(create_account_frame, width=50)
new_password.grid(row=1, column=1, columnspan=3)


#creates account if none exists
def create_account():
    confirm_unique = 'SELECT customer_name FROM customers WHERE customer_name = \'' + new_username.get() + '\''
    unique_account = cursor.execute(confirm_unique).fetchval()
    if new_username.get() == unique_account:
        Label(create_account_frame, text="That account already exists!", font=50, fg='red').grid(row=4, column=1, columnspan=3)
    else:
        user_data = [new_username.get(), new_password.get()]
        cursor.execute(insert_query, user_data)
        cnxn.commit()
        show_frame(create_confirmation_frame)


create_button = Button(create_account_frame, text="Confirm", command=create_account, fg="blue")
create_button.grid(row=2, column=1, pady=15)
return1_button = Button(create_account_frame, text="Return to login", command=lambda: show_frame(login_frame), fg="blue")
return1_button.grid(row=2, column=2)

#========== account confirmation page
Label(create_confirmation_frame, text="Account created!", font=100, fg='green').grid(row=0, column=0, pady=(75, 20), padx=150)
return2_button = Button(create_confirmation_frame, text="Return to login", command=lambda: show_frame(login_frame), fg="blue")
return2_button.grid(row=1, column=0,)

#========== flight list page
airport_scrollbar = Scrollbar(flight_list_page, orient=VERTICAL)
airport_listbox = Listbox(flight_list_page, yscrollcommand=airport_scrollbar.set)
airport_listbox.grid(row=3, column=1, columnspan=2)
airport_scrollbar.config(command=airport_listbox.yview)
airport_scrollbar.grid(row=3, column=3, sticky=(N, S))


#sets the departure airport
def departure_set():
    departure_airport.delete(0, 'end')
    departure_airport.insert(0, airport_listbox.get(ANCHOR))


#sets the arrival airport
def arrival_set():
    arrival_airport.delete(0, 'end')
    arrival_airport.insert(0, airport_listbox.get(ANCHOR))


departure_airport = Entry(flight_list_page, width=4)
departure_airport.grid(row=0, column=1)
Button(flight_list_page, text='Departure:', command=lambda: departure_set()).grid(row=0, column=0, pady=10, padx=10)
Button(flight_list_page, text='Arrival:', command=lambda: arrival_set()).grid(row=0, column=2, padx=20)
arrival_airport = Entry(flight_list_page, width=4)
arrival_airport.grid(row=0, column=3)
Label(flight_list_page, text='Airports').grid(row=1, column=2)
select_airports = 'SELECT airport_code FROM airports'
airport_code = cursor.execute(select_airports).fetchall()

#displays all airports in database
for i in range(len(airport_code)):
    airport_listbox.insert(END, [x for x in cursor.execute(select_airports).fetchall()[i]])


#displays all flights on the selected route
def find_flights():
    route_confirm = 'SELECT route_id FROM plane_routes WHERE departure_airport = \'' + departure_airport.get() + '\' AND arrival_airport = \'' + arrival_airport.get() + '\''
    confirmed_route = cursor.execute(route_confirm).fetchval()
    find_departure = 'SELECT DISTINCT departure_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    departure_time = cursor.execute(find_departure).fetchall()
    for ticket_idx in range(len(departure_time)):
        row_add = ticket_idx + 4
        Label(flight_list_page, text=[x[0] for x in departure_time][ticket_idx]).grid(row=row_add, column=0, padx=10, pady=10)
        find_arrival = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
        Label(flight_list_page, text=[x[0] for x in cursor.execute(find_arrival).fetchall()][ticket_idx]).grid(row=row_add, column=1)
        flight_select_button = Button(flight_list_page, text="SELECT FLIGHT", command=lambda ticket_idx=ticket_idx: booker_main(ticket_idx, confirmed_route))
        flight_select_button.grid(row=row_add, column=2, padx=10)


flight_finder_button = Button(flight_list_page, text="Enter", command=find_flights)
flight_finder_button.grid(row=0, column=4, padx=40)

#=============== Seat booker page


#books selected seat for user
def fill_seat(ticket_idx, confirmed_route):
    current_user = cursor.execute('SELECT * FROM t_user').fetchval()
    select_user_id = 'SELECT customer_id FROM customers WHERE customer_name = \'' + str(current_user) + '\''
    user_id = cursor.execute(select_user_id).fetchval()
    find_departure2 = 'SELECT DISTINCT departure_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    departure_airport2 = cursor.execute(find_departure2).fetchall()[ticket_idx]
    cursor.execute('UPDATE plane_ticket SET customer_name = ' + str(user_id) + ' WHERE seat_id = \'' + str(seat_listbox.get(ANCHOR)) + '\' AND plane_route = \'' + str(confirmed_route) + '\' AND departure_time = \'' + str(departure_airport2[0]) + '\'')
    cnxn.commit()
    seat_confirm()


seat_scrollbar = Scrollbar(book_seat_page, orient=VERTICAL)
seat_listbox = Listbox(book_seat_page, yscrollcommand=seat_scrollbar.set)
seat_listbox.grid(row=1, column=2, pady=20)
seat_scrollbar.config(command=seat_listbox.yview)
seat_scrollbar.grid(row=1, column=3, sticky=(N, S))


#shows all first class seats
def show_first(ticket_idx, confirmed_route):
    global seat_listbox
    seat_listbox.delete(0, END)
    find_arrival_f = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    arrival_airport_f = [z[0] for z in cursor.execute(find_arrival_f).fetchall()]
    my_arrival_f = arrival_airport_f[ticket_idx]
    seats = 'SELECT seat_id FROM plane_ticket WHERE (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(my_arrival_f) + '\' AND customer_name = 1006 AND RIGHT(seat_id,LEN(seat_id) - 1) IN (01,02))'
        #'SELECT seat_id FROM plane_ticket WHERE (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(my_arrival_f) + '\' AND customer_name = 1006 and seat_id LIKE \'%01\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(my_arrival_f) + '\' AND customer_name = 1006 and seat_id LIKE \'%02\')'
    seat_count = [x[0] for x in cursor.execute(seats).fetchall()]
    for i in range(len(seat_count)):
        seat_listbox.insert(END, seat_count[i])


#shows all business class seats
def show_business(ticket_idx, confirmed_route):
    global seat_listbox
    seat_listbox.delete(0, END)
    find_arrival_b = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    arrival_airport_b = [z[0] for z in cursor.execute(find_arrival_b).fetchall()]
    my_arrival_b = arrival_airport_b[ticket_idx]
    seats = 'SELECT seat_id FROM plane_ticket WHERE (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(my_arrival_b) + '\' AND customer_name = 1006 AND RIGHT(seat_id,LEN(seat_id) - 1) IN (03,04,05,06,07,08,09,10,11,12,13))'
    seat_count = [x[0] for x in cursor.execute(seats).fetchall()]
    for i in range(len(seat_count)):
        seat_listbox.insert(END, seat_count[i])


#shows all economy class seats
def show_economy(ticket_idx, confirmed_route):
    global seat_listbox
    seat_listbox.delete(0, END)
    find_arrival_e = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    arrival_airport_e = [z[0] for z in cursor.execute(find_arrival_e).fetchall()]
    my_arrival_e = arrival_airport_e[ticket_idx]
    seats = 'SELECT seat_id FROM plane_ticket WHERE (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(my_arrival_e) + '\' AND customer_name = 1006 AND RIGHT(seat_id,LEN(seat_id) - 1) IN (14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40))'
    seat_count = [x[0] for x in cursor.execute(seats).fetchall()]
    for i in range(len(seat_count)):
        seat_listbox.insert(END, seat_count[i])


#fills booker_main page with arrival and departure times, prices ,buttons and listbox
def booker_main(ticket_idx, confirmed_route):
    global seat_listbox
    show_frame(book_seat_page)
    find_arrival2 = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    find_departure2 = 'SELECT DISTINCT departure_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    arrival2 = cursor.execute(find_arrival2).fetchall()[ticket_idx]
    departure_2 = cursor.execute(find_departure2).fetchall()[ticket_idx]
    Label(book_seat_page, text=str(departure_2[0]) + ' - ' + str(arrival2[0])).grid(row=1, column=0, columnspan=2, padx=25, pady=25)
    Button(book_seat_page, text=("First Class"), command=lambda: show_first(ticket_idx, confirmed_route)).grid(row=2, column=0)
    Button(book_seat_page, text=("Business Class"), command=lambda: show_business(ticket_idx, confirmed_route)).grid(row=2, column=1)
    Button(book_seat_page, text=("Economy Class"), command=lambda: show_economy(ticket_idx, confirmed_route)).grid(row=2, column=2)
    Button(book_seat_page, text="Select Seat", command=lambda: fill_seat(ticket_idx, confirmed_route)).grid(row=1, column=4, padx=10)
    price_selector = 'SELECT cost FROM plane_routes WHERE route_id = \'' + str(confirmed_route) + '\''
    seat_count = cursor.execute('SELECT seat_count FROM plane_type WHERE plane_type_id = 1').fetchval()
    f_price = int(cursor.execute(price_selector).fetchval() / seat_count * 4)
    b_price = int(cursor.execute(price_selector).fetchval() / seat_count * 3)
    e_price = int(cursor.execute(price_selector).fetchval() / seat_count * 2)
    Label(book_seat_page, text="$" + str(f_price)).grid(row=3, column=0)
    Label(book_seat_page, text="$" + str(b_price)).grid(row=3, column=1)
    Label(book_seat_page, text="$" + str(e_price)).grid(row=3, column=2)


#=================== seat confirmation page

user_seat_scrollbar = Scrollbar(seat_confirm_page, orient=VERTICAL)
user_seats_listbox = Listbox(seat_confirm_page, yscrollcommand=user_seat_scrollbar.set)
user_seats_listbox.grid(row=0, column=0, pady=25)
user_seat_scrollbar.config(command=user_seats_listbox.yview)
user_seat_scrollbar.grid(row=0, column=1, sticky=(N, S), pady=25)


#shows list of seats that a user has booked
def seat_confirm():
    show_frame(seat_confirm_page)
    current_user = cursor.execute('SELECT * FROM t_user').fetchval()
    current_user_id = cursor.execute('SELECT customer_id FROM customers WHERE customer_name = \'' + str(current_user) + '\'').fetchval()
    select_user_seats = 'SELECT seat_id FROM plane_ticket WHERE customer_name = \'' + str(current_user_id) + '\''
    user_seats = [x[0] for x in cursor.execute(select_user_seats).fetchall()]
    select_user_routes = 'SELECT plane_route FROM plane_ticket WHERE customer_name = \'' + str(current_user_id) + '\''
    user_routes = cursor.execute(select_user_routes).fetchall()
    for i in range(len(user_seats)):
        select_user_departure = 'SELECT departure_airport FROM plane_routes WHERE route_id = ' + str(user_routes[i][0]) + ''
        departure = cursor.execute(select_user_departure).fetchall()
        select_user_arrival = 'SELECT arrival_airport FROM plane_routes WHERE route_id = ' + str(user_routes[i][0]) + ''
        arrival = cursor.execute(select_user_arrival).fetchall()
        user_seats_listbox.insert(END, user_seats[i] + '   ' + str(departure[0][0] + ' - ' + str(arrival[0][0])))



#removes seat from a user's booked seats
def refund():
    refund_seats = user_seats_listbox.get(ANCHOR)[0:3]
    cursor.execute('UPDATE plane_ticket SET customer_name = 1006 WHERE seat_id = \'' + str(refund_seats) + '\'')
    cnxn.commit()
    user_seats_listbox.delete(user_seats_listbox.curselection())


#goes to flight list frame
def goto_flight_list():
    user_seats_listbox.delete(0, END)
    show_frame(flight_list_page)


Button(seat_confirm_page, text='Refund plane ticket', command=refund).grid(row=0, column=2, padx=20)

goto_flight_list_button = Button(seat_confirm_page, text='Book flight', command=lambda: goto_flight_list()).grid(row=0, column=3)


#=================== window closed


#clears the t_user column in SQL Server when closing the program
def on_closing():
    cursor.execute('DELETE FROM t_user')
    cnxn.commit()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()