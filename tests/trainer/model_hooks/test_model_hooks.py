import os
from tests.base.boring_model import BoringModel
from pytorch_lightning import Trainer
from unittest import mock


os.environ['PL_DEV_DEBUG'] = '1'

@mock.patch('pytorch_lightning.core.hooks.ModelHooks.on_validation_model_eval')
@mock.patch('pytorch_lightning.core.hooks.ModelHooks.on_validation_model_train')
@mock.patch('pytorch_lightning.core.hooks.ModelHooks.on_test_model_eval')
@mock.patch('pytorch_lightning.core.hooks.ModelHooks.on_test_model_train')
def test_eval_train_calls(test_train_mock, test_eval_mock, val_train_mock, val_eval_mock, tmpdir):
    """
    Tests that only training_step can be used
    """
    model = BoringModel()
    model.validation_epoch_end = None

    trainer = Trainer(
        default_root_dir=tmpdir,
        limit_train_batches=2,
        limit_val_batches=2,
        max_epochs=2,
        row_log_interval=1,
        weights_summary=None,
    )

    trainer.fit(model)
    trainer.test()

    # sanity + 2 epochs
    assert val_eval_mock.call_count == 3
    assert val_train_mock.call_count == 3

    # test is called only once
    assert test_eval_mock.call_count == 1
    assert test_train_mock.call_count == 1
