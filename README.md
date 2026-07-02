# Cloud Migration Validation Framework

## Objective

This project demonstrates automated validation of cloud data migrations between AWS and GCP.

It validates:

- Schema parity
- Row count parity
- Duplicate detection
- Null validation
- Hash comparison
- File validation
- Image validation
- Video validation
- Metadata validation
- Bronze/Silver/Gold validation

I built a cloud migration validation framework that simulates AWS-to-GCP data migration. It validates schemas, row counts, nulls, duplicates, checksums, image and video integrity, and generates evidence reports. I built it in Python, SQL, and PySpark using a modular architecture because I wanted to deepen my understanding of the exact challenges involved in migration validation.

### DATA VALIDATION PILLARS

We have 8 validation pillars**, which are also common in industry.

# 1. Data Profiling (Understand the data), we called it data overview in DS

This happens **before** validation.

Checks include:

* Number of rows
* Number of columns
* Column names
* Data types
* Memory usage
* Missing values
* Percentage of missing values
* Duplicate rows
* Duplicate primary keys
* Unique values per column
* Numeric summary (min, max, mean, std)
* Categorical summary
* Sample records
* Statistics Summary  and many more

**Output:** "What does my dataset look like?"

---

# 2. Schema Validation

Checks:

* Column names match
* Column order (if required)
* Data types match
* Required columns exist
* Unexpected columns
* Nullable vs non-nullable columns
* Schema drift

Example:

Source

```
CustomerID INT
```

Target

```
CustomerID STRING
```

❌ Fail

---

# 3. Completeness Validation

Checks:

* Null values
* Empty strings
* Missing files
* Missing records
* Missing partitions
* Missing images
* Missing videos
* Missing metadata

Example:

```
Customer Name = NULL
```

---

# 4. Uniqueness Validation

Checks:

* Duplicate rows
* Duplicate primary keys
* Duplicate business keys
* Duplicate filenames
* Duplicate image IDs

Example:

```
ProductID

1101

1101
```

❌ Duplicate

---

# 5. Validity Validation

Checks:

* Correct data types
* Valid dates
* Valid email format
* Valid phone numbers
* Valid country codes
* Numeric columns contain only numbers
* Allowed categorical values

Example

```
Quantity

two hundred
```

instead of

```
200
```

❌ Invalid

---

# 6. Consistency / Parity Validation

This is huge for migrations.

Checks:

* Row count parity
* Column parity
* Value parity
* Aggregate parity
* Checksums
* Hash comparison
* Source vs target comparison
* Metadata comparison

Example

Source

```
Price = 10
```

Target

```
Price = 15
```

❌ Fail

---

# 7. Integrity Validation

Checks:

* Primary key integrity
* Foreign key integrity
* Referential integrity
* Parent-child relationships
* Orphan records

Example

Orders

```
CustomerID = 5
```

Customer table

```
CustomerID = 5
```

doesn't exist.

❌ Fail

---

# 8. Business Rule Validation

These depend on the business.

Warehouse example:

* Quantity ≥ 0
* Price > 0
* Status must be:

```
In Stock

Out of Stock

Reserved
```

Category must be

```
Electronics

Furniture

Toys
```

Restocked date

Cannot be in the future.

---

# For Images

Checks

* Missing images
* Corrupt images
* Resolution
* Width
* Height
* Image format
* Duplicate images
* Missing labels
* Metadata consistency

---

# For Videos

Checks

* Missing videos
* Corrupt videos
* FPS
* Frame count
* Duration
* Resolution
* Codec
* Missing annotations

---

# For Text

Checks

* Empty text
* Duplicate text
* Invalid language
* Missing labels
* Token count
* Encoding
* Offensive content labels
* Metadata consistency

---

# For Migration Validation (AWS → GCP)

Checks

* Schema parity
* Row count parity
* Hash comparison
* Object count
* File size parity
* Checksum parity
* Metadata parity
* Partition parity
* Replication lag
* DAG completion
* Data quality alerts
* Pipeline logs
* Retry validation

# The order I would build your project

```text
validation/

│

├── data_profiler.py

├── schema_validator.py

├── completeness_validator.py

├── uniqueness_validator.py

├── validity_validator.py

├── consistency_validator.py

├── integrity_validator.py

├── business_rule_validator.py

├── migration_validator.py

└── report_generator.py
```

## Why this structure?

I like this architecture because it's **principle-based**, not dataset-based. Whether you're validating warehouse data, customer records, images, videos, or text, you're asking the same kinds of questions:

* Is the schema correct?
* Is the data complete?
* Is it unique?
* Is it valid?
* Is it consistent with the source?
* Does it maintain integrity?
* Does it satisfy the business rules?

That makes your framework reusable across different projects—the kind of design decision interviewers often appreciate because it shows you're thinking beyond a single dataset.
