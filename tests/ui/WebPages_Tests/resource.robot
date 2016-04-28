*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
Library           Selenium2Library

*** Variables ***
${SERVER}         pf1010.systemsbiology.net
${BROWSER}        Firefox
${DELAY}          0
${VALID USER}     demo
${VALID PASSWORD}    mode
${WELCOME URL}    https://${SERVER}
${ABOUT URL}      https://${SERVER}/about
${EXPLORE URL}    https://${SERVER}/dav/explore
${CURRICULUM URL}   https://${SERVER}/curriculum
${RESOURCES URL}   https://${SERVER}/resources

*** Keywords ***
Open Browser To Project Feed 1010
    Open Browser    ${WELCOME URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Project Feed 1010 Should Be Open

Project Feed 1010 Should Be Open
    Title Should Be    Project Feed 1010

About Should Be Open
    Title Should Be    About

Go To About
    Go To    ${ABOUT URL}
    About Should Be Open

Explore Should Be Open
    Title Should Be    Explore

Go To Explore
    Go To    ${EXPLORE URL}
    Explore Should Be Open

Curriculum Should Be Open
    Title Should Be    Curriculum

Go To Curriculum
    Go To    ${CURRICULUM URL}
    Curriculum Should Be Open

Resources Should Be Open
    Title Should Be    Resources

Go To Resources
    Go To    ${RESOURCES URL}
    Resources Should Be Open
