import sqlite3
conn = sqlite3.connect('my_db.sqlite3')
curs = conn.cursor()

curs.execute('''CREATE TABLE users (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  first_name  TEXT NOT NULL,
  last_name  TEXT NOT NULL,
  name  TEXT NOT NULL,
  email  TEXT NOT NULL,
  passw TEXT NOT NULL
  )''')

conn.commit()

curs.execute('''INSERT INTO 'users' 
               (first_name,last_name,name,email,passw)  
               VALUES 
               ('Volodymyr','Husak','Lodko','vovatrap@gmail.com','1q2w3e4r5t')''')

conn.commit()
conn.close()