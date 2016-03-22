from selenium import webdriver # Functional testing using selenium
from selenium.webdriver.support.ui import Select # Select class to work with select tags


driver = webdriver.Firefox()
driver.get("http://127.0.0.1:5000/dav/explore")

# On explore page:
# Reading dropdowns
dropdown1 = Select(driver.find_element_by_id('selectTechnique'))
dropdown2 = Select(driver.find_element_by_id('selectOrganism'))
dropdown3 = Select(driver.find_element_by_id('selectCrop'))
dropdown4 = Select(driver.find_element_by_id('selectGrowbedMedium'))
print 'Reading dropdowns...'

# Select items from dropdown
dropdown1.select_by_visible_text('Floating Raft')
dropdown3.select_by_visible_text('Strawberry')
print 'Selecting items from dropdowns...'

# Submit the selections
submitButton = driver.find_element_by_id('submitbtn').click()
print 'Clicking submit'

# Reset all the selections
resetButton = driver.find_element_by_id('resetbtn').click()
print 'Page reset'

# close window
driver.quit()