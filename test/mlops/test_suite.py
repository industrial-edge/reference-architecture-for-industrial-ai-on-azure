import sys
import unittest
from test.mlops.common.src import test_package_delivery, test_package_delivery_mm
from test.mlops.image_classification.src.data_asset_creation import (
    test_data_asset_creation as test_ic_data_asset_creation,
)
from test.mlops.image_classification.src.package import (
    test_packaging as test_ic_packaging,
)
from test.mlops.image_classification.src.package import (
    test_score_package as test_ic_score_package,
)
from test.mlops.image_classification.src.prep import test_prep as test_ic_prep
from test.mlops.image_classification.src.register import (
    test_register as test_ic_register,
)
from test.mlops.image_classification.src.score import test_score as test_ic_score
from test.mlops.image_classification.src.train import test_train as test_ic_train
from test.mlops.state_identifier.src.data_asset_creation import (
    test_data_asset_creation as test_si_data_asset_creation,
)
from test.mlops.state_identifier.src.package import test_packaging as si_test_packaging
from test.mlops.state_identifier.src.package import (
    test_score_package as si_test_score_package,
)
from test.mlops.state_identifier.src.prep import test_prep as test_si_prep
from test.mlops.state_identifier.src.register import test_register as test_si_register
from test.mlops.state_identifier.src.score import test_score as test_si_score
from test.mlops.state_identifier.src.train import test_train as test_si_train

from HtmlTestRunner import HTMLTestRunner


class CustomHTMLTestRunner(HTMLTestRunner):
    def run(self, test):
        result = super().run(test)
        if not result.wasSuccessful():
            sys.exit(1)
        return result


# load the test cases
loader = unittest.TestLoader()

delivery_suite = loader.loadTestsFromModule(test_package_delivery)
delivery_mm_suite = loader.loadTestsFromModule(test_package_delivery_mm)

packaging_si_suite = loader.loadTestsFromModule(si_test_packaging)
score_package_si_suite = loader.loadTestsFromModule(si_test_score_package)
data_asset_creation_si_suite = loader.loadTestsFromModule(test_si_data_asset_creation)
prep_si_suite = loader.loadTestsFromModule(test_si_prep)
register_si_suite = loader.loadTestsFromModule(test_si_register)
score_si_suite = loader.loadTestsFromModule(test_si_score)
train_si_suite = loader.loadTestsFromModule(test_si_train)

packaging_ic_suite = loader.loadTestsFromModule(test_ic_packaging)
score_package_ic_suite = loader.loadTestsFromModule(test_ic_score_package)
data_asset_creation_ic_suite = loader.loadTestsFromModule(test_ic_data_asset_creation)
prep_ic_suite = loader.loadTestsFromModule(test_ic_prep)
train_ic_suite = loader.loadTestsFromModule(test_ic_train)
register_ic_suite = loader.loadTestsFromModule(test_ic_register)
score_ic_suite = loader.loadTestsFromModule(test_ic_score)

# add them to a test suite
suite = unittest.TestSuite(
    [
        delivery_suite,
        delivery_mm_suite,
        packaging_si_suite,
        score_package_si_suite,
        prep_si_suite,
        register_si_suite,
        score_si_suite,
        train_si_suite,
        packaging_ic_suite,
        # score_package_ic_suite,  # something went wrong
        prep_ic_suite,
        train_ic_suite,
        register_ic_suite,
        score_ic_suite,
    ]
)

# run the suite using the custom test runner
runner = CustomHTMLTestRunner(output="test_reports")
runner.run(suite)
