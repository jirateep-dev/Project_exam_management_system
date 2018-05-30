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
![add connection](https://firebasestorage.googleapis.com/v0/b/testproject-da832.appspot.com/o/Senior_project%2Fconectrion.jpg?alt=media&token=52261261-5b90-412f-b193-1fabedcb61b2)
* หลังจากนั้นทำการ import database จากแถบด้านซ้ายมือ คลิก Data import/Restore <br />
![import](https://firebasestorage.googleapis.com/v0/b/testproject-da832.appspot.com/o/Senior_project%2Fimport.jpg?alt=media&token=e4d8330d-c2f5-48eb-a765-0a4cd5f47840)
* ทำการเลือกไฟล์ senior_proj.sql ในตัวโปรเจคทำการ import เข้ามา <br />
![import](https://firebasestorage.googleapis.com/v0/b/testproject-da832.appspot.com/o/Senior_project%2Fimport2.jpg?alt=media&token=760ec858-ba69-464c-8554-86fa579f0885)

<br />

## Run project 
เข้าไปใน path project จากนั้น run คำสั่ง
```
python manage.py runserver
```
<br />

## FACET
สำหรับโปรแกรม FACET <br />
สามารถ download และติดตั้งตามขั้นตอนได้ที่ลิ้ง <br />
* [https://www.winsteps.com/minifac.htm](https://www.winsteps.com/minifac.htm)
