# use the fit elastic tensor code and hardcoded queries to get the derived elastic tensor properties

from atomate2.common.jobs.elastic import fit_elastic_tensor

# query the job store for all workflows that are DFT-elastic and have all elastic relax jobs with status completed

# get the required elastic relax propeties

# properties i need: structure: Structure, deformation_data: list[dict], equilibrium_stress: Matrix3D | None = None, order: int = 2, fitting_method: str = SETTINGS.ELASTIC_FITTING_METHOD,symprec: float = SETTINGS.SYMPREC, allow_elastically_unstable_structs: bool = True,

# deformation data needs  stresses.append(Stress(data["stress"])), deformations.append(Deformation(data["deformation"])), uuids.append(data["uuid"]), job_dirs.append(data["job_dir"])
