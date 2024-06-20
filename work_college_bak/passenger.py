import sqlite3 as sl
from tkinter import *
from tkinter import ttk
from functools import partial
from random import randint

con = sl.connect('a.db')
crsr = con.cursor()

def values_tuple(colname, tablename):
    a = crsr.execute("select distinct " + colname + " from " + tablename).fetchall()
    cmb=[]
    for i in range(len(a)):
        for j in range(len(a[i])):
            cmb.append(a[i][j])
    return tuple(cmb)

def find_flights(win, cmb):
    c = []
    for i in range(len(cmb)):
        c.append(cmb[i].get())
    s1 = "select iata_code from airport where city = '" + str(c[0]) + "'"
    s2 = "select iata_code from airport where city = '" + str(c[1]) + "'"
    s3 = "select flight.u_num as 'Номер перелёта', flight.num_reis as 'Номер рейса', reis.price as 'Стоимость билета', flight.dep_date as 'Дата вылета', flight.dep_time as 'Время вылета', reis.airport_dep as 'Вылет из', flight.ar_date as 'Дата прибытия', flight.ar_time as 'Время прибытия', reis.airport_ar as 'Прибытие в' from flight, reis where dep_date = '" + c[2] + "' and reis.num = flight.num_reis and reis.airport_dep in ("+s1+") and reis.airport_ar in ("+s2+") order by reis.price asc"
    show_flights(win, s3)
    return

def add_table(tab, headings, rows):
    table = ttk.Treeview(tab, show="headings", selectmode="extended")
    table["columns"]=headings
    table["displaycolumns"]=headings
    for head in headings:
        table.heading(head, text=head, anchor=CENTER)
        table.column(head, minwidth = 0, width=100, anchor=CENTER, stretch = NO)
    for row in rows:
        table.insert('', END, values=tuple(row))
    return table

def rem_data(win, table):
    for selection in table.selection():
        item = table.item(selection)
        flight_inf = item["values"]
        pers_data(win, flight_inf)
        return

def ins_pas_data(entries, flight_inf, win):
    row = []
    for i in range(len(entries)-1):
        row.append(entries[i].get())
    row = tuple(row)
    check_doc = crsr.execute("select document from passenger").fetchall()
    if row[0] not in check_doc:
        sql_1 = "insert into passenger values " + str(row)
        crsr.execute(sql_1)
    check_tic = crsr.execute("select num from ticket").fetchall()
    check_seat = crsr.execute("select seat from ticket").fetchall()
    while True:
        tic_num = randint(0, 999)
        seat_r = randint(0, 40)
        letters = 'ABCDEFJHI'
        seat_l = randint(0, 8)
        l = letters[seat_l]
        seat = str(seat_r) + l
        if (tic_num not in check_tic and seat not in check_seat):
            break
    new = (tic_num, seat, row[0], str(flight_inf[0]))
    crsr.execute("insert into ticket values " + str(new))
    show_tic(win, new, flight_inf)
    return

def open_win():
    win1 = Tk() #создание окна для поиска билетов
    win1.title("Пассажир")
    #win1.geometry('384x128')
    win1.geometry('1024x1024')
    
    lbls_win1 = [] #добавление надписей
    lbls_win1.append(Label(win1, text="Поиск авиабилетов", font = ("Segoe UI", 14)))
    lbls_win1[0].grid(row=0, column=0, sticky=W)
    lbls_win1.append(Label(win1, text="Откуда:"))
    lbls_win1[1].grid(row=1, column=0, sticky=W)
    lbls_win1.append(Label(win1, text="Куда:"))
    lbls_win1[2].grid(row=2, column=0, sticky=W)
    lbls_win1.append(Label(win1, text="Дата отправления:"))
    lbls_win1[3].grid(row=3, column=0, sticky=W)
    lbls_win1.append(Label(win1, text="(YYYY-MM-DD)"))
    lbls_win1[4].grid(row=4, column=0, sticky=W)
    cmb = [] #массив для получения вариантов в комбобоксы
    t = values_tuple('city', 'airport')
    cmb.append(t)
    t = values_tuple('city', 'airport')
    cmb.append(t)
    t = values_tuple('dep_date', 'flight')
    cmb.append(t)
    comb_win1 = []
    comb_win1.append(ttk.Combobox(win1))
    comb_win1[0]['values'] = cmb[0]
    comb_win1[0].grid(row = 1, column = 1)
    comb_win1.append(ttk.Combobox(win1))
    comb_win1[1]['values'] = cmb[1]
    comb_win1[1].grid(row = 2, column = 1)
    comb_win1.append(ttk.Combobox(win1))
    comb_win1[2]['values'] = cmb[2]
    comb_win1[2].grid(row = 3, column = 1)
    
    f = partial(find_flights, win1, comb_win1) #преобразование функции find_flights
    find_but = Button(win1, text="Найти", command = f) #кнопка найти
    find_but.grid(row=4, column=2, sticky=W)
    return

