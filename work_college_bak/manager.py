import sqlite3 as sl
from tkinter import *
from tkinter import ttk
from functools import partial

con = sl.connect('a.db')
crsr = con.cursor()

#создание таблиц
crsr.execute("create table if not exists airplane(model text primary key, type text, max_dist integer, seats integer, count integer)")
crsr.execute("create table if not exists airport(iata_code text primary key, name text, city text)")
crsr.execute("create table if not exists airline(name text primary key, country text)")
crsr.execute("create table if not exists reis(num text primary key, price integer, plane text, airport_dep text, airport_ar text, airline text, foreign key (plane) references airplane(model) on delete cascade on update cascade, foreign key (airport_dep) references airport(iata_code) on delete cascade on update cascade, foreign key (airport_ar) references airport(iata_code) on delete cascade on update cascade, foreign key (airline) references airline(name) on delete cascade on update cascade)")
crsr.execute("create table if not exists flight(u_num text primary key, ar_date date, ar_time time, dep_date date, dep_time time, num_reis text, foreign key (num_reis) references reis(num) on delete cascade on update cascade)")
crsr.execute("create table if not exists passenger(document text primary key, name text, birth date, sex text, email text)")
crsr.execute("create table if not exists ticket(num integer primary key, seat text, pas_doc text, flight_num text, foreign key (pas_doc) references passenger(document) on delete cascade on update cascade, foreign key (flight_num) references flight(u_num) on delete cascade on update cascade)")

#занесение данных в таблицу
crsr.execute("insert into airplane values ('737-200', 'Boeing', 3000, 130, 3)")
crsr.execute("insert into airplane values ('737 MAX 10', 'Boeing', 6000, 230, 3)")
crsr.execute("insert into airport values ('LED', 'Pulkovo', 'Saint Petersburg')")
crsr.execute("insert into airport values ('DME', 'Domodedovo', 'Moscow')")
crsr.execute("insert into airline values ('Aeroflot', 'Russia')")
crsr.execute("insert into airline values ('Ural Airlines', 'Russia')")
crsr.execute("insert into flight values ('1', '2020-01-03', '15:00', '2020-01-03', '13:00', 'AF112')")
crsr.execute("insert into flight values ('2', '2020-01-05', '17:00', '2020-01-05', '15:00', 'UA015')")
crsr.execute("insert into reis values ('AF112', 3000, '737-200', 'LED', 'DME', 'Aeroflot')")
crsr.execute("insert into reis values ('UA015', 5000, '737 MAX 10', 'DME', 'LED', 'Ural Airlines')")
crsr.execute("insert into passenger values ('1111 222222', 'Ivanov Ivan Ivanovich', '2000-07-30', 'Male', 'iviviv@mail.ru')")
crsr.execute("insert into ticket values (152, '32A', '1111 222222', '1')")

'''
#данные из всех таблиц
crsr.execute("select * from airplane")
print(crsr.fetchall())
crsr.execute("select * from airport")
print(crsr.fetchall())
crsr.execute("select * from airline")
print(crsr.fetchall())
crsr.execute("select * from flight")
print(crsr.fetchall())
crsr.execute("select * from reis")
print(crsr.fetchall())
crsr.execute("select * from ticket")
print(crsr.fetchall())
crsr.execute("select * from passenger")
print(crsr.fetchall())
'''


def add_table(tab, headings, rows):
    table = ttk.Treeview(tab, show="headings", selectmode="extended")
    table["columns"]=headings
    table["displaycolumns"]=headings
    for head in headings:
        table.heading(head, text=head, anchor=CENTER)
        table.column(head, minwidth = 0, width=150, anchor=CENTER, stretch = NO)
    for row in rows:
        table.insert('', END, values=tuple(row))
    return table

