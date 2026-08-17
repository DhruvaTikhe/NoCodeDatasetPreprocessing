from . import (
    redundant,
    duplicates,
    whitespace,
    casing,
    datatypes,
    missing_values,
    outliers,
    # encoding,
    # scaling,
)

MODULES = [
    redundant,
    duplicates,
    whitespace,
    casing,
    datatypes,
    missing_values,
    outliers,
    # encoding,
    # scaling,
]

"""
dependencies list
load data
remove empty rows and colums
remove redundant/useless columns
remove duplicates
trim whitespaces
handle cases
handle inconsistent data which means the same value
convert placeholders to missing values
handle datatypes (number as a string)
convert datatypes (number as a number)
parse date and time features
validate ranges (age<0, salary<0)
handle missing values
outliers
manage distribution (skew,normal,square root)
encoding
scaling/normalizing

<diff sections>
train test split
class imbalance on training only (if applicable)
apply trial models
"""