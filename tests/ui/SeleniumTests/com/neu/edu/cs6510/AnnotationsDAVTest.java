package com.neu.edu.cs6510;

import java.util.concurrent.TimeUnit;

import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;


public class AnnotationsDAVTest {

  public static final String YOUR_PASSWORD = "";
  public static final String PASSWD = "Passwd";
  public static final String SITE_NAME = "https://pf1010.systemsbiology.net/";
  public static final String EMAIL = "Email";
  public static final String LOGIN_WITH_GOOGLE = "Login with Google+";
  public static final String YOUR_GMAIL_ID = "";
  public static final String NEXT = "next";
  protected static final String SELENIUM_ACQA_SYSTEM_1 = "Selenium AcqaSystem_2";

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
    driver.get(SITE_NAME);
    // Maximize the window.
    driver.manage().window().maximize();

    driver.findElement(By.linkText(LOGIN_WITH_GOOGLE)).click();
    // Enter UserName
    driver.findElement(By.id(EMAIL)).sendKeys(YOUR_GMAIL_ID);
    // Click next
    driver.findElement(By.id(NEXT)).click();
    // Enter Password
    driver.findElement(By.id(PASSWD)).sendKeys(YOUR_PASSWORD);

    // Wait For Page To Load
    driver.manage().timeouts().implicitlyWait(60, TimeUnit.SECONDS);
    // Click on 'Sign In' button
    driver.findElement(By.id("signIn")).click();
    // Click Allow button

//    wait.until(ExpectedConditions.elementToBeClickable(By.id("submit_approve_access"))).click();
    // Till here common to all test cases.

    // Select system
    driver.findElement(By.linkText(SELENIUM_ACQA_SYSTEM_1)).click();

    // Add annotations start
    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//*[@title='Annotations']")))
        .click();
    Select select_annotation1 = new Select(driver.findElement(By.id("mySelect")));
    select_annotation1.selectByVisibleText("Fish");
    driver.findElement(By.id("changeAdd")).click();
    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//*[contains(text(), 'Submit')]")))
        .click();
    wait.until(ExpectedConditions.alertIsPresent());
    Alert alertOK = driver.switchTo().alert();
    System.out.println(alertOK.getText());
    alertOK.accept();

    Select select_annotation2 = new Select(driver.findElement(By.id("mySelect")));
    select_annotation2.selectByVisibleText("Plant");
    driver.findElement(By.id("changeAdd")).click();
    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//*[contains(text(), 'Submit')]")))
        .click();
    wait.until(ExpectedConditions.alertIsPresent());
    alertOK.accept();

    // Click Social start
    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//*[@title='Social']"))).click();
    wait.until(
        ExpectedConditions.elementToBeClickable(By.xpath("//button[@class='btn btn-blue btn-sm']")))
        .click();
    driver.findElement(By.id("new_link")).sendKeys(
        "http://science-all.com/image.php?pic=/images/plant/plant-03.jpg");
    driver.findElement(By.id("addUrl")).click();
    Select select_public = new Select(driver.findElement(By.name("privacy")));
    select_public.selectByVisibleText("Public");
    driver.findElement(By.id("new_post")).sendKeys("It's tuesday: final");
    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//input[@value='Share']")))
        .click();


     driver.close();

  }
}
