# Unit Testing

Unit Testing is a software testing method in which individual units or components of a software application (such as functions, methods, or classes) are tested in isolation to verify that they work correctly as expected.
* It helps to find and fix defects at the very beginning of the developement cycle, reducing the cost and effort of debugging later.
* It promptes writing modular, clearn and maintainable code by ensuring each small part of the application behaves correctly on it's own.

# Types of Unit Testing
Unit Testing can be performed manually or automatically.

## Manual Unit Testing

Manual Testing involves develpers testing individual code unit manullay without using automation tools. It is not commonly used for large scale testing, but it can be useful during debugging and initial verificaton of code logic.
* Developers may manually verify small units of code during debugging or early development.
* It is useful for quick checks when writing or fixing specific functions.
* However, it is not scalable and becomes inefficient for repeated testing.
* Automated unit testing is preferred for consistency, speed, and long-term maintainability.

## Automated Unit Testing

Automated Unit Testing checks software functionality automatically using testing tools and frameworks, reducing manual effort and improving accuracy. Developers write small test cases to validate individual functions automatically during development. These test cases verify whether the function behaves as expected under different conditions.
* Test Focus on single units, run in memory, and do not depend on external systems.
* Automated unit tests are commonly integrated into build and CI/CD pipelines to ensure conditions code qualtiy.


# Architecture of Unit Testing
Unit Testing Architecture defines the structured approach used to design and organize unit tests, ensuring that individual components are tested in isolation for correctness and reliability.


## Components of Unit Testing Architecture

### Test Isolation & Dependencies
Each unit is tested in complete isolation from external systems such as databases, APIs, and file systems. To achieve this, mocks, stubs, or fakes are used to simulate dependencies so that only the internal logic of the unit is tested.

### AAA Pattern(Arrange-ACT-Assets)
A widely used structure for writing clean and readable unit test:
* Arrange: Prepare test data, objects and required mocks.
* Act: Execute the function or method beign tested.
* Assert: Verify that the output or behavior matches the expected result.

This architecture focuses on modular design and isolated testing of individual components using structured approaches like the AAA pattern. Since unit tests run quickly (often in milliseconds), they provide rapid feedback to developers.

# Unit Testing Strategies
To create effective unit tests the following techniques are commonly used:
* Logic Checks:  Verify that calculations are correct and all logical paths in the code are executed as expected.
* Boundary Checks: Test normal, edge, and invalid inputs to ensure the system handles limits correctly.
* Error Handaling: Ensure the system responds properly to errors instead of crashing.
* Object-Oriented Checks: Confirm that object states are correctly updated after method execution.

# Unit Testing Techniques

## Black Box Testing: 
Black Box Testing is a technique where the system is tested based on inputs and expected outputs without any knowledge of internal code or logic. It focuses on validating functionality from a user’s perspective and ensures the system behaves correctly for given inputs.


## White Box Testing:
White Box Testing is a technique where the internal structure, logic, and code of the application are tested. It ensures that all code paths, conditions, and statements work correctly as expected.

## Gray Box Testing:
Gray Box Testing is a technique that combines both black box and white box testing approaches, where the tester has partial knowledge of the internal system. It helps in testing both functionality and some internal behaviors of the application.