# Recommendations for future contributions to the code base

## Python

  - Follow Python style naming and comments, don't invent your own
    naming scheme, see PEP-8
  - avoid cyclic module dependencies
  - avoid global state variables
  - test for multiple browsers and input formats
  - avoid comments that repeat what the function name should say anyways,
    instead try to find good, self-documenting names for functions, classes
    and modules
  - avoid Java-isms, there is no need to have a class for everything and there
    is nothing wrong about putting multiple small classes into a single file
  - if you do nothing in a an exception handler except re-raising the exception
    you can as well omit the except clause, finally can stand by itself

## Javascript

  - when writing your own Javascript modules in a separate files always
    your functions in a namespace, using the  !!!! Placing them in the global
    namespace will only mean an endless sea of pain
  - don't go wild with the Javascript libraries, simpler and less dependencies
    is usually better
  - don't assume URL's in Javascript files, this makes it much harder to
    change and adapt to different environments
  - check for null or undefined, not doing so can lead to weird website
    behavior
