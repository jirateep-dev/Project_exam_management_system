*** Variables ***

${HOSTNAME}             127.0.0.1
${PORT}                 8000
${SERVER}               http://${HOSTNAME}:${PORT}/
${BROWSER}              Chrome
${ONESECOND}      		1.0
${THREESECOND}      	3.0
${FIVESECOND}      		5.0
${TENSECOND}      		10.0
${ONEMINUTE}      		60.0
${USER}      			bundit
${PASS}      			ad123456
${DATE1}          15/05/2018
${DATE2}          16/05/2018

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

*** Test Cases ***

As a visitor I can visit the django default page
  Input Text    			name=username			${USER}
  Input Text    			name=password			${PASS}
  Click Element 			id=btn_login
  Sleep     				${ONESECOND}

visit manage_page before create schedule room
  Click Link    link=จัดห้องสอบ
  Sleep    		${ONESECOND}

export schedule_room.csv
  Click Element       id=export_panel
  Sleep       ${ONESECOND}
  Capture Page Screenshot
  Click Element       id=export_file
  Sleep       ${FIVESECOND}
  Capture Page Screenshot