def add_all_labels(tab, columns):
    lbls = []
    lbls.append(Label(tab, text="Добавить:", font = ("Segoe UI", 14)))
    for i in range(0, len(columns)):
        lbls.append(Label(tab, text=columns[i]+":"))
    lbls.append(Label(tab, text="Удалить:", font = ("Segoe UI", 14)))
    for i in range(len(lbls)):
        lbls[i].grid(row=i, column=0, sticky=W)
    lbls[len(lbls)-1].grid(row=0, column=3, sticky=W)
    lbls.append(Label(tab, text = "(выберите нужную строку"))
    lbls[len(lbls)-1].grid(row=1, column=3, sticky=W)
    lbls.append(Label(tab, text = " и нажмите кнопку):"))
    lbls[len(lbls)-1].grid(row=2, column=3, sticky=W)
    return lbls

def add_all_entries(tab, c):
    entrs = []
    for i in range(c):
        entrs.append(Entry(tab, textvariable=StringVar()))
        entrs[i].grid(row=i+1, column=1)
    return entrs

def values_tuple(colname, tablename):
    a = crsr.execute("select distinct " + colname + " from " + tablename).fetchall()
    cmb=[]
    for i in range(len(a)):
        for j in range(len(a[i])):
            cmb.append(a[i][j])
    return tuple(cmb)

def add_all_entries_and_comboboxes(tab, cmb):
    mas = []
    for i in range(len(cmb)):
        if cmb[i] == 0:
            mas.append(Entry(tab, textvariable=StringVar()))
        else:
            mas.append(ttk.Combobox(tab))
            mas[i]['values'] = cmb[i]
        mas[i].grid(row = i+1, column = 1)
    return mas

def del_data(tab_control, table, tablename, keyname):
    for selection in table.selection():
        item = table.item(selection)
        key = item["values"][0]
        table.delete(selection)
        sql = "delete from " + tablename + " where " + keyname + " = '" + str(key) + "'"
        crsr.execute(sql)
        tabs = []
        for i in tab_control.tabs():
            tabs.append(tab_control.nametowidget(i))
        for tab in tabs:
            tab.destroy()
        cr_tabs(tab_control)
    return
    
def ins_data(tab_control, table, entries, tablename):
    row = []
    for i in range(len(entries)):
        row.append(entries[i].get())
    row = tuple(row)
    table.insert('', END, values=row)
    sql = "insert into " + tablename + " values " + str(row)
    crsr.execute(sql)
    tabs = []
    for i in tab_control.tabs():
        tabs.append(tab_control.nametowidget(i))
    for tab in tabs:
        tab.destroy()
    cr_tabs(tab_control)
    return

def cr_tab1(tab_control):
    tab1 = ttk.Frame(tab_control) #вкладка 1
    tab_control.add(tab1, text='Самолёты')

    airplane_data = crsr.execute("select model as 'Модель', type as 'Тип', max_dist as 'Расстояние', seats as 'Кол-во мест', count as 'Кол-во самолётов' from airplane")
    colnames = airplane_data.description
    c_names = []
    for i in colnames:
        c_names.append(i[0])
    labels_tab1 = add_all_labels(tab1, c_names) #добавление надписей
    mas1 = [0 for i in range(len(c_names))] 
    entries_tab1 = add_all_entries_and_comboboxes(tab1, mas1) #добавление текстовых полей
    table1 = add_table(tab1, c_names, airplane_data) #добавление таблицы
    table1.grid(row = len(c_names)+1, columnspan = 15)
    ins_data_table1 = partial(ins_data, tab_control, table1, entries_tab1, 'airplane') #изменение функции добавления специально для таблицы 1
    ins_but_tab1 = Button(tab1, text="Добавить", command = ins_data_table1) #добавление кнопки Добавить
    ins_but_tab1.grid(row=len(c_names), column=2, sticky=W)
    del_data_table1 = partial(del_data, tab_control, table1, 'airplane', 'model') #изменение функции удаления специально для таблицы 1
    table1_bind = table1.bind("<ButtonRelease-1>", del_data_table1) #фиксирование клика мыши на определенной строке
    del_but_tab1 = Button(tab1, text="Удалить", command = table1_bind) #добавление кнопки Удалить
    del_but_tab1.grid(row=3, column=3, sticky=W)

    return

