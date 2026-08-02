#!/bin/bash
#PBS -N cmip6_gmst_blended
#PBS -P e14
#PBS -q normalbw
#PBS -l walltime=06:00:00
#PBS -l ncpus=28
#PBS -l mem=126GB
#PBS -l storage=gdata/e14+gdata/oi10+gdata/xp65
#PBS -j oe

set -euo pipefail

echo "[$(date)] Job starting on $(hostname)"
echo "[$(date)] PBS job ID: $PBS_JOBID"
echo "[$(date)] Working directory: $PBS_O_WORKDIR"

module use /g/data/xp65/public/modules
module load conda/analysis3-26.02

export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_MAX_THREADS=1
export HDF5_USE_FILE_LOCKING=FALSE

cd "$PBS_O_WORKDIR"

PYFILE="gmst_blended_historical.py"

echo "[$(date)] Running: python -u ${PYFILE}"
python -u "${PYFILE}"

echo "[$(date)] Job finished."
