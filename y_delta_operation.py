# -*- coding: utf-8 -*-
"""Y-delta operation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-U8rEgzqTWzVFY-F6rV2zoQTjwlX6wZ9
"""

import numpy as np

# chop a specified degree 3 vertex (Perform a Y -> Delta operation)
# inputs:
# adj_matrix (numpy array)    Adjacency matrix of a graph
# vertex (int)  index of vertex that we want to chop
# outputs:
# new_adj_matrix (numpy array)    Adjacency matrix of graph with vertex chopped

# NOTE: for now we can only choose degree 3 vertices due to difficulty in structuring the vertex figure

def chop_off_vertex(adj_matrix, vertex):
  n = adj_matrix.shape[0]
  num_neighbors = np.sum(adj_matrix[vertex])
  # Create a new adjacency matrix for the modified graph
  new_size = n + num_neighbors - 1
  new_adj_matrix = np.zeros((new_size, new_size), dtype=int)

  # Copy the old edges except for the specified vertex
  for i in range(n):
    if i < vertex: # rows before i
      cols_before_i = adj_matrix[i, :vertex].tolist()
      cols_after_i = adj_matrix[i, vertex+1:].tolist()
      new_row = cols_before_i + cols_after_i + np.zeros(new_size - len(cols_before_i) - len(cols_after_i), dtype=int).tolist()
      new_adj_matrix[i] = new_row
    elif i > vertex: # rows after i
      cols_before_i = adj_matrix[i, :vertex].tolist()
      cols_after_i = adj_matrix[i, vertex+1:].tolist()
      new_adj_matrix[i-1] = cols_before_i + cols_after_i + np.zeros((new_size - len(cols_before_i) - len(cols_after_i)), dtype=int).tolist()

  # Add new vertices and edges around the specified vertex
  neighbors = np.where(adj_matrix[vertex] == 1)[0].tolist()

  # first_neighbor_index = n - 1
  # second_neighbor_index = n
  # third_neighbor_index = n + 1

  # Connect old neighbors to new vertices
  i = -1
  for x in neighbors:
    if x < vertex:
      new_adj_matrix[x][n + i] = 1
      new_adj_matrix[n + i][x] = 1
    if x > vertex:
      new_adj_matrix[x-1][n + i] = 1
      new_adj_matrix[n + i][x-1] = 1
    i += 1

  # Connect new vertices to one another
  # And also check to ensure we aren't having double edges!

  new_adj_matrix[n - 1][n] = 1
  new_adj_matrix[n][n - 1] = 1

  new_adj_matrix[n - 1][n + 1] = 1
  new_adj_matrix[n + 1][n - 1] = 1

  new_adj_matrix[n + 1][n] = 1
  new_adj_matrix[n][n + 1] = 1

  # cycle_start = n - 1
  # for i in range(num_neighbors):
    # new_adj_matrix[cycle_start + i, cycle_start + ((i + 1) % num_neighbors)] = 1  # Cycle edges
  #   new_adj_matrix[cycle_start + i, neighbors[i]] = 1  # Connect to original neighbors

  return new_adj_matrix

# Example usage
cube = np.array([[0,1,0,1,1,0,0,0],[1,0,1,0,0,1,0,0],[0,1,0,1,0,0,0,1],[1,0,1,0,0,0,1,0],[1,0,0,0,0,1,1,0],[0,1,0,0,1,0,0,1],[0,0,0,1,1,0,0,1],[0,0,1,0,0,1,1,0]])
new_matrix = chop_off_vertex(cube, 3)
print(new_matrix.tolist())

import networkx as nx
import numpy as np

# returns p-vector of polytope associated to planar, 3-connected graph
# inputs:
# graph (numpy array)   Adjacency Matrix of the graph
# outputs:
# p_vector (list)   p vector (p_3, p_4, p_5,...) of a polytope whose graph is the given graph

# NOTE: If the graph is simple (3-regular), then its associated combinatorial polytope is unique

