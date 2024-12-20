import os
import great_expectations as gx
from great_expectations.checkpoint import (
    UpdateDataDocsAction,
)

BASE_PATH = "/workspaces/MLOPS_Project3/"
CLEANED_DATA_PATH = os.path.join(BASE_PATH, "data", "clean")

context = gx.get_context(
    mode="file", project_root_dir=os.path.join(BASE_PATH, "./")
)

data_source_name = "my_filesystem_data_source"
# Create the Data Source:
data_source = context.data_sources.add_pandas_filesystem(
    name=data_source_name, base_directory=CLEANED_DATA_PATH
)

asset_name = "online_retail.csv"
# Add the Data Asset to the Data Source:
file_csv_asset = data_source.add_csv_asset(name=asset_name)

file_name = "2010-12-01.csv"
batch_definition_name = "my_batch_definition"
batch_definition = file_csv_asset.add_batch_definition_path(
    name=batch_definition_name, path=file_name
)

batch = batch_definition.get_batch()

# Create an Expectation Suite
suite_name = "my_expectation_suite"
suite = gx.ExpectationSuite(name=suite_name)
suite = context.suites.add(suite)

# StockCode should be a 5-digit number followed by a letter
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToMatchRegex(
        column="StockCode",
        regex=r"^\d{5}[A-Za-z]$"
    )
)

# Description should not be null
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="Description"
    )
)

# Date should be a datetime64
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeOfType(
        column="Date",
        type_="datetime64"
    )
)

# UnitPrice should be a positive integer
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="UnitPrice",
        min_value=0,
        strict_min=True
    )
)

# CustomerID should not be null
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="CustomerID"
    )
)

# CustomerID should be an integer
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeOfType(
        column="CustomerID",
        type_="int",
    )
)

# CustomerID should be positive
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="CustomerID",
        min_value=0,
        strict_min=True
    )
)

# InvoiceNo should be a 6-digit number preceded by an optional "C"
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToMatchRegex(
        column="InvoiceNo",
        regex=r"^C?\d{6}$"
    )
)

# Quantity should be a positive integer, unless InvoiceNo starts with "C"
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="Quantity",
        min_value=0,
        condition_parser="pandas",
        row_condition='~InvoiceNo.str.startswith("C")'
    )
)

# Quantity should be a negative integer, unless InvoiceNo does not start with "C"
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="Quantity",
        max_value=-1,
        condition_parser="pandas",
        row_condition='InvoiceNo.str.startswith("C")'
    )
)

# Create a Validation Definition
definition_name = "my_validation_definition"
validation_definition = gx.ValidationDefinition(
    data=batch_definition, suite=suite, name=definition_name
)

# Add the Validation Definition to the Data Context
validation_definition = context.validation_definitions.add(
    validation_definition
)

# this is the default path (relative to the root folder of the Data Context) but can be changed as required
base_directory = "uncommitted/data_docs/local_site/"
site_config = {
    "class_name": "SiteBuilder",
    "site_index_builder": {"class_name": "DefaultSiteIndexBuilder"},
    "store_backend": {
        "class_name": "TupleFilesystemStoreBackend",
        "base_directory": base_directory,
    },
}

site_name = "my_data_docs_site"
context.add_data_docs_site(site_name=site_name, site_config=site_config)

# Create a list of Actions for the Checkpoint to perform
action_list = [
    # This Action updates the Data Docs static website with the Validation
    #   Results after the Checkpoint is run.
    UpdateDataDocsAction(
        name="update_all_data_docs", site_names=[site_name]
    ),
]

checkpoint_name = "my_checkpoint"
checkpoint = gx.Checkpoint(
    name=checkpoint_name,
    validation_definitions=[validation_definition],
    actions=action_list,
    result_format={"result_format": "COMPLETE"},
)
context.checkpoints.add(checkpoint)

validation_results = checkpoint.run()
# print(validation_results)