def cr_tab2(tab_control):
    tab2 = ttk.Frame(tab_control) #вкладка 2
    tab_control.add(tab2, text='Аэропорты')

    airport_data = crsr.execute("select iata_code as 'Код ИАТА', name as 'Название', city as 'Город' from airport")
    colnames = airport_data.description
    c_names = []
    for i in colnames:
        c_names.append(i[0])
    labels_tab2 = add_all_labels(tab2, c_names) #добавление надписей
    mas2 = [0 for i in range(len(c_names))] 
    entries_tab2 = add_all_entries_and_comboboxes(tab2, mas2) #добавление текстовых полей
    table2 = add_table(tab2, c_names, airport_data) #добавление таблицы
    table2.grid(row = len(c_names)+1, columnspan = 15)
    ins_data_table2 = partial(ins_data, tab_control, table2, entries_tab2, 'airport') #изменение функции добавления специально для таблицы 2
    ins_but_tab2 = Button(tab2, text="Добавить", command = ins_data_table2) #добавление кнопки Добавить
    ins_but_tab2.grid(row=len(c_names), column=2, sticky=W)
    del_data_table2 = partial(del_data, tab_control, table2, 'airport', 'iata_code') #изменение функции удаления специально для таблицы 2
    table2_bind = table2.bind("<ButtonRelease-1>", del_data_table2) #фиксирование клика мыши на определенной строке
    del_but_tab2 = Button(tab2, text="Удалить", command = table2_bind) #добавление кнопки Удалить
    del_but_tab2.grid(row=3, column=3, sticky=W)

    return

def cr_tab3(tab_control):
    tab3 = ttk.Frame(tab_control) #вкладка 3
    tab_control.add(tab3, text='Авиакомпании')

    airline_data = crsr.execute("select name as 'Название', country as 'Страна' from airline")
    colnames = airline_data.description
    c_names = []
    for i in colnames:
        c_names.append(i[0])
    labels_tab3 = add_all_labels(tab3, c_names) #добавление надписей
    mas3 = [0 for i in range(len(c_names))] 
    entries_tab3 = add_all_entries_and_comboboxes(tab3, mas3) #добавление текстовых полей
    table3 = add_table(tab3, c_names, airline_data) #добавление таблицы
    table3.grid(row = len(c_names)+1, columnspan = 15)
    ins_data_table3 = partial(ins_data, tab_control, table3, entries_tab3, 'airline') #изменение функции добавления специально для таблицы 3
    ins_but_tab3 = Button(tab3, text="Добавить", command = ins_data_table3) #добавление кнопки Добавить
    ins_but_tab3.grid(row=len(c_names), column=2, sticky=W)
    del_data_table3 = partial(del_data, tab_control, table3, 'airline', 'name') #изменение функции удаления специально для таблицы 3
    table3_bind = table3.bind("<ButtonRelease-1>", del_data_table3) #фиксирование клика мыши на определенной строке
    del_but_tab3 = Button(tab3, text="Удалить", command = table3_bind) #добавление кнопки Удалить
    del_but_tab3.grid(row=2, column=4, sticky=W)

    return

