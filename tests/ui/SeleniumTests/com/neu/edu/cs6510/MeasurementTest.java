package com.neu.edu.cs6510;

import java.util.concurrent.TimeUnit;

import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;


public class MeasurementTest {



  public static final String SELENIUM_ACQA_SYSTEM = "Selenium AcqaSystem_2";
  public static final String SUBMIT_APPROVE_ACCESS = "submit_approve_access";
  public static final String SELENIUM_TEST_FOR_NEW_POST_TEST_3 =
      "Selenium test for new post test 3";

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

//    wait.until(ExpectedConditions.elementToBeClickable(By.id(SUBMIT_APPROVE_ACCESS))).click();
    // Till here common to all test cases.


    // Test for posting new post as public start
    driver.findElement(By.id("new_post")).sendKeys(SELENIUM_TEST_FOR_NEW_POST_TEST_3);
    Select select = new Select(driver.findElement(By.name("privacy")));
    select.selectByVisibleText("Public");
    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//*[contains(text(), 'Share')]")))
        .click();
    // Test for posting new post as public end

    // Create system start
    driver.findElement(By.linkText("Create")).click();
    driver.findElement(By.xpath("//input[@placeholder='System Name']")).sendKeys(
        SELENIUM_ACQA_SYSTEM);
    driver.findElement(By.xpath("//input[@placeholder='Address']")).sendKeys(
        "401 Terry Ave N, Seattle, WA 98109");
    driver.findElement(By.linkText("Get Coordinates")).click();
    driver.findElement(By.linkText("Get Coordinates")).click();
    driver.findElement(By.xpath("//*[@ng-model='system.startDate']")).sendKeys("04/30/2016");


    Select selectd1 =
        new Select(driver.findElement(By.xpath("//select[@ng-model='system.techniqueID']")));
    selectd1.selectByVisibleText("Ebb and Flow (Media-based)");

    Select selectd3 =
        new Select(driver.findElement(By.xpath("//select[@ng-model='system.gbMedia[0].ID']")));
    selectd3.selectByVisibleText("Clay Pebbles");

    Select selectd4 =
        new Select(driver.findElement(By.xpath("//select[@ng-model='system.crops[0].ID']")));
    selectd4.selectByVisibleText("Strawberry");
    driver.findElement(By.xpath("//input[@ng-model='system.crops[0].count']")).sendKeys("2");

    Select selectd5 =
        new Select(driver.findElement(By.xpath("//select[@ng-model='system.organisms[0].ID']")));
    selectd5.selectByVisibleText("Nile Tilapia");
    driver.findElement(By.xpath("//input[@ng-model='system.organisms[0].count']")).sendKeys("2");

    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//button[@class='btn btn-green']")))
        .click();
    // create system end

    // input measurement start
    Select select_measurement1 =
        new Select(driver.findElement(By.xpath("//select[@ng-model='measure.measurement_id']")));
    select_measurement1.selectByVisibleText("Ammonium");

    WebElement dateBox = driver.findElement(By.xpath("//input[@ng-model='measure.datetime']"));
    // Fill date as mm/dd/yyyy as 09/25/2013
    dateBox.sendKeys("04/25/2016");
    // Press tab to shift focus to time field
    dateBox.sendKeys(Keys.TAB);
    // Fill time as 02:45 PM
    dateBox.sendKeys("02:45PM");
    driver.findElement(By.xpath("//input[@ng-model='measure.value']")).sendKeys("0.5");
    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//*[contains(text(), 'Submit')]")))
        .click();

    Select select_measurement2 =
        new Select(driver.findElement(By.xpath("//select[@ng-model='measure.measurement_id']")));
    select_measurement2.selectByVisibleText("Light");

    WebElement dateBox1 = driver.findElement(By.xpath("//input[@ng-model='measure.datetime']"));
    // Fill date as mm/dd/yyyy as 09/25/2013
    dateBox1.sendKeys("04/25/2016");
    // Press tab to shift focus to time field
    dateBox1.sendKeys(Keys.TAB);
    // Fill time as 02:45 PM
    dateBox1.sendKeys("02:45PM");

    driver.findElement(By.xpath("//input[@ng-model='measure.value']")).sendKeys("123.3");
    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//*[contains(text(), 'Submit')]")))
        .click();

    // Add measurement end


   // Close the browser.
    driver.close();
  }
}
