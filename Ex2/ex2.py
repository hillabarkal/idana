import numpy as np
from numpy import linalg as lg

# Task 1: Geometrical transformations
def getAffineTransformation(pts1, pts2):
    """
    :param: pts1,pts2 - at least 3 pairs of matched points between images A and B
    :return: an affine transformation from image A to image B
    """
    bpts2 = np.hstack(pts2)
    # create arrays xi, yi, zeros, ones
    arrayType = pts1.dtype
    numOfPoints = int(pts1.size / 2.0)
    zeros = np.zeros((numOfPoints,), dtype=int)
    ones = np.ones((numOfPoints,), dtype=int)
    xi = pts1[:, 0]
    yi = pts1[:, 1]

    # create columns of M
    m0 = np.empty((numOfPoints * 2,), dtype=arrayType)
    m0[0::2] = xi
    m0[1::2] = zeros
    m1 = np.empty((numOfPoints * 2,), dtype=arrayType)
    m1[0::2] = yi
    m1[1::2] = zeros
    m2 = np.empty((numOfPoints * 2,), dtype=arrayType)
    m2[0::2] = zeros
    m2[1::2] = xi
    m3 = np.empty((numOfPoints * 2,), dtype=arrayType)
    m3[0::2] = zeros
    m3[1::2] = yi
    m4 = np.empty((numOfPoints * 2,), dtype=arrayType)
    m4[0::2] = ones
    m4[1::2] = zeros
    m5 = np.empty((numOfPoints * 2,), dtype=arrayType)
    m5[0::2] = zeros
    m5[1::2] = ones
    M = np.column_stack((m0, m1, m2, m3, m4, m5))

    # solve linear equation
    [a, b, c, d, tx, ty] = lg.lstsq(M, bpts2)[0]
    affineT = np.array([[a, b, tx],
                        [c, d, ty],
                        [0, 0, 1]],
                       dtype=float)

    return np.array(affineT, dtype=float)


def applyAffineTransToImage(img, affineT):
    """
    :param: an image A and an affine transformation T
    :return: the transformed image T*A
    """
    # should implement a bi-linear interpolation function to calculate new pixel values
    xBound, yBound = img.shape
    xBound -= 1
    yBound -= 1
    newImg = np.zeros(img.shape)
    for y, x in np.ndindex(img.shape):
        newx, newy, _ = np.dot(affineT, [x, y, 1])
        val = bilinearInterpolation(img, x, y)
        newx = np.around(np.clip(newx, 0, xBound)).astype(int)
        newy = np.around(np.clip(newy, 0, yBound)).astype(int)
        newImg[int(newy)][int(newx)] = val
    return newImg


def bilinearInterpolation(img, x, y):
    yBound, xBound = img.shape
    x0 = np.floor(x).astype(int)
    x1 = x0 + 1
    y0 = np.floor(y).astype(int)
    y1 = y0 + 1

    x0 = np.clip(x0, 0, xBound - 1)
    x1 = np.clip(x1, 0, xBound - 1)
    y0 = np.clip(y0, 0, yBound - 1)
    y1 = np.clip(y1, 0, yBound - 1)

    q00 = img[y0, x0]
    q10 = img[y1, x0]
    q01 = img[y0, x1]
    q11 = img[y1, x1]

    wa = (x1 - x) * (y1 - y)
    wb = (x1 - x) * (y - y0)
    wc = (x - x0) * (y1 - y)
    wd = (x - x0) * (y - y0)

    return int(wa * q00 + wb * q10 + wc * q01 + wd * q11)


def singleSegmentationDeformation(Rt, Qt, Pt, Qs, Ps):
    normQPt = lg.norm(Qt - Pt)
    ut = (Qt - Pt) / normQPt
    vt = np.array([ut[1], -ut[0]])

    alpha = np.dot((Rt - Pt), ut) / normQPt
    beita = np.dot((Rt - Pt), vt)

    normQPs = lg.norm(Qs - Ps)
    u = (Qs - Ps) / normQPs
    v = np.array([u[1], -u[0]])

    R = Ps + np.dot(np.dot(alpha, normQPs), u) + np.dot(beita, v)

    return R, beita


def multipleSegmentDefromation(img, Qs, Ps, Qt, Pt, p, b):
    a = 0.001
    newImg = np.zeros(img.shape)
    for y, x in np.ndindex(img.shape):
        Rt = np.array([x, y])
        sum1 = 0  # will hold sum of Wi*Ri for all i
        sum2 = 0  # will hold sum of Wi for all i
        
        for i in range(0, len(Qs)):
            Ri, beita = singleSegmentationDeformation(Rt, Qt[i], Pt[i],
                                                      Qs[i], Ps[i])
            temp = np.abs(Qs[i] - Ps[i])
            temp = lg.norm(temp)
            temp = np.power(temp, p)

            temp /= (a + np.abs(beita))
            wi = np.power(temp, b)

            sum1 += (Ri * wi)
            sum2 += wi

        # final mapping
        R = sum1 / sum2
        # bilinear interpolation to get pixel value
        val = bilinearInterpolation(img, R[0], R[1])
        newImg[y][x] = val
    return newImg


# Task 2: Image Gradients
def imGradSobel(img):
    """
    :param img: an image
    :return: the gradient images (direction and magnitude)
    using the Sobel operator to calculate the image gradient.
    """
    newImage = np.copy(img)
    newImage = np.lib.pad(newImage, ((1, 1),), 'reflect')
    N = np.copy(newImage)
    Gx = np.zeros(img.shape, dtype=int)
    Gy = np.zeros(img.shape, dtype=int)

    # sobel operator:
    x1 = np.array([[1, 2, 1]]).T
    x2 = np.array([[-1, 0, 1]])
    y1 = np.array([[-1, 0, 1]]).T
    y2 = np.array([[1, 2, 1]])

    for y, x in np.ndindex(img.shape):
        if x == 0 or y == 0 or x == img.shape[0] or y == img.shape[1]:
            continue
        A = np.array([[newImage[y - 1, x - 1], newImage[y - 1, x], newImage[y - 1, x + 1]],
                      [newImage[y, x - 1],     newImage[y, x],     newImage[y + 1, x]],
                      [newImage[y + 1, x - 1], newImage[y + 1, x], newImage[y + 1, x + 1]]])

        temp = x1[:] * (x2[:] * A[:])
        Gx[y, x] = np.sum(temp)

        temp = y1[:] * (y2[:] * A[:])
        Gy[y, x] = np.sum(temp)

    magnitude = np.sqrt(np.power(Gx, 2) + np.power(Gy, 2))

    return Gx, Gy, magnitude
