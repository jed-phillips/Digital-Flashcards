'''
Created on Jul 11, 2012

@author: Jedidiah Phillips
'''
import argparse
import xml.dom.minidom
import os
import pyne
from pyne.simplesim import cards
from pyne import material as pinemat
from pyne.simplesim import definition
from pyne.simplesim import inputfile

parser = argparse.ArgumentParser(description="Convert OpenMC input files to"
                                 + " MCNP input file. Navigate to the"
                                 + " directory of the OpenMC input files"
                                 + " or type in the directory after the"
                                 + " 'i' tag. The MCNP input files created"
                                 + " will be saved to a folder in the"
                                 + " current directory. You can change the"
                                 + " name of this directory using the 'o'"
                                 + " tag.")
parser.add_argument('-i', action="store", default=os.getcwd(),
                    help="Directory to OpenMC input files.", metavar='Inputs',
                    dest="directory")
parser.add_argument('-o', action="store", default="MCNP_Input_Files",
                    help="Name of folder for Output", metavar="Destination",
                    dest="fileName")
args = parser.parse_args()
                    
print args.directory
print args.fileName

sys = definition.SystemDefinition(verbose=False)


class geometry(object):
    data = None
    surfaces = []
    cells = []
    lattices = []

    def __init__(self):
        try:
            file = open(args.directory + '/geometry.xml')
            self.data = xml.dom.minidom.parseString(file.read())
            file.close()
            self.readCells()
            self.readSurfaces()
            self.readLattices()
        except:
            raise
            print "geometry.xml does not exist in this directory"
            return
    def __str__(self):
        return "geomentry.xml"
    def readSurfaces(self):
        surfaces = self.data.getElementsByTagName('surface')
        for element in surfaces:
            self.surfaces.append(surface(element))
    def readCells(self):
        cells = self.data.getElementsByTagName('cell')
        for element in cells:
            self.cells.append(cell(element))
    def readLattices(self):
        lattices = self.data.getElementsByTagName('lattice')
        for element in lattices:
            self.lattices.append(lattice(element))

    def convertSurfaces(self):
        dic = {}
        for s in self.surfaces:
            dic[float(s.id)] = s.convert()
        return dic
    def convertCells(self, dicm):
        dics = self.convertSurfaces()
        dic = {}
        for c in self.cells:
            sys.add_cell(c.convert(dics, dicm))
        return
            
class surface(object):
    id = None
    type = None
    coeffs = None
    boundary = None
    
    def __init__(self, element):
        self.id = getValue(element, "id")
        self.type = getValue(element, "type")
        self.coeffs = getValue(element, "coeffs")
        self.boundary = getValue(element, "boundary")
    def __str__(self):
        return (self.id + " " + self.type + " "
                 + self.coeffs + " " + self.boundary)
    def getID(self):
        return self.id
    def getType(self):
        return self.type
    def getCoeffs(self):
        return self.coeffs
    def getBoundary(self):
        return self.boundary
    def convert(self):
        shift = [0, 0, 0]
        if self.type == "x-plane":
            card=cards.AxisPlane(self.id, "x", float(self.coeffs))
        elif self.type == "y-plane":
            card=cards.AxisPlane(self.id, "y", float(self.coeffs))
        elif self.type == "z-plane":
            card=cards.AxisPlane(self.id, "z", float(self.coeffs))
        elif self.type == "x-cylinder":
            card=cards.AxisCylinder(self.id, "x", float(self.coeffs.rsplit(" ")[2]))
            shift[0] = float(self.coeffs.rsplit(" ")[0])
            shift[2] = 0.0
            shift[1] = float(self.coeffs.rsplit(" ")[1])
            card.shift(shift)
        elif self.type == "y-cylinder":
            card=cards.AxisCylinder(self.id, "y", float(self.coeffs.rsplit(" ")[2]))
            shift[0] = float(self.coeffs.rsplit(" ")[0])
            shift[1] = 0.0
            shift[2] = float(self.coeffs.rsplit(" ")[1])
            card.shift(shift)
        elif self.type == "z-cylinder":
            card=cards.AxisCylinder(self.id, "z", float(self.coeffs.rsplit(" ")[2]))
            shift[0] = float(self.coeffs.rsplit(" ")[0])
            shift[2] = 0.0
            shift[1] = float(self.coeffs.rsplit(" ")[1])
            card.shift(shift)
        elif self.type == "sphere":
            print "spheres not supported"
        return card

