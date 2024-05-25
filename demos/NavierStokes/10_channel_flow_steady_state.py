# -*- coding: utf-8 -*-
"""05_channel_flow_with_gmsh.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14JaWNdbZqJ0ZzJ_Swvtcewey92iohOIl

# The Laplace Problem
"""

# Commented out IPython magic to ensure Python compatibility.
# %reset -f

import os
os.environ['XLA_PYTHON_CLIENT_PREALLOCATE'] = "false"

import numpy as np
import jax
import jax.numpy as jnp
from jax.tree_util import Partial
jax.config.update('jax_platform_name', 'cpu')           ## CPU is faster here !


import matplotlib.pyplot as plt
import seaborn as sns
sns.set(context='notebook', style='ticks',
        font='sans-serif', font_scale=1, color_codes=True, rc={"lines.linewidth": 2})

from updes import *
# from updec.cloud import SquareCloud, GmshCloud
# from updec.operators import *
# from updec.utils import print_line_by_line, polyharmonic, multiquadric

"""## Using Updec"""

# facet_types = {"south":"d", "west":"d", "north":"d", "east":"d"}
# facet_types = {"Dirichlet":"d", "Robin":"d", "Neumann":"d"}
facet_types = {"inlet":"d", "wall":"d", "blowing":"d", "outlet":"n", "suction":"d"}

# cloud = SquareCloud(Nx=7, Ny=5, facet_types=facet_types, support_size=3)
# cloud = GmshCloud("./meshes/triangle.msh", facet_types, support_size=3)
cloud = GmshCloud("./demos/meshes/channel.msh", facet_types, support_size=20)       ## TODO do not hardcode this path

cloud.visualize_cloud(figsize=(6,4));


# exit(0)


RBF = polyharmonic      ## Can define which rbf to use
MAX_DEGREE = 4

# ## Operates on radial basis functions and polynomials at position x: don't forget the None. It is important!
# # @jax.jit
# # @partial(jax.jit, static_argnums=2)
# def my_diff_operator(x, node=None, monomial=None, *args):
#     return  args[0] * nodal_laplacian(x, node, monomial, rbf=RBF) / args[1]

# minus_ones = -jnp.ones((cloud.N,))
# ones = jnp.ones((cloud.N,))
# ## Operates on entire fields at position x (inside node)
# # @jax.jit
# def my_rhs_operator(x):
#     # return divergence(x, known_field, cloud, rbf=RBF, max_degree=2)
#     # return 2.0
#     return 1.0

# d_north = lambda node: jnp.sin(jnp.pi * node[0])
# d_zero = lambda node: 0.0

# # boundary_conditions = {0:d_zero, 1:d_zero, 2:d_zero, 3:d_zero}
# boundary_conditions = {"inlet":d_north, "wall":d_zero, "blowing":d_zero, "outlet":d_zero, "suction":d_zero}

# # solution_field = pde_solver(my_diff_operator, my_rhs_operator, cloud, boundary_conditions, RBF, MAX_DEGREE, minus_ones, ones)
# # cloud.visualize_field(solution_field, cmap="viridis", projection="2d", ax=None, figsize=(6,5));

d_north = lambda node: jnp.sin(jnp.pi * node[0])
d_zero = lambda node: 0.0

boundary_conditions = {"inlet":d_north, "wall":d_zero, "blowing":d_zero, "outlet":d_zero, "suction":d_zero}

u = jnp.ones((cloud.N,))
v = jnp.ones((cloud.N,))
p = jnp.ones((cloud.N,))
RHO = 1
NU = 1

@Partial(jax.jit, static_argnums=[2,3])
def diff_operator_u(x, center=None, rbf=None, monomial=None, fields=None):
    v = fields[0]                                                      ## TODO Make it clear that this is v at this particular center
    u = nodal_value(x, center, rbf, monomial)
    grad_u = nodal_gradient(x, center, rbf, monomial)
    return  u * grad_u[0] + v * grad_u[1]                           ## TODO: Actually, this is wrong. write this nodal fomrula down !


# nodal_rbf = Partial(make_nodal_rbf, rbf=RBF)   ### TODO Do this in code

@Partial(jax.jit, static_argnums=[2])
def rhs_operator_u(x, centers=None, rbf=None, fields=None):
    p, u = fields[:, 0], fields[:, 1]
    grad_p = gradient(x, p, centers, rbf=rbf)
    lap_u = laplacian(x, u, centers, rbf=rbf)
    return  (-grad_p[0] / RHO) + (NU * lap_u)

usol = pde_solver(diff_operator=diff_operator_u, 
                diff_args=[v], 
                rhs_operator = rhs_operator_u, 
                rhs_args=[p,u], 
                cloud = cloud, 
                boundary_conditions = boundary_conditions)

# print(usol.vals)

# def diff_operator_v(x, node=None, monomial=None, *args):
#     val_v = nodal_value(x, node, monomial, rbf=RBF)
#     grad_v = nodal_gradient(x, node, monomial, rbf=RBF)
#     return  val_v * grad_v[1] + args[0]*grad_v[0]

# def rhs_operator_v(x):
#     grad_p = gradient(x, p, cloud, rbf=RBF, max_degree=MAX_DEGREE)
#     lap_v = laplacian(x, v, cloud, rbf=RBF, max_degree=MAX_DEGREE)
#     return  (-grad_p[0] / RHO) + (NU * lap_v)

# v = pde_solver(diff_operator_v, rhs_operator_v, cloud, boundary_conditions, RBF, MAX_DEGREE, u)

# def diff_operator_p(x, node=None, monomial=None, *args):
#     return  nodal_laplacian(x, node, monomial, rbf=RBF)

# def rhs_operator_p(x):
#     grad_u = gradient(x, u, cloud, rbf=RBF, max_degree=MAX_DEGREE)
#     grad_v = gradient(x, v, cloud, rbf=RBF, max_degree=MAX_DEGREE)
#     return  -RHO * (grad_u[0]*grad_u[0] + 2*grad_u[1]*grad_v[0] + grad_v[1]*grad_v[1])

# p = pde_solver(diff_operator_p, rhs_operator_p, cloud, boundary_conditions, RBF, MAX_DEGREE)

cloud.visualize_field(usol.vals, cmap="viridis", projection="2d", ax=None, figsize=(7,4));
plt.show()
