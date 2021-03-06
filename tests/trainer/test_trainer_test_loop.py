import pytest
import torch
import os

import pytorch_lightning as pl
import tests.base.develop_utils as tutils
from tests.base import EvalModelTemplate


os.environ['PL_DEV_DEBUG'] = '1'

@pytest.mark.skipif(torch.cuda.device_count() < 2, reason="test requires multi-GPU machine")
def test_single_gpu_test(tmpdir):
    tutils.set_random_master_port()

    model = EvalModelTemplate()
    trainer = pl.Trainer(
        default_root_dir=tmpdir,
        max_epochs=2,
        limit_train_batches=10,
        limit_val_batches=10,
        gpus=[0],
    )
    trainer.fit(model)
    assert 'ckpt' in trainer.checkpoint_callback.best_model_path
    results = trainer.test()
    assert 'test_acc' in results[0]

    old_weights = model.c_d1.weight.clone().detach().cpu()

    results = trainer.test(model)
    assert 'test_acc' in results[0]

    # make sure weights didn't change
    new_weights = model.c_d1.weight.clone().detach().cpu()

    assert torch.all(torch.eq(old_weights, new_weights))


@pytest.mark.skipif(torch.cuda.device_count() < 2, reason="test requires multi-GPU machine")
def test_dp_test(tmpdir):
    tutils.set_random_master_port()

    import os
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'

    model = EvalModelTemplate()
    trainer = pl.Trainer(
        default_root_dir=tmpdir,
        max_epochs=2,
        limit_train_batches=10,
        limit_val_batches=10,
        gpus=[0, 1],
        distributed_backend='dp',
    )
    trainer.fit(model)
    assert 'ckpt' in trainer.checkpoint_callback.best_model_path
    results = trainer.test()
    assert 'test_acc' in results[0]

    old_weights = model.c_d1.weight.clone().detach().cpu()

    results = trainer.test(model)
    assert 'test_acc' in results[0]

    # make sure weights didn't change
    new_weights = model.c_d1.weight.clone().detach().cpu()

    assert torch.all(torch.eq(old_weights, new_weights))


@pytest.mark.skipif(torch.cuda.device_count() < 2, reason="test requires multi-GPU machine")
def test_ddp_spawn_test(tmpdir):
    tutils.set_random_master_port()

    model = EvalModelTemplate()
    trainer = pl.Trainer(
        default_root_dir=tmpdir,
        max_epochs=2,
        limit_train_batches=10,
        limit_val_batches=10,
        gpus=[0, 1],
        distributed_backend='ddp_spawn',
    )
    trainer.fit(model)
    assert 'ckpt' in trainer.checkpoint_callback.best_model_path
    results = trainer.test()
    assert 'test_acc' in results[0]

    old_weights = model.c_d1.weight.clone().detach().cpu()

    results = trainer.test(model)
    assert 'test_acc' in results[0]

    # make sure weights didn't change
    new_weights = model.c_d1.weight.clone().detach().cpu()

    assert torch.all(torch.eq(old_weights, new_weights))
