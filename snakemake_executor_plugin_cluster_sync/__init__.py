from dataclasses import dataclass, field
import os
import shlex
import subprocess
from typing import List, Generator, Optional

from snakemake_interface_common.exceptions import WorkflowError
from snakemake_interface_executor_plugins.executors.base import SubmittedJobInfo
from snakemake_interface_executor_plugins.executors.remote import RemoteExecutor
from snakemake_interface_executor_plugins.settings import (
    ExecutorSettingsBase,
    CommonSettings,
)
from snakemake_interface_executor_plugins.jobs import (
    JobExecutorInterface,
)


# Optional:
# define additional settings for your executor
# They will occur in the Snakemake CLI as --<executor-name>-<param-name>
# Omit this class if you don't need any.
@dataclass
class ExecutorSettings(ExecutorSettingsBase):
    submit_cmd: Optional[str] = field(
        default=None,
        metadata={
            "help": "Submission command for synchronous cluster "
            "submission (expecting jobscript as single argument)."
        },
    )


# Required:
# Specify common settings shared by various executors.
common_settings = CommonSettings(
    # define whether your executor plugin executes locally
    # or remotely. In virtually all cases, it will be remote execution
    # (cluster, cloud, etc.). Only Snakemake's standard execution
    # plugins (snakemake-executor-plugin-dryrun, snakemake-executor-plugin-local)
    # are expected to specify False here.
    non_local_exec=True,
    # Define whether your executor plugin implies that there is no shared
    # filesystem (True) or not (False).
    # This is e.g. the case for cloud execution.
    implies_no_shared_fs=False,
    job_deploy_sources=False,
    pass_default_storage_provider_args=True,
    pass_default_resources_args=True,
    pass_envvar_declarations_to_cmd=True,
    auto_deploy_default_storage_provider=False,
)


# Required:
# Implementation of your executor
class Executor(RemoteExecutor):
    def run_job(self, job: JobExecutorInterface):
        # Implement here how to run a job.
        # You can access the job's resources, etc.
        # via the job object.
        # After submitting the job, you have to call
        # self.report_job_submission(job_info).
        # with job_info being of type
        # snakemake_interface_executor_plugins.executors.base.SubmittedJobInfo.

        jobscript = self.get_jobscript(job)
        self.write_jobscript(job, jobscript)

        try:
            submitcmd = job.format_wildcards(self.workflow.executor_settings.submit_cmd)
        except AttributeError as e:
            raise WorkflowError(str(e), rule=job.rules if not job.is_group() else None)

        process = subprocess.Popen(
            f'{submitcmd} "{jobscript}"',
            shell=True,
        )

        self.report_job_submission(
            SubmittedJobInfo(job, aux={"process": process, "jobscript": jobscript})
        )

    async def check_active_jobs(
        self, active_jobs: List[SubmittedJobInfo]
    ) -> Generator[SubmittedJobInfo, None, None]:
        # Check the status of active jobs.

        # You have to iterate over the given list active_jobs.
        # For jobs that have finished successfully, you have to call
        # self.report_job_success(job).
        # For jobs that have errored, you have to call
        # self.report_job_error(job).
        # Jobs that are still running have to be yielded.
        #
        # For queries to the remote middleware, please use
        # self.status_rate_limiter like this:
        #
        # async with self.status_rate_limiter:
        #    # query remote middleware here
        for active_job in active_jobs:
            async with self.status_rate_limiter:
                exitcode = active_job.aux["process"].poll()

            jobscript = active_job.aux["jobscript"]

            if exitcode is None:
                # job not yet finished
                yield active_job
            elif exitcode == 0:
                # job finished successfully
                os.remove(jobscript)
                self.report_job_success(active_job)
            else:
                # job failed
                os.remove(jobscript)
                self.report_job_error(active_job)

    def cancel_jobs(self, active_jobs: List[SubmittedJobInfo]):
        # Cancel all active jobs.
        # This method is called when Snakemake is interrupted.
        self.logger.info("Will exit after finishing currently running jobs.")

    def get_job_exec_prefix(self, job):
        if self.workflow.storage_settings.assume_shared_fs:
            return f"cd {shlex.quote(self.workflow.workdir_init)}"
        else:
            return ""
