from tkinter import *
import pyodbc

server = "DESKTOP-DRDGQUL\SQLEXPRESS"
database = "data_airlines"

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + server + '; DATABASE=' + database + '; Trusted_connection=yes;')

cursor = cnxn.cursor()

insert_query = '''INSERT INTO customers
                  VALUES (?, ?);'''

root = Tk()
root.title("Data Airlines Login")


def show_frame(frame):
    frame.tkraise()


login_frame = Frame(root)
create_account_frame = Frame(root)
create_confirmation_frame = Frame(root)
flight_list_page = Frame(root)
book_seat_page = Frame(root)
seat_confirm_page = Frame(root)

for frame in (login_frame, create_account_frame, create_confirmation_frame, flight_list_page, book_seat_page, seat_confirm_page):
    frame.grid(row=0, column=0, sticky='nsew')

show_frame(login_frame)


#=============== login page
eu = Entry(login_frame, width=50)
eu.grid(row=0, column=1, pady=10, columnspan=3)
username = Label(login_frame, text="Username").grid(row=0, column=0, padx=5)
password = Label(login_frame, text="Password").grid(row=1, column=0)
ep = Entry(login_frame, width=50)
ep.grid(row=1, column=1, columnspan=3)

def login():
    select_customers = 'SELECT customer_name FROM customers WHERE customer_name = \'' + eu.get() + '\' AND pass_word = \'' + ep.get() + '\''
    customer_name = cursor.execute(select_customers).fetchall()
    select_password = 'SELECT pass_word FROM customers WHERE customer_name = \'' + eu.get() + '\' AND pass_word = \'' + ep.get() + '\''
    pass_word = cursor.execute(select_password).fetchall()
    if customer_name == []:
        Label(login_frame, text="ACCESS DENIED!", font=50, fg="red").grid(row=4, column=1, columnspan=3)
    else:
        temp_insert = 'INSERT INTO t_user VALUES (?)'
        eug = [eu.get()]
        cursor.execute(temp_insert, eug)
        cnxn.commit()
        seat_confirm()



login_button = Button(login_frame, text="Login", command=login, fg="blue")
login_button.grid(row=2, column=1, pady=15)

creation_buttion = Button(login_frame, text="Create account", command=lambda: show_frame(create_account_frame), fg="blue")
creation_buttion.grid(row=2, column=2,)

#============ Account creation page
cu = Entry(create_account_frame, width=50)
cu.grid(row=0, column=1, pady=10, columnspan=3)
username_c = Label(create_account_frame, text="Create username").grid(row=0, column=0)
password_c = Label(create_account_frame, text="Create password").grid(row=1, column=0)
cp = Entry(create_account_frame, width=50)
cp.grid(row=1, column=1, columnspan=3)


def create_account():
    confirm_unique = 'SELECT customer_name FROM customers WHERE customer_name = \'' + cu.get() + '\''
    unique_account = cursor.execute(confirm_unique).fetchval()
    if cu.get() == unique_account:
        Label(create_account_frame, text="That account already exists!", font=50, fg='red').grid(row=4, column=1, columnspan=3)
    else:
        user_data = [cu.get(), cp.get()]
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


def departure_set():
    df.delete(0, 'end')
    df.insert(0, airport_listbox.get(ANCHOR))

def arrival_set():
    af.delete(0, 'end')
    af.insert(0, airport_listbox.get(ANCHOR))

df = Entry(flight_list_page, width=4)
df.grid(row=0, column=1)
Button(flight_list_page, text='Departure:', command=lambda: departure_set()).grid(row=0, column=0, pady=10, padx=10)
Button(flight_list_page, text='Arrival:', command=lambda: arrival_set()).grid(row=0, column=2, padx=20)
af = Entry(flight_list_page, width=4)
af.grid(row=0, column=3)
Label(flight_list_page, text='Airports').grid(row=1, column=2)
select_airports = 'SELECT airport_code FROM airports'
a = cursor.execute(select_airports).fetchall()

