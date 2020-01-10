import os
import pytest
import torch

from ..model import Classifier

TEST_PATH = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(TEST_PATH, "data")


@pytest.fixture
def model():
    model_path = os.path.join(TEST_DATA_PATH, "model.pt")
    model_state_dict = torch.load(model_path)
    model = Classifier()
    model.load_state_dict(model_state_dict)

    return model


@pytest.fixture
def data():
    data_path = os.path.join(TEST_DATA_PATH, "data.pt")
    return torch.load(data_path)
