from analysis.registry_analysis import ANALYSIS_MODULES

def test_registry_contains_three_analysis_modules():
    names = {module.__name__.split(".")[-1] for module in ANALYSIS_MODULES}
    assert names == {"correlation", "describe", "value_counts"}

def test_each_analysis_module_exposes_analyze():
    for module in ANALYSIS_MODULES:
        assert callable(getattr(module, "analyze", None))
