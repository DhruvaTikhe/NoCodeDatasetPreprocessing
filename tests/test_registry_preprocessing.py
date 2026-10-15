from preprocessing.registry_preprocessing import MODULES

def test_registry_contains_expected_modules():
    names = {module.__name__.split(".")[-1] for module in MODULES}
    assert names == {"redundant", "duplicates", "whitespace", "casing", "datatypes", "missing_values", "outliers", "encoding", "scaling", "normalization"}

def test_each_registered_module_has_expected_metadata_and_process():
    for module in MODULES:
        for attribute in ("TITLE", "COLUMN_TYPE", "METHODS", "SHOW_CONSTANT", "ALLOW_MULTISELECT", "process"):
            assert hasattr(module, attribute), f"{module.__name__} missing {attribute}"
