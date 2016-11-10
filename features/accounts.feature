Feature: The banking system service back-end
  As a Banking System Owner
  I need a RESTful service
  So that I can Create, Read, Update, Delete, List, Query, Deactivate accounts

  Background:
    Given the server is started

  Scenario: The server is running
    When I visit the "home page"
    Then I should see "Banking System REST API Service"
    Then I should not see "404 Not Found"

  Scenario: Create a new account
    When I post a new account to '/accounts'
      | name          | balance  | active |
      | alex          | 10   | 1          |
    Then I should see 'alex' with balance '10' and active: '1'

  Scenario: List all accounts
    Given the following accounts
      | id | name |  balance | active|
      | 1  |  Xi  |  1000    | 1     |
      | 2  | john |   980    | 1     |
      | 3  | Gina |  20000   | 1     |
      | 4  |  Xi  |  20000   | 1     |
    When I visit '/accounts'
    Then I should see '1'
    And I should see '2'
    And I should see '3'
    And I should see '4'

  Scenario: Search accounts of given name
    Given the following accounts
      | id | name |  balance | active|
      | 1  |  Xi  |  1000    | 1     |
      | 2  | john |   980    | 1     |
      | 3  | Gina |  20000   | 1     |
      | 4  |  Xi  |  20000   | 1     |
    When I search for 'Xi'
    Then I should see '1'
    And I should see '4'