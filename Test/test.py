import cx_Oracle


if __name__ == '__main__':
    db = cx_Oracle.connect('DEMO', 'DEMO', '192.168.0.23:1521/helowin')
    cr = db.cursor()
    cr.execute("select * from MAP_POINT where ID not exists (select ID from BOUNDARY) order by ID asc")
    cr.close()
    db.commit()
    db.close()

    print("over")
