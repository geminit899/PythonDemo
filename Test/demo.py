import re
import pymysql

if __name__ == '__main__':
    db = pymysql.connect(host="192.168.0.23", port=3306, user="root", password="C/hEz8ygYA4g459j/TsQHg==htdata", database="ddh_sbztjk_prod")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM base_device_info where location is null and system_struct_id >= 84 and system_struct_id <= 85")
    data = cursor.fetchall()

    file = open(r'C:\Users\geminit\Desktop\mock.js', 'r')
    i = 0
    for line in file.readlines():
        line = line.strip()
        m = re.match(".*?\'location\': \'(.*?)\'.*", line)
        location = m.group(1)
        row = data[i]
        row_id = row[0]
        cursor.execute("update base_device_info set type=%s, location=%s where id=%s", ('WX_CD', location, row[0]))
        i += 1

    cursor.close()
    db.commit()
    db.close()
