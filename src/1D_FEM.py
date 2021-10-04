import numpy
import matplotlib.pyplot as plot

from nodespace_1D import NodeSpace1D
from elementspace_1D import ElementSpace1D
from polynomial import Polynomial
from matrix import Matrix
from gaussian_quadrature import GaussianQuad

class FiniteElementMethod:

    mesh = []                   # ElementSpace

    material_matrix = []        # Matrix(square)
    force_vector = []           # Matrix(vector)
    material_function = []      # Polynomial

    solution_space = []         # Matrix(vector)

    # Define the Gaussian Quaqdrature positions & weights:
    gaussian = []             # GaussianQuad instance

    def __init__(self, element_space, material_property, bc_type1, bc_type2, gauss_order = 2):
        self.mesh = element_space
        self.material_matrix = Matrix(numpy.zeros((element_space.n_nodes + 1, element_space.n_nodes + 1)))

        # Define linear material function
        self.material_function = Polynomial([material_property, 0])

        # Define the solution space to accomodate the initial type1 boundary conditions
        if isinstance(bc_type1, NodeSpace1D):
            self.solution_space = Matrix(bc_type1.nodes)
        elif isinstance(bc_type1, numpy.ndarray):
            self.solution_space = Matrix(bc_type1)
        elif isinstance(bc_type1, Matrix):
            self.solution_space = bc_type1
        else:
            raise TypeError("bc_type1: Unknown Type")

        # Define the force vector to include the initial type2 boundary conditions
        if isinstance(bc_type2, NodeSpace1D):
            self.force_vector = Matrix(bc_type2.nodes)
        elif isinstance(bc_type2, numpy.ndarray):
            self.force_vector = Matrix(bc_type2)
        elif isinstance(bc_type2, Matrix):
            self.force_vector = bc_type2
        else:
            raise TypeError("bc_type2: Unknown Type")

        self.gaussian = GaussianQuad(gauss_order)
    
    #  Setup the matrices for solving the equations
    def setup(self):
        print("setup_mesh:", self.mesh)
        print("element_type:", type(self.mesh.elements))
        # setup the material matrix, K
        for i in range(self.mesh.n_elements):
            for n_i in range(self.mesh.nodes_per_element - 1):
                nodeA = int( self.mesh.elements[i, n_i] )
                nodeB = int( self.mesh.elements[i, n_i + 1] )
                dx = self.mesh.nodes[nodeB] - self.mesh.nodes[nodeA]
                self.material_matrix[i, i] += self.material_function.evaluate(1)/dx
                self.material_matrix[i + 1, i] += -self.material_function.evaluate(1)/dx
                self.material_matrix[i, i + 1] += -self.material_function.evaluate(1)/dx 
                self.material_matrix[i + 1, i + 1] += self.material_function.evaluate(1)/dx
        
        self.material_matrix[0,0] = 1.0
        self.material_matrix[self.mesh.n_nodes, self.mesh.n_nodes] = 1.0

    def linear_interpolationY(self, x_0, y_0, x_2, y_2, X1):
        return y_0 + (X1 - x_0)*(y_2 - y_0)/(x_2 - x_0)

    # The Partial Differential Equations are solved using ...
    def solve(self):
        #self.solution_space = self.material_matrix.get_inverse() * self.force_vector
        print("Material_matrix:", self.material_matrix)
        print("Inverse_material_matrix:", self.material_matrix.get_inverse())
        print("Force_vector:", self.force_vector)
        print("Solution_space:", self.solution_space)

    # Plot the solution_space values on the respective node coordinates
    def plot(self):
        plot.plot(self.mesh.nodes, self.solution_space)
        plot.xlabel("X Coordinates")
        plot.ylabel("Degree-Of-Freedom Value")
        plot.show()

# Test methods and classes
def main():
    # Heat transfer test method
    # Create mesh using parameters:
    x_dimension = 12        # Distance in meters
    n_elements = 8          # Number of finite elements in domain
    start_pos = 0           # First Node position
    nodes_per_element = 2   # Number of Nodes per element  

    # Create mesh of discrete elements that consist of nodes_per_element
    fem_espace = ElementSpace1D(n_elements, x_dimension, start_pos, nodes_per_element)
    
    # Analysis Conditions:
    #   - Material Properties:
    K = 20      # Stiffness Coefficient (Material Property)

    #   - Type 1 (Dirichlet) boundary conditions:
    Type1_BC = 24       # Temperature specification
    Type1_Nodes = [0]   # Node indices subject to Type 1 BC
    BC_Type1 = NodeSpace1D( numpy.zeros(fem_espace.n_nodes) )
    BC_Type1.assign_values(Type1_BC, Type1_Nodes)

    #   - Type 2 (Neumann) boundary condition:
    Type2_BC = 16                   # Heat Flux Specification
    Type2_Nodes = [n_elements]      # Node indices subject to Type 2 BC
    BC_Type2 = NodeSpace1D( numpy.zeros(fem_espace.n_nodes) )
    BC_Type2.assign_values(Type2_BC, Type2_Nodes)

    # Numerical Conditions:
    Gaussian_order = 3

    FEM = FiniteElementMethod(fem_espace, K, BC_Type1, BC_Type2, Gaussian_order)
    print("FEM_setup..........................................................")
    FEM.setup()
    print("FEM_solve..........................................................")
    FEM.solve()
    print("FEM_plot...........................................................")
    #FEM.plot()

if __name__ == "__main__":
    main()