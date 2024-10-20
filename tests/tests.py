from pathlib import Path
from typing import Optional
import snakemake.common.tests
from snakemake_interface_executor_plugins.settings import ExecutorSettingsBase

from snakemake_executor_plugin_mpcdf import ExecutorSettings


class TestWorkflows(snakemake.common.tests.TestWorkflowsLocalStorageBase):
    __test__ = True

    def _get_cmd(self, cmd) -> str:
        return str((Path(__file__).parent / cmd).absolute())

    def get_executor(self) -> str:
        return "mpcdf"

    def get_executor_settings(self) -> Optional[ExecutorSettingsBase]:
        return ExecutorSettings()