for aa in range(len(a)):
    airport_listbox.insert(END, [x for x in cursor.execute(select_airports).fetchall()[aa]])

def find_flights():
    route_confirm = 'SELECT route_id FROM plane_routes WHERE departure_airport = \'' + df.get() + '\' AND arrival_airport = \'' + af.get() + '\''
    confirmed_route = cursor.execute(route_confirm).fetchval()
    find_departure = 'SELECT DISTINCT departure_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    departure_time = cursor.execute(find_departure).fetchall()
    for fd in range(len(departure_time)):
        afd = fd + 4
        Label(flight_list_page, text=[x[0] for x in departure_time][fd]).grid(row=afd, column=0, padx=10, pady=10)
        find_arrival = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
        Label(flight_list_page, text=[x[0] for x in cursor.execute(find_arrival).fetchall()][fd]).grid(row=afd, column=1)

        flight_select_button = Button(flight_list_page, text="SELECT FLIGHT", command=lambda fd=fd: function_test(fd, confirmed_route))
        flight_select_button.grid(row=afd, column=2, padx=10)


flight_finder_buttion = Button(flight_list_page, text="Enter", command=find_flights)
flight_finder_buttion.grid(row=0, column=4, padx=40)

#=============== Seat booker page


def fill_seat(fd, confirmed_route):
    current_user = cursor.execute('SELECT * FROM t_user').fetchval()
    select_user_id = 'SELECT customer_id FROM customers WHERE customer_name = \'' + str(current_user) + '\''
    user_id = cursor.execute(select_user_id).fetchval()
    find_departure2 = 'SELECT DISTINCT departure_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    x = cursor.execute(find_departure2).fetchall()[fd]
    cursor.execute('UPDATE plane_ticket SET customer_name = ' + str(user_id) + ' WHERE seat_id = \'' + str(seat_listbox.get(ANCHOR)) + '\' AND plane_route = \'' + str(confirmed_route) + '\' AND departure_time = \'' + str(x[0]) + '\'')
    cnxn.commit()
    s_seat = seat_listbox.get(ANCHOR)
    seat_confirm()


seat_scrollbar = Scrollbar(book_seat_page, orient=VERTICAL)
seat_listbox = Listbox(book_seat_page, yscrollcommand=seat_scrollbar.set)
seat_listbox.grid(row=1, column=2, pady=20)
seat_scrollbar.config(command=seat_listbox.yview)
seat_scrollbar.grid(row=1, column=3, sticky=(N, S))


def show_first(fd, confirmed_route):
    global seat_listbox
    seat_listbox.delete(0, END)
    find_arrival2 = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    z = [z[0] for z in cursor.execute(find_arrival2).fetchall()]
    zz = z[fd]
    seats = 'SELECT seat_id FROM plane_ticket WHERE (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%01\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%02\')'
    seat_count = [x[0] for x in cursor.execute(seats).fetchall()]
    for s in range(len(seat_count)):
        seat_listbox.insert(END, seat_count[s])

def show_business(fd, confirmed_route):
    global seat_listbox
    seat_listbox.delete(0, END)
    find_arrival2 = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    z = [z[0] for z in cursor.execute(find_arrival2).fetchall()]
    zz = z[fd]
    seats = 'SELECT seat_id FROM plane_ticket WHERE (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%03\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%04\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%05\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%05\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%06\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%07\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%08\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%09\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%10\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%11\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%12\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%13\')'
    seat_count = [x[0] for x in cursor.execute(seats).fetchall()]
    for s in range(len(seat_count)):
        seat_listbox.insert(END, seat_count[s])

