"""
Poisson Image Editing
William Emmanuel
wemmanuel3@gatech.edu
CS 6745 Final Project Fall 2017
"""

import numpy as np
from scipy.sparse import linalg as linalg
from scipy.sparse import lil_matrix as lil_matrix
# Helper enum
OMEGA = 0
DEL_OMEGA = 1
OUTSIDE = 2

# Determine if a given index is inside omega, on the boundary (del omega),
# or outside the omega region


def point_location(index, mask, source):
    if in_omega(index, mask) == False:
        return OUTSIDE
    if edge(index, mask, source) == True:
        return DEL_OMEGA
    return OMEGA

# Determine if a given index is either outside or inside omega


def in_omega(index, mask):
    return mask[index] == 1

# Deterimine if a given index is on del omega (boundary)


def edge(index, mask, source):
    if in_omega(index, mask) == False:
        return False
    for pt in get_surrounding(index, source):
        # If the point is inside omega, and a surrounding point is not,
        # then we must be on an edge
        if in_omega(pt, mask) == False:
            return True
    return False

# Apply the Laplacian operator at a given index


def lapl_at_index(source, index):
    i = index[0]
    j = index[1]
    sub = 0
    cut = 0

    if i + 1 < source.shape[0]:
        sub = sub + source[i + 1, j]
        cut = cut + 1
    if i - 1 >= 0:
        sub = sub + source[i - 1, j]
        cut = cut + 1
    if j + 1 < source.shape[1]:
        sub = sub + source[i, j + 1]
        cut = cut + 1
    if j - 1 >= 0:
        sub = sub + source[i, j - 1]
        cut = cut + 1

    val = (cut * source[i, j]) - sub
    return val

# Find the indicies of omega, or where the mask is 1


def mask_indicies(mask):
    nonzero = np.nonzero(mask)
    locs = []
    for i in range(nonzero[0].shape[0]):
        locs.append((nonzero[0][i], nonzero[1][i]))
    return locs

# Get indicies above, below, to the left and right


def get_surrounding(index, source):
    i = index[0]
    j = index[1]
    out = []
    if i + 1 < source.shape[0]:
        out.append((i + 1, j))
    if i - 1 >= 0:
        out.append((i - 1, j))
    if j + 1 < source.shape[1]:
        out.append((i, j + 1))
    if j - 1 >= 0:
        out.append((i, j - 1))

    return out

# Create the A sparse matrix


def poisson_sparse_matrix(points, source):
    # N = number of points in mask
    N = len(points)
    A = lil_matrix((N, N))
    # Set up row for each point in mask

    for i, index in enumerate(points):
        # Should have 4's diagonal
        A[i, i] = 4
        # Get all surrounding points
        for x in get_surrounding(index, source):
            # If a surrounding point is in the mask, add -1 to index's
            # row at correct position
            if x not in points:
                continue
            j = points.index(x)
            A[i, j] = -1
    return A

# Main method
# Does Poisson image editing on one channel given a source, target, and mask


def process(source, target, mask):

    indicies = mask_indicies(mask)
    N = len(indicies)
    # Create poisson A matrix. Contains mostly 0's, some 4's and -1's
    A = poisson_sparse_matrix(indicies, source)
    # Create B matrix
    b = np.zeros(N)
    for i, index in enumerate(indicies):
        # Start with left hand side of discrete equation
        b[i] = lapl_at_index(source, index)
        # If on boundry, add in target intensity
        # Creates constraint lapl source = target at boundary
        if point_location(index, mask, source) == DEL_OMEGA:
            for pt in get_surrounding(index, source):
                if in_omega(pt, mask) == False:
                    b[i] += target[pt]

    # Solve for x, unknown intensities
    x = linalg.cg(A, b)
    # Copy target photo, make sure as int
    composite = np.copy(target).astype(int)
    # Place new intensity on target at given index
    for i, index in enumerate(indicies):
        composite[index] = x[0][i]

    return composite

# Naive blend, puts the source region directly on the target.
# Useful for testing


def preview(source, target, mask):
    return (target * (1.0 - mask)) + (source * (mask))