class cell(object):
    id = None
    material = None
    surfaces = None
    universe = None
    
    def __init__(self, element):
        self.id = getValue(element, "id")
        self.universe = getValue(element, "universe")
        self.material = getValue(element, "material")
        self.surfaces = getValue(element, "surfaces")
    def __str__(self):
        return self.id + " " + self.material + " " + self.surfaces
    def getID(self):
        return self.id
    def getMaterial(self):
        return self.material
    def getSurfaces(self):
        return self.surfaces
    def convert(self, dics, dicm):
        identity = None
        region = None
        n = 0
        units = None
        if dicm[float(self.material)][2] == "atom/b-cm":
            units = "atoms/b/cm"
        else:
            units = "g/cm^3"
        surf = self.surfaces.rsplit(" ")
        if (float(surf[0]) < 0):
            region = dics.get(-1*float(surf[0])).neg
        else:
            region = dics.get(float(surf[0])).pos
        for s in surf:
            identity=float(s)
            if (n != 0):
                if identity < 0:
                    region = region | dics.get(-1*identity).neg
                else:
                    region = region | dics.get(identity).pos
            n+=1
        card = cards.CellMCNP(self.id, region, dicm[float(self.material)][0],dicm[float(self.material)][1], units)
        return card
        
class lattice(object):
    id = None
    type = None
    dimension = None
    lower_left = None
    width = None
    universes = []
    def __init__(self,element):
        self.id = getValue(element, "id")
        self.type = getValue(element, "type")
        self.dimension = getValue(element, "dimension")
        self.lower_left = getValue(element, "lower_left")
        self.universes = getValue(element, "universes")
        print self.universes[0:20]
class materials(object):
    data = None
    materials = []
    
    def __init__(self):
            try:
                file = open(args.directory + '/materials.xml')
                self.data = xml.dom.minidom.parseString(file.read())
                file.close()
                self.readMaterials()
            except:
                print "materials.xml does not exist in this directory."
            return
    def __str__(self):
        return "materials.xml"
    def readMaterials(self):
        materials = self.data.getElementsByTagName('material')
        for element in materials:
            self.materials.append(material(element))
    def getMaterials(self):
        return self.materials
    def convertMaterials(self):
        dic = {}
        for m in self.materials:
            print m
            dic[float(m.id)] = m.convert(), m.getDensity(), m.getUnits()
        return dic

class material(object):
    id = None
    density = None
    units = None
    nuclides = []
    
    def __init__(self, element):
        self.id = getValue(element, "id")
        self.density = getValue(element.getElementsByTagName("density")
                        .item(0), "value")
        self.units = getValue(element.getElementsByTagName("density")
                      .item(0),"units")
        self.readNuclides(element)
    def __str__(self):
        return self.id + " " + self.density + " " + self.units
    def readNuclides(self, element):
        for element in element.getElementsByTagName("nuclide"):
            self.nuclides.append(nuclide(element))
    def getID(self):
        return self.id
    def getDensity(self):
        return float(self.density)
    def getUnits(self):
        return self.units
    def getNuclides(self):
        return self.nuclides
    def convert(self):
        dic = {}
        for x in self.nuclides:
            if x.getName()[-3:] == "Nat":
                x.setName(str(pyne.nucname.name_zz[x.getName()[:-4]]*1000))
            dic[x.getName()] = x.getAo()
            print x.getName()
            print dic
        return cards.Material(pinemat.from_atom_frac(dic), name=self.id)
    
class nuclide(object):
    name = None
    ao = None

    def __init__(self, element):
        self.name = getValue(element,"name")
        self.ao = getValue(element,"ao")
    def __str__(self):
        return self.name + " " + self.ao
    def getName(self):
        return self.name
    def setName(self, nametemp):
        self.name = nametemp
    def getAo(self):
        return float(self.ao)