def show_economy(fd, confirmed_route):
    global seat_listbox
    seat_listbox.delete(0, END)
    find_arrival2 = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    z = [z[0] for z in cursor.execute(find_arrival2).fetchall()]
    zz = z[fd]
    seats = 'SELECT seat_id FROM plane_ticket WHERE (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%14\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%15\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%16\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%17\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%18\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%19\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%20\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%21\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%22\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%23\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%24\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%25\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%26\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%27\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%28\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%29\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%30\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%31\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%32\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%33\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%34\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%35\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%36\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%37\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%38\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%39\') OR (plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006 and seat_id LIKE \'%40\')'
    seat_count = [x[0] for x in cursor.execute(seats).fetchall()]
    for s in range(len(seat_count)):
        seat_listbox.insert(END, seat_count[s])

def function_test(fd, confirmed_route):
    show_frame(book_seat_page)
    find_arrival2 = 'SELECT DISTINCT arrival_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    find_departure2 = 'SELECT DISTINCT departure_time FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\''
    z = [z[0] for z in cursor.execute(find_arrival2).fetchall()]
    y = cursor.execute(find_arrival2).fetchall()[fd]
    x = cursor.execute(find_departure2).fetchall()[fd]
    zz = z[fd]
    Label(book_seat_page, text=str(x[0]) + ' - ' + str(y[0])).grid(row=1, column=0, columnspan=2, padx=25, pady=25)
    seats = 'SELECT seat_id FROM plane_ticket WHERE plane_route = \'' + str(confirmed_route) + '\' AND arrival_time = \'' + str(zz) + '\' AND customer_name = 1006'
    seat_count = [x[0] for x in cursor.execute(seats).fetchall()]
    global seat_listbox
    first_button = Button(book_seat_page, text=("First Class"), command=lambda: show_first(fd, confirmed_route)).grid(row=2, column=0)
    business_button = Button(book_seat_page, text=("Business Class"), command=lambda: show_business(fd, confirmed_route)).grid(row=2, column=1)
    economy_button = Button(book_seat_page, text=("Economy Class"), command=lambda: show_economy(fd, confirmed_route)).grid(row=2, column=2)
    select_seat_button = Button(book_seat_page, text="Select Seat", command=lambda: fill_seat(fd, confirmed_route)).grid(row=1, column=4, padx=10)


#=================== seat confirmation page

user_seat_scrollbar = Scrollbar(seat_confirm_page, orient=VERTICAL)
user_seats_listbox = Listbox(seat_confirm_page, yscrollcommand=user_seat_scrollbar.set)
user_seats_listbox.grid(row=0, column=0, pady=25)
user_seat_scrollbar.config(command=user_seats_listbox.yview)
user_seat_scrollbar.grid(row=0, column=1, sticky=(N, S), pady=25)

def seat_confirm():
    show_frame(seat_confirm_page)
    current_user = cursor.execute('SELECT * FROM t_user').fetchval()
    current_user_id = cursor.execute('SELECT customer_id FROM customers WHERE customer_name = \'' + str(current_user) + '\'').fetchval()
    select_user_seats = 'SELECT seat_id FROM plane_ticket WHERE customer_name = \'' + str(current_user_id) + '\''
    user_seats = [x[0] for x in cursor.execute(select_user_seats).fetchall()]
    for s in range(len(user_seats)):
        user_seats_listbox.insert(END, user_seats[s])


def refund():
    cursor.execute('UPDATE plane_ticket SET customer_name = 1006 WHERE seat_id = \'' + str(user_seats_listbox.get(ANCHOR)) + '\'')
    cnxn.commit()
    user_seats_listbox.delete(user_seats_listbox.curselection())


def goto_flight_list():
    user_seats_listbox.delete(0, END)
    show_frame(flight_list_page)

refund_button = Button(seat_confirm_page, text='Refund plane ticket', command=refund).grid(row=0, column=2, padx=20)

goto_flight_list_button = Button(seat_confirm_page, text='Book flight', command=lambda: goto_flight_list()).grid(row=0, column=3)


#=================== window closed


def on_closing():
    cursor.execute('DELETE FROM t_user')
    cnxn.commit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
