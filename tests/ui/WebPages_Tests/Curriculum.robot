*** Settings ***
Documentation     A test suite with a single test to explore page from home page.
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot

*** Test Cases ***
Valid Project Feed 1010
    Open Browser To Project Feed 1010
    Project Feed 1010 Should Be Open
    Go To Curriculum
    [Teardown]    Close Browser