import re
import cx_Oracle


if __name__ == '__main__':
    db = cx_Oracle.connect('DEMO', 'DEMO', '192.168.0.23:1522/helowin')

    file = open("/Users/geminit/Desktop/百度地图项目/BDMAP_DB_BACKUP/DEMO_BOUNDARY.sql")
    for line in file.readlines():
        line = line.strip()
        m = re.match(".*?\'(.*?)\', \'(.*?)\'.*", line)
        id = m.group(1)
        boundary = m.group(2)
        cr = db.cursor()
        cr.setinputsizes(PATH=cx_Oracle.CLOB)
        cr.execute("insert into BOUNDARY (ID, PATH) values ('" + id + "', :PATH)", PATH=boundary)
        cr.close()
        db.commit()

    db.close()

    print("over")
