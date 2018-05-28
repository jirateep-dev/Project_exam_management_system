# Project_exam_management_system
ระบบจัดสอบวิชาโครงงาน ภาคเรียนที่ 1 และ 2
## Getting Started
clone โปรเจคนี้และ run
```
pip install -r requirements.txt
```
<br />

## Setting Database
ใช้ MySQL ในการจัดการ database<br />
ในโปรเจคถ้าใช้ MySQL Workbench6.3 CE ในการจัดการให้ทำตามขั้นตอนดังนี้
* ทำการ add connection ก่อนและสร้าง schema ชื่อ senior_db ขึ้นมา <br />
![add connection](https://github.com/s7070018/Project_exam_management_system/blob/master/wiki%20images/database/conectrion.jpg)
* หลังจากนั้นทำการ import database จากแถบด้านซ้ายมือ คลิก Data import/Restore <br />
![import](https://github.com/s7070018/Project_exam_management_system/blob/master/wiki%20images/database/import.jpg)
* ทำการเลือกไฟล์ senior_proj.sql ในตัวโปรเจคทำการ import เข้ามา <br />
![import](https://github.com/s7070018/Project_exam_management_system/blob/master/wiki%20images/database/import2.jpg)

<br />

## Run project 
เข้าไปใน path project จากนั้น run คำสั่ง
```
python manage.py runserver
```
