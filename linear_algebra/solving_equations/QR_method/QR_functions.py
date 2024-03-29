import os, sys
sys.path.append(os.getcwd())
from linear_algebra.functions import *
from typing import List, Tuple

matrix_shape = List[List[float]]
vector_shape = List[float]


def solve_with_qr_decomposition(matrix: matrix_shape) -> vector_shape:
    """
    Solve linear equation using QR decomposition.

    -----
    Info:
    -----
    At first to solve linear equation using QR decomposition, 
    we have to get Q and R matrices and transform initial formula:
    • `Ax = b`

    to:
    • `QRx = b`

    because we decompose A matrix into Q and R matrices => A = QR.

    x: is our coefficients we are willing to find (solve equation).
    To get x, the formula above transforms to:
    • `(QR) @ (QR)^-1 @ x = (QR)^-1 @ b    | * (QR)^-1`
    • `x = R^-1 @ Q.T @ b`
    
    because Q.T = Q^-1 and A@A^-1 = I.

    So, matrix product of Invertible matrix R (R^-1), 
    transposed matrix (Q) and const vector values (b)
    will solve our equation.

    ------
    Steps:
    ------
    1. Split original extended matrix into A (original matrix) 
    and b (answer vector)

    2. Get QR matrices

    3. Find coefficient vector using formula: R^-1@Q.T@b

    Args:
        matrix (matrix_shape): Original extended matrix

    Returns:
        vector_shape: Vector of unknown variables
    """
    A, b = split_by_vectors(matrix)
    Q, R = qr_decomposition(A)

    print_matrix(Q, "Q matrix:", 4)
    print_matrix(R, "R matrix:", 4)

    params = get_equation_params(Q, R, b)
    return params


def qr_decomposition(A) -> Tuple[matrix_shape, matrix_shape]:
    """
    Return Q and R matrices.

    Info:
    -----
    QR factorization is another method to solve linear equation. 
    QR factorization decompose original matrix into 2: 
    Orthogonal Q matrix and triangular R matrix.

    Q: Orthonormalized matrix. To get Q matrix use Gram-Schmidt process.
    R: Triangular matrix. Q.T@A

    Formula:
    --------
    A = QR -> Original matrix is the matrix product of Q and R

    Q.T@Q = I -> Matrix product of transposed Q and Q 
    is equal to Identity matrix

    -----
    Args:
        A (matrix_shape): Original matrix

    Returns:
        matrix_shape: Q - orthonormalized matrix
        matrix_shape: R - triangular matrix
    """
    Q = gram_schmidt_orthonormalization(A)

    Q = transpose(Q)  # Return Q back to original shape
    A = transpose(A)  # Return A back to original shape
    R = get_r_matrix(Q, A)

    return Q, R


def gram_schmidt_orthonormalization(A: matrix_shape) -> matrix_shape:
    """
    Return orthonormalized matrix (Q).

    -----
    INFO:
    -----
    This function applies Gram-Schmidt process to the matrix and 
    returns orthonormalized matrix. 
    Orthonormalized matrix (all vectors in it tho) has the length (norm) = 1
    and all vectors are orthogonal to each other. It means, that scalar product
    of vi and vj (vi, vj) = 0, but (vi, vi) = 1.
    
    This means, that:
    
    1.) Q.T @ Q = I
    
    where 
        Q: orthonormalized matrix
        @: matrix product
        I: Identity matrix

    2.) if we can calculate "I" matrix, this means, we can find invertible matrix Q^-1.
    Actually here Q^-1 = Q.T, because Q @ Q.T = Q @ Q^-1 = I => Q.T = Q^-1

    This process is useful when solving linear equations.

    Args:
        A (matrix_shape): Original matrix
    
    Steps:
    -------
    1. Get orthogonal vectors "u" for each initial vector "v"
    
    2. Normalize vectors "u" by it's norm
    """
    U = orthogonalize_matrix(A)
    Q = normalize_matrix(U)
    return Q


