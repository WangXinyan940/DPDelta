import openmm as mm
import openmm.app as app
import openmm.unit as unit
import numpy as np
import argparse
import sys


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--temperature", type=float, default=300.0)
    args = parser.parse_args()
    return args


def runMD(args):
    pdb = app.PDBFile("40w.pdb")
    ff = app.ForceField("amoeba2018.xml")
    system = ff.createSystem(pdb.topology)
    if args.model is not None:
        from OpenMMDeepmdPlugin import DeepmdForce
        dp_force = DeepmdForce(args.model, "", "", False)
        dp_force.addType(0, app.element.oxygen.symbol)
        dp_force.addType(1, app.element.hydrogen.symbol)
        for atom in pdb.topology.atoms():
            dp_force.addParticle(atom.index, atom.element.symbol)
        for bond in pdb.topology.bonds():
            dp_force.addBond(bond.atom1.index, bond.atom2.index)
        dp_force.setUnitTransformCoefficients(10.0, 964.8792534459,
                                              96.48792534459)  # 1 model
        dp_force.setPBC(False)
    # add flat-bottom restraint
    ogroup = [
        atom.index for atom in pdb.topology.atoms()
        if atom.element == app.element.oxygen
    ]
    res = mm.CustomCentroidBondForce(
        2, "100.0*step(dg)*dg^2;dg=distance(g1,g2)-radius")
    res.addGlobalParameter("radius", 0.7)
    res.addGroup(ogroup)
    for ii in ogroup:
        res.addGroup([ii])
    for ni in range(len(ogroup)):
        res.addBond([0, ni+1])
    system.addForce(res)
    integrator = mm.LangevinIntegrator(args.temperature * unit.kelvin,
                                       5.0 / unit.picosecond,
                                       1.0 * unit.femtosecond)
    simulation = app.Simulation(pdb.topology,
                                system,
                                integrator,
                                platform=mm.Platform.getPlatformByName("CUDA"))
    simulation.context.setPositions(pdb.getPositions())
    simulation.minimizeEnergy()
    simulation.step(1000)  # eq
    simulation.reporters.append(
        app.StateDataReporter("sample.out",
                              100,
                              step=True,
                              time=True,
                              potentialEnergy=True,
                              totalEnergy=True,
                              temperature=True,
                              speed=True))
    simulation.reporters.append(app.DCDReporter("sample.dcd", 100))
    simulation.step(int(1000 * 100))

def main():
    args = parser()