*** Variables ***

${HOSTNAME}             161.246.38.112
${PORT}                 80
${SERVER}               http://${HOSTNAME}:${PORT}/
${BROWSER}              Chrome
${ONESECOND}      		1.0
${THREESECOND}      	3.0
${FIVESECOND}      		5.0
${TENSECOND}      		10.0
${ONEMINUTE}      		60.0
${USER}      			bundit
${PASS}      			ad123456
${DATE1}          29/05/2018
${DATE2}          30/05/2018

*** Settings ***

Library         	Selenium2Library  timeout=10  implicit_wait=0
Library           BuiltIn
Library           String
Suite Setup     	Start Django and open Browser
Suite Teardown    Stop Django and close Browser

*** Keywords ***

Start Django and open Browser
  Open Browser    ${SERVER}    ${BROWSER}
  Maximize Browser Window

Stop Django and close Browser
  Close Browser

Generate room
  [Arguments]    ${date}    ${room}    ${period}    ${major}
  Execute Javascript            $(document).scrollTop(${500})
  Focus                         jquery=[name=date_selected]
  Clear Element Text            xpath=//input[@name='date_selected']
  Press Key                     jquery=[name=date_selected]      ${date}

  Select From List By Label     xpath=//select[@name="room_selected"]     ${room}
  Select From List By Value     xpath=//select[@name="period_selected"]    ${period}
  Select From List By Label     xpath=//select[@name="major_selected"]    ${major}
  Click button                  สร้างตาราง

*** Test Cases ***

As a visitor I can visit the django default page
  Input Text    			name=username			${USER}
  Input Text    			name=password			${PASS}
  Click Element 			id=btn_login
  Sleep     				${ONESECOND}

visit manage_page before create schedule room
  Click Link    link=จัดห้องสอบ
  Sleep    		${ONESECOND}

check result for create 1 room and 1 period time in schedule_room
  Execute Javascript    $(document).scrollTop(${500})
  Click button                  ล้างข้อมูล

  Focus                         jquery=[name=date_selected]
  Clear Element Text            xpath=//input[@name='date_selected']
  Press Key                     jquery=[name=date_selected]      ${DATE1}

  Select From List By Label     xpath=//select[@name="room_selected"]     M03
  Select From List By Value     xpath=//select[@name="period_selected"]    0
  Select From List By Label     xpath=//select[@name="major_selected"]    Software Development

  Capture Page Screenshot
  Click button                  สร้างตาราง
  Capture Page Screenshot

create schedule room

  Generate room      ${DATE1}      M04      0      Software Development
  Generate room      ${DATE1}      M03      1      Software Development
  Generate room      ${DATE1}      M04      1      Software Development
  Generate room      ${DATE1}      M21      0      Multimedia
  Generate room      ${DATE1}      M21      1      Multimedia
  Generate room      ${DATE1}      M22      0      Network and Communication
  Generate room      ${DATE1}      M23      0      Data Science

  Generate room      ${DATE2}      M03      0      Business Intelligence
  Generate room      ${DATE2}      M03      1      Business Intelligence
  Generate room      ${DATE2}      M04      1      Embedded Systems
  Generate room      ${DATE2}      M04      0      Data Science
  Generate room      ${DATE2}      M21      0      Data Science
  Generate room      ${DATE2}      M21      1      Data Science
  Generate room      ${DATE2}      M21      1      Multimedia
  Generate room      ${DATE2}      M22      0      Multimedia
  Generate room      ${DATE2}      M22      1      Software Development
  Generate room      ${DATE2}      M23      0      Embedded Systems
  Generate room      ${DATE2}      M23      0      Software Development
  Generate room      ${DATE2}      M21      0      Business Intelligence
  Generate room      ${DATE2}      M23      1      Network and Communication

  Execute Javascript    $(document).scrollTop(${500})
  Capture Page Screenshot
  Click button                  โครงงานที่ยังไม่ถูกจัด
  Execute Javascript    $(document).scrollTop(${1500})
  Capture Page Screenshot
  Sleep     						        ${FIVESECOND}

visit table_room page and check table schedule room
  Click Link    link=ตารางการจัดห้องสอบ
  Execute Javascript    $(document).scrollTop(${200})
  Capture Page Screenshot
  Click Link    link=ตารางการสอบโปรเจค
  Sleep             ${THREESECOND}
  Capture Page Screenshot
