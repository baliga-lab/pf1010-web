package com.neu.edu.cs6510;

import java.util.concurrent.TimeUnit;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.seleniumhq.jetty9.util.log.Log;


public class DavSystemTest {

  public static void main(String[] args) {

    // Create a new instance of the Firefox driver
    System.setProperty("webdriver.chrome.driver", "/Users/preetymishra/chromedriver");
    WebDriver driver = new ChromeDriver();
    // WebDriver driver = new FirefoxDriver();
    WebDriverWait wait = new WebDriverWait(driver, 20);
    // Wait For Page To Load
    // Put a Implicit wait, this means that any search for elements on the page
    // could take the time the implicit wait is set for before throwing exception
    driver.manage().timeouts().implicitlyWait(50, TimeUnit.SECONDS);
    // Navigate to URL
    driver.get(AnnotationsDAVTest.SITE_NAME);
    // Maximize the window.
    driver.manage().window().maximize();

    driver.findElement(By.linkText(AnnotationsDAVTest.LOGIN_WITH_GOOGLE)).click();
    // Enter UserName
    driver.findElement(By.id(AnnotationsDAVTest.EMAIL)).sendKeys(AnnotationsDAVTest.YOUR_GMAIL_ID);
    // Click next
    driver.findElement(By.id(AnnotationsDAVTest.NEXT)).click();
    // Enter Password
    driver.findElement(By.id(AnnotationsDAVTest.PASSWD)).sendKeys(AnnotationsDAVTest.YOUR_PASSWORD);

    // Wait For Page To Load
    driver.manage().timeouts().implicitlyWait(60, TimeUnit.SECONDS);
    // Click on 'Sign In' button
    driver.findElement(By.id("signIn")).click();
    // Click Allow button

    // Not for the deployed version
//    wait.until(ExpectedConditions.elementToBeClickable(By.id("submit_approve_access"))).click();
    // Till here common to all test cases.

    wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Explore"))).click();

    Select exploreTechnique1 = new Select(driver.findElement(By.id("selectTechnique")));
    exploreTechnique1.selectByVisibleText("Ebb and Flow (Media-based)");

    Select exploreGrowbed1 = new Select(driver.findElement(By.id("selectGrowbedMedium")));
    exploreGrowbed1.selectByVisibleText("Coconut Coir");

    Select exploreCrop1 = new Select(driver.findElement(By.id("selectCrop")));
    exploreCrop1.selectByVisibleText("Chocolate Mint");

    Select exploreStatus1 = new Select(driver.findElement(By.id("selectStatus")));
    exploreStatus1.selectByVisibleText("Pre-Established");

    wait.until(ExpectedConditions.elementToBeClickable(By.id("submitbtn"))).click();
    if (driver.findElement(By.xpath("//div[@class='alert alert-danger']")).isDisplayed()) {
      Log.getLogger("No system");
      System.out.println("No system");
    } else {
      Log.getLogger("Success");
      System.out.println("Success");
    }

    // select 4 systems
    wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Explore"))).click();

    Select exploreTechnique = new Select(driver.findElement(By.id("selectTechnique")));
    exploreTechnique.selectByVisibleText("Floating Raft");

    Select exploreGrowbed = new Select(driver.findElement(By.id("selectGrowbedMedium")));
    exploreGrowbed.selectByVisibleText("Coconut Coir");

    Select exploreStatus = new Select(driver.findElement(By.id("selectStatus")));
    exploreStatus.selectByVisibleText("Pre-Established");

    wait.until(ExpectedConditions.elementToBeClickable(By.id("submitbtn"))).click();
    if (driver.findElement(By.xpath("//div[@class='alert alert-success']")).isDisplayed()) {
      Log.getLogger("Success");
      System.out.println("Success");
    } else {
      Log.getLogger("No system");
    }
    wait.until(
        ExpectedConditions.elementToBeClickable(By
            .xpath("//div[@class='chosen-container chosen-container-multi']"))).click();
    WebElement dropdown = driver.findElement(By.xpath("//*[@class='chosen-results']"));
    dropdown.findElement(By.xpath("//li[@data-option-array-index='0']")).click();

    for (int i = 0; i < 3; i++) {
      wait.until(
          ExpectedConditions.elementToBeClickable(By.xpath("//div[@id='analyzeSystem_chosen']")))
          .click();
      WebElement dropdown1 = driver.findElement(By.xpath("//*[@class='chosen-results']"));
      dropdown1.findElement(By.xpath("//li[@data-option-array-index='" + i + "']")).click();
    }
    wait.until(ExpectedConditions.elementToBeClickable(By.id("analyzebtn"))).click();

    // select 0 system
    wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Explore"))).click();
    wait.until(ExpectedConditions.elementToBeClickable(By.id("analyzebtn"))).click();
    if (driver.findElement(By.xpath("//div[@class='alert alert-danger']")).isDisplayed()) {
      Log.getLogger("No system selected");
      System.out.println("No system selected");
    }
    // Close the browser.
    driver.close();
  }
}


