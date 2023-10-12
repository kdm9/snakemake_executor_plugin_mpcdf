from pathlib import Path
from typing import Optional
import snakemake.common.tests
from snakemake_interface_executor_plugins import ExecutorSettingsBase

from snakemake_executor_plugin_cluster_sync import ExecutorSettings


class TestWorkflows(snakemake.common.tests.TestWorkflowsBase):
    __test__ = True

    def _get_cmd(self, cmd) -> str:
        return str((Path(__file__).parent / cmd).absolute())

    def get_executor(self) -> str:
        return "cluster-sync"

    def get_executor_settings(self) -> Optional[ExecutorSettingsBase]:
        return ExecutorSettings(submit_cmd=self._get_cmd("qsub.sh"))

    def get_default_storage_provider(self) -> Optional[str]:
        return None

    def get_default_storage_prefix(self) -> Optional[str]:
        return None