def orthogonalize_matrix(A: matrix_shape) -> matrix_shape:
    """
    Return ortogonal matrix.

    Args:
        A (matrix_shape): Original matrix, represented with list of lists.

    Returns:
        matrix_shape: Transformed orthogonal matrix

    ---------------------------------
    Formula for orthogonal transform:
    ---------------------------------
    v : initial vector, that will be transformed
    u : orthogonal vector

    u1 = v1

    u2 = v2 - proj_b1(v2)

    u3 = v3 - proj_b1(v3) - proj_b2(v3)
    
    ...

    un = vn - proj_u1(vn) - proj_u2(vn) - ... - proj_un-1(vn)
    """
    m, n = len(A), len(A[0])  # Columns (vectors), Rows (items)
    U = [[] for _ in range(m)]

    # First U column will be the same as the A column
    U[0] = list(A[0])

    # For each vector...
    for current_column in range(1, m):
        U[current_column] = list(A[current_column])
        # For each prev column to the current column...
        for prev_column in range(current_column):
            proj = projection_value(A, U, current_column, prev_column)
            # For each item in this column...
            for i in range(n):
                U[current_column][i] -= proj * U[prev_column][i]
    return U


def normalize_matrix(U: matrix_shape) -> matrix_shape:
    """
    Return normalized matrix.
    
    Info:
    -----
    Divide each item in vector by it's norm. ||v|| - norm (length).

    Formula:
    --------

    e1 = u1 / ||u1||

    e2 = u2 / ||u2||

    ...

    en = un / ||un||
    """
    m, n = len(U), len(U[0])  # Columns, Rows
    Q = [[0] * n for _ in range(m)]

    # For each vector...
    for current_vector in range(m):
        length = get_vector_norm(U[current_vector])
        # For each item in vector...
        for i in range(n):
            Q[current_vector][i] = U[current_vector][i] / length
    return Q


def projection_value(A: matrix_shape, U: matrix_shape, i: int, j: int) -> float:
    """
    Return projection value of a certain column. (Only multiplication value)

    Args:
        A (matrix_shape): Original matrix
        U (matrix_shape): Transformed matrix
        i (int): Original vector index
        j (int): Transformed vector index (Previously transformed vectors)
    
    Returns:
        float: Alpha value for vector transformation

    --------------------------
    Formula:
    ---------
    proj = < v, u > / < u, u >

    < >: Scalar product of 2 vectors
    """
    f = A[i]
    u = U[j]
    f_u = mul(f, u)
    u_u = mul(u, u)
    return f_u / u_u


def get_r_matrix(Q: matrix_shape, A: matrix_shape) -> matrix_shape:
    """Calculates triangular matrix R

    Formula: 
    --------
    `R = Q.T@A`

    ---------

    Args:
        Q (matrix_shape): Orthonormalized matrix (n x m)
        A (matrix_shape): Original matrix (n x m)

    Returns:
        matrix_shape: Matrix R (m x m)
    """
    return matmul(transpose(Q), A)


def get_equation_params(Q: matrix_shape, R: matrix_shape, b: vector_shape):
    """
    Return matrix coefficients using QR matrices and answer vector b.

    -----
    Info:
    -----
    The formula of linear equation is:

    Ax = b, where A - is an original coefficient matrix

                  x - vector of unknown variables

                  b - answer vector (contant)

    Matrix A is decomposed into Q and R matrices and formula became:

    `QRx = b`

    To find x vector we multiply each side of equation by (QR)^-1, 
    where (QR)^-1 is the inverse matrix. As we know, Q.T@Q = I,
    so Q.T = Q^-1 and formula became:

    `x = R^-1 @ Q.T @ b`

    --------
    Formula:
    --------
    •`C = Q.T@B`

    •`x = R^-1@C`

    ------
    Steps:
    ------
    1. Find C

    2. Find inverse matrix of R

    3. Find vector coefficients by matrix product of inverse R and C


    Args:
        Q (matrix_shape): Orthogonal matrix. Shape: (n, m)

        R (matrix_shape): Triangular matrix. Shape: (m, m)
        
        b (vector_shape): Answer vector. Shape: (n, 1)

    Returns:
        vector_shape: List of unknown variables
    """
    b = transpose(list([b]))
    C = matmul(transpose(Q), b)  # Shape (m, 1)

    r_inverse = inverse(R)

    print_matrix(r_inverse, "Inverse R matrix:", 4)
    I = matmul(R, r_inverse)
    print_matrix(I, "R@R-1 = I matrix:", 4)

    RC = matmul(r_inverse, C)
    RC = transpose(RC)[0]
    return RC
