from selenium import webdriver # Functional testing using selenium
from selenium.webdriver.support.ui import Select # Select class to work with select tags


driver = webdriver.Firefox()
driver.get("http://127.0.0.1:5000/dav/explore")

# Start on explore page
# Select checkboxes
checkboxISB1 = driver.find_element_by_id('2e79ea8a411011e5aac7000c29b92d09').click()
checkBoxISB3 = driver.find_element_by_id('03b0e3345af711e589b2000c29b92d09').click()
print "selecting ISB 1 & 3..."

# Click analyze and redirect to analyze page
analyzeButton = driver.find_element_by_id('analyzebtn').click()
print 'Analyze button clicked'

# On analyze page:
# Read x-axis
xAxis = Select(driver.find_element_by_id('selectXAxis'))
print 'Reading x-axis options'

# Select "time" for x-axis
timeSelect = xAxis.select_by_visible_text('Time')
print 'Time selected for x-axis'

# Multi-select options for y-axis
hardness = driver.find_element_by_xpath('//*[@id="selectYAxis"]/option[3]').click()
pH = driver.find_element_by_xpath('//*[@id="selectYAxis"]/option[6]').click()
print 'selecting multiple y-axis options'

# Select type of graph
graphType = Select(driver.find_element_by_id('selectGraphType'))
scatterPlot = graphType.select_by_value('scatter')
print 'Scatter plot selected...'

# Click on submit button of analyze page
submitButton = driver.find_element_by_id('submitbtn').click()
print 'Clicking submit'

# close window
driver.quit()