def cr_tab4(tab_control):
    tab4 = ttk.Frame(tab_control) #вкладка 4
    tab_control.add(tab4, text='Рейсы')

    svod = crsr.execute("select reis.num as 'Номер рейса', airplane.type as 'Тип самолета', airplane.model as 'Модель самолета', airplane.seats as 'Кол-во мест', reis.airport_dep as 'Отправление из', reis.airport_ar as 'Прибытие в', reis.price as 'Стоимость билета', airline.name as 'Авиакомпания' from reis join airplane on reis.plane = airplane.model join airline on reis.airline = airline.name")
    colnames = svod.description
    svod = svod.fetchall()
    c_names = []
    for i in colnames:
        c_names.append(i[0])
    comboboxes_tab4 = [0, 1, 1, 1, 1, 1, 0, 1]
    t = values_tuple('type', 'airplane')
    comboboxes_tab4[1] = t
    t = values_tuple('model', 'airplane')
    comboboxes_tab4[2] = t
    t = values_tuple('seats', 'airplane')
    comboboxes_tab4[3] = t
    t = values_tuple('iata_code', 'airport')
    comboboxes_tab4[4] = t
    comboboxes_tab4[5] = t
    t = values_tuple('name', 'airline')
    comboboxes_tab4[7] = t
    labels_tab4 = add_all_labels(tab4, c_names) #добавление надписей
    entries_tab4 = add_all_entries_and_comboboxes(tab4, comboboxes_tab4) #добавление текстовых полей
    table4 = add_table(tab4, c_names, svod) #добавление таблицы
    table4.grid(row = len(c_names)+1, columnspan = 15)
    ins_data_table4 = partial(ins_data, tab_control, table4, entries_tab4, 'reis') #изменение функции добавления специально для таблицы 4
    ins_but_tab4 = Button(tab4, text="Добавить", command = ins_data_table4) #добавление кнопки Добавить
    ins_but_tab4.grid(row=len(c_names), column=2, sticky=W)
    del_data_table4 = partial(del_data, tab_control, table4, 'reis', 'num') #изменение функции удаления специально для таблицы 4
    table4_bind = table4.bind("<ButtonRelease-1>", del_data_table4) #фиксирование клика мыши на определенной строке
    del_but_tab4 = Button(tab4, text="Удалить", command = table4_bind) #добавление кнопки Удалить
    del_but_tab4.grid(row=3, column=3, sticky=W)

    return

def cr_tab5(tab_control):
    tab5 = ttk.Frame(tab_control) #вкладка 5
    tab_control.add(tab5, text='Перелёты')

    reis_flight = crsr.execute("select flight.u_num as 'Перелёт', reis.num as 'Номер рейса', reis.price as 'Стоимость билета', reis.airport_dep as 'Отправление из', flight.dep_date as 'Дата отправления', flight.dep_time as 'Время отправления', reis.airport_ar as 'Прибытие в', flight.ar_date as 'Дата прибытия', flight.ar_time as 'Время прибытия' from reis, flight where reis.num = flight.num_reis")
    colnames = reis_flight.description
    reis_flight = reis_flight.fetchall()
    c_names = []
    for i in colnames:
        c_names.append(i[0])
    comboboxes_tab5 = [0, 1, 0, 1, 0, 0, 1, 0, 0]
    t = values_tuple('num', 'reis')
    comboboxes_tab5[1] = t
    t = values_tuple('iata_code', 'airport')
    comboboxes_tab5[3] = t
    comboboxes_tab5[6] = t
    labels_tab5 = add_all_labels(tab5, c_names) #добавление надписей
    entries_tab5 = add_all_entries_and_comboboxes(tab5, comboboxes_tab5) #добавление текстовых полей
    table5 = add_table(tab5, c_names, reis_flight) #добавление таблицы
    table5.grid(row = len(c_names)+1, columnspan = 15)
    ins_data_table5 = partial(ins_data, tab_control, table5, entries_tab5, 'flight') #изменение функции добавления специально для таблицы 5
    ins_but_tab5 = Button(tab5, text="Добавить", command = ins_data_table5) #добавление кнопки Добавить
    ins_but_tab5.grid(row=len(c_names), column=2, sticky=W)
    del_data_table5 = partial(del_data, tab_control, table5, 'flight', 'u_num') #изменение функции удаления специально для таблицы 5
    table5_bind = table5.bind("<ButtonRelease-1>", del_data_table5) #фиксирование клика мыши на определенной строке
    del_but_tab5 = Button(tab5, text="Удалить", command = table5_bind) #добавление кнопки Удалить
    del_but_tab5.grid(row=3, column=3, sticky=W)

    return

def cr_tabs(tab_control):
    cr_tab1(tab_control)
    cr_tab2(tab_control)
    cr_tab3(tab_control)
    cr_tab4(tab_control)
    cr_tab5(tab_control)
    return

def new_window(): #работа с tkinter
    win = Tk() #создание окна для менеджера
    win.title("Менеджер")
    win.geometry('1024x1024')

    tab_control = ttk.Notebook(win) #добавление вкладок
    cr_tabs(tab_control)
    tab_control.pack(expand=1, fill='both')

    win.mainloop()
    return

new_window()
con.commit()
con.close()
