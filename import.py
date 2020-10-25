import pymysql
import re


db = pymysql.connect("localhost","root","123456")
cursor = db.cursor()
cursor.execute("use EDict;")
with open("dict.txt", "r") as f:
    data = f.readlines()
    for i in data:
        if len(re.findall("^[a-z]{1}", i)) == 1:
            word = re.findall(r"^[A-Z]*[a-z]*\b", i)
            word = word[0]
            meaning = i[len(word):]
            meaning = meaning.replace("\"", "w")
            meaning = meaning.replace("\'", "w")
            space = re.findall("^\s*", meaning)[0]
            meaning = meaning[len(space):]
            commandline = "insert into dictionary(words,meaning) values(\"%s\",\"%s\")"%(word, meaning)
            # print(commandline)
            try:
                cursor.execute(commandline)
                db.commit()
            except(Exception):
                db.rollback()

            # db.commit()
        else:
            continue

cursor.close()
db.close()
