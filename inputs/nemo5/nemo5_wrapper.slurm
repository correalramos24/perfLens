#!/bin/bash
#SBATCH -A bsc32
#SBATCH --ntasks-per-node 112
#SBATCH -c 1
#SBATCH --job-name scale_nemo5
#SBATCH --qos gp_bsces
#SBATCH --ntasks 880
#SBATCH -N 8
#SBATCH --output run_scale_orca1.log
# ================================================================================
# AUTOMATED SLURM SCRIPT WRAPPER GENERATION:

source /gpfs/projects/ehpc252/vcorreal/0.ENVS/intel-mpi.sh
export SRUN_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}
printenv &> env.log
srun nemo
# ================================================================================
