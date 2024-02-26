from seleniumbase import Driver
driver = Driver(uc=True)
try:
    driver.get("https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePage_false_0&formSourceTag=112&newSearchFromOverviewPage=true&inventorySearchWidgetType=AUTO&entitySelectingHelper.selectedEntity=&entitySelectingHelper.selectedEntity2=&zip={}&distance=100&searchChanged=true&modelChanged=true&filtersModified=true")
    driver.sleep(4)

finally:
    driver.quit()