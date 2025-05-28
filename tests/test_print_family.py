import pytest
from runnable_family.print_family import (
    RunnableLog,
)


@pytest.mark.parametrize(
    'input_obj',
    [
        0,
        'a',
        {'a': 1},
    ]
)
def test_runnable_log(
    input_obj,
    mocker,
):
    func = mocker.MagicMock(return_value=None)
    log_runnable = RunnableLog(func)
    log_runnable.invoke(input_obj)
    func.assert_called_once_with(input_obj)
