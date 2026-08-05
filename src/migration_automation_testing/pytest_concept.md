#### Fixture, Marker, Parametrize

1. Fixtures – "Prepare everything my test needs"

### Definition:

A fixture is a reusable setup function that creates or prepares the resources a test needs before it runs.

### Why do we need fixtures?

Imagine you have 30 tests, and every one of them needs:

A source DataFrame
A target DataFrame
A database connection
A temporary file
An API client

Without fixtures, you would recreate those objects in every test, leading to duplicated code that is harder to maintain.

Instead, we create the setup once in a fixture and let Pytest inject it into any test that requests it.

### Think about our migration project

Suppose every validation test needs the same source dataset.

Without a fixture:

def test_row_count():
    source_df = load_csv("customers.csv")
def test_null_validation():
    source_df = load_csv("customers.csv")
def test_duplicate_validation():
    source_df = load_csv("customers.csv")

The same setup is repeated.

With a fixture:

@pytest.fixture
def source_df():
    return load_csv("customers.csv")

Now every test simply asks for it:

def test_row_count(source_df):
def test_duplicate_validation(source_df):

Pytest automatically creates the DataFrame and passes it to the test.


A fixture is not a test.

It is reusable test preparation.

Use fixtures whenever multiple tests require the same setup.
### PARAMETRIZE

2. Parametrize – "Run the same test with different data"

Definition:

Parametrize allows one test function to run multiple times using different inputs and expected results.

Why do we need it?

Suppose we're testing row-count validation.

Our business rule is simple:

Same row count → PASS
Different row count → FAIL

But we shouldn't test only one scenario.

We should test many.

Source	Target	Expected
3	3	PASS
3	4	FAIL
4	3	FAIL
0	0	PASS

Without parametrize, we'd write four almost identical test functions.

With parametrize, we write one test template, and Pytest executes it once for each row of test data.

@pytest.mark.parametrize(...)
def test_row_count(...):

Pytest effectively performs:

Run test using case 1

↓

Run test using case 2

↓

Run test using case 3

↓

Run test using case 4
Senior QA mindset

Parametrize removes duplicated tests by changing only the input data.

Use it whenever the logic stays the same but the inputs change.

3. Markers – "Organise and control your tests"

Definition:

A marker is metadata attached to a test that tells Pytest something about that test or how it should be executed.

Think of a marker as putting a label on a file.

Examples:

Smoke

Regression

Database

API

Slow

Skip

The marker doesn't change the business logic of the test.

It simply classifies or controls it.

Example:

@pytest.mark.smoke
def test_login():

Now Pytest knows this belongs to the smoke test suite.

You can run only smoke tests:

pytest -m smoke

Or perhaps:

@pytest.mark.skip

which tells Pytest:

Don't execute this test.

Or:

@pytest.mark.xfail

which tells Pytest:

This test is expected to fail because of a known issue.

### Senior QA mindset

Markers help organise, filter, and control how tests are executed.

Use markers when you want to:

group tests,
skip tests,
mark known failures,
or apply special execution behaviour.
How they work together in a real project

Imagine you're testing customer data migration.

Fixture
@pytest.fixture
def source_df():

Creates the customer dataset.

Parametrize
@pytest.mark.parametrize(...)

Runs the same validation against several migration scenarios.

Marker
@pytest.mark.regression

Labels this as a regression test so it can be run separately from smoke tests.

## Runing tests in python pytest

### Run every test
1. Running every test

From the project root:

pytest

or

python -m pytest

Pytest searches for all files named:

test_*.py
*_test.py

and runs every test it finds.

Example output:

=================== test session starts ===================

test_row_count.py .....
test_duplicate.py ...
test_nulls ....
test_profile ....

==================== 16 passed ============================

##  Run a single test file

2. Run a single test file

If you only want to run your row count tests:

pytest tests/test_row_count.py

or

python -m pytest tests/test_row_count.py

Pytest ignores every other file.

#### Run one specific test function
3. Run one specific test function

Suppose your file contains:

def test_row_count_match():
    ...

def test_target_has_more_rows():
    ...


Run:

pytest tests/test_row_count.py::test_row_count_match

Only this function runs.

### Run a specific test class

4. Run a specific test class

Suppose you have:

class TestRowCount:

    def test_match(self):
        ...

    def test_fail(self):
        ...

Run:

pytest tests/test_row_count.py::TestRowCount

It runs every test inside that class.

#### Run one method inside a class

5. Run one method inside a class
pytest tests/test_row_count.py::TestRowCount::test_match

Only that single method runs.

### Run only smoke tests

6. Run only smoke tests

If you have:

@pytest.mark.smoke
def test_login():

Run:

pytest -m smoke

#### Run everything except smoke tests
7. Run everything except smoke tests
pytest -m "not smoke"


### Decorator
A decorator is a function that extend the behaviour of another function w/o modifying the base function. We pass the base function as an argument to the decorator.