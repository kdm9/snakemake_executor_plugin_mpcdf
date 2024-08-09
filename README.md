# snakemake-executor-plugin-mpcdf

A Snakemake executor plugin for the raven/viper/cobra systems at MPCDF, Garching, DE (the HPC for all Max Planck Institutes).

These clusters only permit running a very small number of Slurm jobs concurrently. This means that with the default limit of 8 jobs, you're limited to at most 8*72 cores. This is profile allows one to submit one massive job, requesting e.g. 24 nodes, and then use job steps to run jobs in parallel within the massive job. This effectively treats the single big job as your own private mini-cluster, within which your jobs can operate almost as per normal. There is one caveat: jobs are limited to at most about 3000 job steps, so use snakemake groups and `--group-components` liberally to batch up smaller jobs.

Nothing about this should be unique to MPCDF systems, so if your slurm cluster has similar restrictions, then this might work well for you too. It's also a bit of a hack, so if it breaks, you get to keep both pieces.

NB: this is not an official MPCDF product, nor is its use sanctioned by them. Their documentation and some direct communication at least indicates that this is allowed, but there could well be a better way to handle this problem.