def show_flights(win1, sql):
    flights = crsr.execute(sql)
    colnames = flights.description
    flights = flights.fetchall()
    
    fl = []
    for flight in flights: # отбор всех перелётов на которые есть ещё места
        s1 = crsr.execute("select airplane.seats from airplane join reis on airplane.model = reis.plane and reis.num = '" + str(flight[1]) + "'").fetchall()
        s2 = crsr.execute("select count(ticket.pas_doc) from ticket where ticket.flight_num = '" + str(flight[0]) + "'").fetchall()
        free_seats = s1[0][0] - s2[0][0]
        if (free_seats != 0):
            fl.append(flight)

    c_names = []
    for i in colnames:
        c_names.append(i[0])
        
    heading = Label(win1, text="Все перелёты:", font = ("Segoe UI", 14))
    heading.grid(row = 5, column = 0)
    
    table_w2 = add_table(win1, c_names, fl)
    table_w2.grid(row = 6, columnspan = 15)
    r = partial(rem_data, win1, table_w2) #изменение функции специально для окна 2
    table_w2_bind = table_w2.bind("<ButtonRelease-1>", r) #фиксирование клика мыши на определенной строке
    ch_but_table_w2 = Button(win1, text="Выбрать", command = table_w2_bind) #добавление кнопки Выбрать
    ch_but_table_w2.grid(row=5, column=1, sticky=W)
    return

def pers_data(win1, flight_inf):
    lbls_w3 = []
    lbls_w3.append(Label(win1, text="Введите личные данные:", font = ("Segoe UI", 14)))
    lbls_w3[0].grid(row = 7, column = 0, sticky=W)
    lbls_w3.append(Label(win1, text="Номер документа:"))
    lbls_w3[1].grid(row = 8, column = 0, sticky=W)
    lbls_w3.append(Label(win1, text="ФИО:"))
    lbls_w3[2].grid(row = 9, column = 0, sticky=W)
    lbls_w3.append(Label(win1, text="Дата рождения (YYYY-MM-DD):"))
    lbls_w3[3].grid(row = 10, column = 0, sticky=W)
    lbls_w3.append(Label(win1, text="Пол:"))
    lbls_w3[4].grid(row = 11, column = 0, sticky=W)
    lbls_w3.append(Label(win1, text="Эл. почта:"))
    lbls_w3[5].grid(row = 12, column = 0, sticky=W)
    lbls_w3.append(Label(win1, text="Номер банковской карты:"))
    lbls_w3[6].grid(row = 13, column = 0, sticky=W)

    entrs_w3 = []
    for i in range(6):
        entrs_w3.append(Entry(win1, textvariable=StringVar()))
        entrs_w3[i].grid(row = 8+i, column = 1, sticky=W)

    f = partial(ins_pas_data, entrs_w3, flight_inf, win1) #преобразование функции
    ins_but = Button(win1, text="Ввод данных", command = f) #кнопка ввод данных
    ins_but.grid(row=13, column=2, sticky=W)
    return

def show_tic(win1, new, flight_inf):
    lbls_w4 = []
    lbls_w4.append(Label(win1, text="Билет № " + str(new[0]), font = ("Segoe UI", 14)))
    lbls_w4[0].grid(row = 14, column = 0, sticky=W)
    lbls_w4.append(Label(win1, text="Место: " + str(new[1]), font = ("Segoe UI", 12)))
    lbls_w4[1].grid(row = 15, column = 0, sticky=W)
    name = crsr.execute("select name from passenger where document = '" + new[2] + "'").fetchall()
    lbls_w4.append(Label(win1, text="Пассажир: " + name[0][0] + " (документ " + str(new[2]) + ")", font = ("Segoe UI", 12)))
    lbls_w4[2].grid(row = 16, column = 0, sticky=W)
    lbls_w4.append(Label(win1, text="Вылет: " + str(flight_inf[3]) + " " + str(flight_inf[4])+ " " + str(flight_inf[5]), font = ("Segoe UI", 12)))
    lbls_w4[3].grid(row = 17, column = 0, sticky=W)
    lbls_w4.append(Label(win1, text="Прибытие: " + str(flight_inf[6]) + " " + str(flight_inf[7])+ " " + str(flight_inf[8]), font = ("Segoe UI", 12)))
    lbls_w4[4].grid(row = 18, column = 0, sticky=W)
    win1.mainloop()

open_win()
con.commit()
con.close()