class settings(object):
    data = None
    criticality = None
    source = None
    
    def __init__(self):
        try:
            file = open(args.directory + '/settings.xml')
            self.data = xml.dom.minidom.parseString(file.read())
            file.close()
            self.readCriticality(self.data.getElementsByTagName("settings")[0])
            self.readSource(self.data.getElementsByTagName("settings")[0])
        except:
            print "settings.xml does not exist in this directory."
            return
    def __str__(self):
        return "settings.xml"
    def readCriticality(self, element):
        self.criticality = criticality(element)
    def readSource(self, element):
        self.source = source(element)
    def getCriticality(self):
        return self.criticality
    def getSource(self):
        return self.source

class criticality(object):
    batches = None
    inactive = None
    particles = None
    
    def __init__(self, element):
        self.batches = (element.getElementsByTagName("batches")[0]
                        .childNodes[0].data)
        self.inactive = (element.getElementsByTagName("inactive")[0]
                         .childNodes[0].data)
        self.particles = (element.getElementsByTagName("particles")[0]
                          .childNodes[0].data)
    def __str__(self):
        return self.batches + " " + self.inactive + " " + self.particles
    def getBatches(self):
        return self.batches
    def getInactive(self):
        return self.inactive
    def getParticles(self):
        return self.particles
    
class source(object):
    type = None
    coeffs = None
    
    def __init__(self, element):
        self.type = element.getElementsByTagName("type")[0].childNodes[0].data
        self.coeffs = (element.getElementsByTagName("coeffs")[0]
                       .childNodes[0].data)
    def __str__(self):
        return self.type + " " + self.coeffs
    def getType(self):
        return self.type
    def getCoeffs(self):
        return self.coeffs

class comment(object):
    data = None
    fullcomment = None
    comment = ""
    def __init__(self):
        try:
            file = open(args.directory + '/settings.xml')
            self.data = xml.dom.minidom.parseString(file.read())
            file.close()
            self.fullcomment = self.data.getElementsByTagName("settings")[0].childNodes[1].data
            self.buildComment()
        except:
            print "There was an error getting the description."
            return
    def __str__(self):
        return self.comment
    def buildComment(self):
        begining = self.fullcomment.find("Description:")
        end1 = self.fullcomment.find("Case:")
        end2 = self.fullcomment.find("Written By:")
        
        self.comment = (self.fullcomment[begining + 13: end1].rstrip())
        self.comment += ", " + (self.fullcomment[end1 + 13: end2].rstrip())
    def getComment(self):
        return self.comment
    def convert(self):
        return self.comment

class mcnpfile(object):
    geometry = None
    materials = None
    settings = None
    comment = None
    convertedString = ""
    def __init__(self):
        self.geometry = geometry()
        self.materials = materials()
        self.settings = settings()
        self.comment = comment()
    def __str__(self):
        return "MCNP file object"
    def convert(self):
        self.geometry.convertCells(self.materials.convertMaterials())
        sim = definition.MCNPSimulation(sys, verbose=False)
        inp = inputfile.MCNPInput(sim, title="Infinite lattice.")
        inp.write("testMCNP")

def getValue(element, name):
    if element.hasAttribute(name):
        return element.getAttribute(name)
    elif element.getElementsByTagName(name):
        return element.getElementsByTagName(name)[0].childNodes[0].nodeValue
    else:
        return None

mcnpfile().convert()

s = settings()
print s.getSource()
print s.getCriticality()
"""
g = geometry()
print g.surfaces[0]
print g.surfaces[1]
print g.surfaces[2]
print g.cells[0]
s1 = g.surfaces[0].convert()
s2 = g.surfaces[1].convert()
s3 = g.surfaces[2].convert()
region = s1.pos
region = region  | s2.neg
print region
region = region  | s1.pos
print region
region = region | s3.neg
print region
m1 = materials().materials[0].convert()
coolant = cards.CellMCNP('coolant',region, m1,
        1.0, 'g/cm^3',
        importance=('neutron', 1),
        volume=1)
print coolant
from pyne.simplesim import definition
sys = definition.SystemDefinition(verbose=False)
sys.add_cell(coolant)
sim = definition.MCNPSimulation(sys, verbose=False)
from pyne.simplesim import inputfile
inp = inputfile.MCNPInput(sim, title="Infinite lattice.")
inp.write("testMCNP")"""
