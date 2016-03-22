*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
Library           Selenium2Library

*** Variables ***
${SERVER}         127.0.0.1:5000 
${BROWSER}        Firefox
${DELAY}          0
${VALID USER}     demo
${VALID PASSWORD}    mode
${WELCOME URL}    http://${SERVER}/ui/ui-index
${ABOUT URL}      http://${SERVER}/ui/about
${EXPLORE URL}    http://${SERVER}/ui/explore
${NEWSFEED URL}   http://${SERVER}/ui/newsfeed
${ERROR URL}      http://${SERVER}/error.html

*** Keywords ***
Open Browser To Project Feed 1010
    Open Browser    ${WELCOME URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Project Feed 1010 Should Be Open

Project Feed 1010 Should Be Open
    Location Should Be    ${WELCOME URL}
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

Newsfeed Should Be Open
    Title Should Be    Newsfeed

Go To Newsfeed
    Go To    ${NEWSFEED URL}
    Newsfeed Should Be Open