def p_k_vector(graph):
    num_i_sides = {} # keys are 3 (triangle), 4 (quadrilateral), 5 (pentagon), etc., values are how many of each kind of face.
    G_nx = nx.Graph(graph)

    # Check if the graph is planar and get the planar embedding
    is_planar, embedding_nx = nx.check_planarity(G_nx)

    # Construct poset of 1-skeleton
    # add vertices
    vert_elms = [] # a list 1,...,n

    for i in range(1, len(graph[0]) + 1):
        vert_elms = vert_elms + [i]

    # add edges
    edge_elms = []
    edge_dict = {} # keys are edge indices, values are the indicestwo vertices it contains

    # and relations
    relations = []

    for vert in vert_elms:
        vert_mat_index = vert - 1

        neighbors = [] # poset indices of neighbors
        for j in range(len(graph[0])):
            if graph[vert_mat_index][j] == 1:
                neighbors = neighbors + [j + 1]

        for buddy in neighbors:
            if vert < buddy:
                if len(edge_elms) == 0:
                    edge_elms = edge_elms + [vert_elms[-1] + 1]
                    edge_dict[edge_elms[-1]] = [vert, buddy]
                    relations = relations + [[vert, edge_elms[-1]]] + [[buddy, edge_elms[-1]]]
                else:
                    edge_elms = edge_elms + [edge_elms[-1] + 1]
                    edge_dict[edge_elms[-1]] = [vert, buddy]
                    relations = relations + [[vert, edge_elms[-1]]] + [[buddy, edge_elms[-1]]]

    # add faces
    face_elms = []
    face_dict = {} # key is the index of a face (in the poset lattice), feature is the first nx vertex list we find

    for edge in edge_dict:
        # Take in an edge, traverse its face to see which vertices are contained.
        two_vert_indices = edge_dict[edge]
        two_verts = []
        for i in two_vert_indices:
            two_verts = two_verts + [i-1]

        # first half-edge
        f1_vert_list = list(embedding_nx.traverse_face(v=two_verts[0], w=two_verts[1]))

        # test if this face has been accounted for yet
        test_face1 = []
        for face in face_dict:
            already_found_face = face_dict[face]
            if sorted(f1_vert_list) == sorted(already_found_face):
                test_face1 = test_face1 + [1]
                # if this face has already been acknowledged, take its index and add a relation
                relations = relations + [ [edge, face] ]

        # if this face has not been accounted for yet, add it to the dict / poset element list
        if len(test_face1) == 0:
            if len(face_elms) == 0:
                face_elms = face_elms + [edge_elms[-1] + 1]
                face_dict[face_elms[-1]] = f1_vert_list
                relations = relations + [ [edge, face_elms[-1]] ]
            else:
                face_elms = face_elms + [face_elms[-1] + 1]
                face_dict[face_elms[-1]] = f1_vert_list
                relations = relations + [ [edge, face_elms[-1]] ]

        # second half-edge
        f2_vert_list = list(embedding_nx.traverse_face(v=two_verts[1], w=two_verts[0]))

        # test if this face has been accounted for yet
        test_face2 = []
        for face in face_dict:
            already_found_face = face_dict[face]
            if sorted(f2_vert_list) == sorted(already_found_face):
                test_face2 = test_face2 + [1]
                # if this face has already been acknowledged, take its index and add a relation
                relations = relations + [ [edge, face] ]

        # if this face has not been accounted for yet, add it to the dict / poset element list
        if len(test_face2) == 0:
            if len(face_elms) == 0:
                face_elms = face_elms + [edge_elms[-1] + 1]
                face_dict[face_elms[-1]] = f2_vert_list
                relations = relations + [ [edge, face_elms[-1]] ]
            else:
                face_elms = face_elms + [face_elms[-1] + 1]
                face_dict[face_elms[-1]] = f2_vert_list
                relations = relations + [ [edge, face_elms[-1]] ]

    for face in face_dict:
        if len(face_dict[face]) in num_i_sides:
            num_i_sides[len(face_dict[face])] += 1
        else:
            num_i_sides[len(face_dict[face])] = 1

    # get a vector of keys so we can sort it
    key_list = []
    for key in  num_i_sides:
        key_list += [key]
    key_list = sorted(key_list)
    max_k = key_list[-1]

    p_vector = []
    for i in range(3, max_k +1):
        if i in num_i_sides:
            p_vector += [num_i_sides[i]]
        else:
            p_vector += [0]

    return(p_vector)

# Example usage
cube = np.array([[0,1,0,1,1,0,0,0],[1,0,1,0,0,1,0,0],[0,1,0,1,0,0,0,1],[1,0,1,0,0,0,1,0],[1,0,0,0,0,1,1,0],[0,1,0,0,1,0,0,1],[0,0,0,1,1,0,0,1],[0,0,1,0,0,1,1,0]])
new_matrix = chop_off_vertex(cube, 3)
print(p_k_vector(new_matrix))