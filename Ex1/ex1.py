import cv2
import numpy as np
import cv2

# Task 1: Spatial sampling
def getSampledImageAtResolution(dim, pixelSize, k=2):
    x0 = dim[0]
    x1 = dim[1]
    y0 = dim[2]
    y1 = dim[3]

    numXPixels = int(float(x1 - x0) / pixelSize)
    numYPixels = int(float(y1 - y0) / pixelSize)

    X = []
    Y = []

    for i in range(0, numXPixels):
        val = x0 + (i * pixelSize)
        X.append(val)

    X = np.array(X, float)
    X = np.multiply(3, X)

    for i in range(0, numYPixels):
        val = y0 + (i * pixelSize)
        Y.append(val)

    Y = np.array(Y, float)
    Y = np.multiply(2, Y)

    Xs, Ys = np.meshgrid(X, Y)
    print("======")
    print(Xs + Ys)
    print("======")
    return np.cos(k * np.pi * (Xs + Ys))

def analyticFunction(x, y, k):
    x = np.multiply(3, x)
    y = np.multiply(2, y)

    tempMatrix = np.add(x, y)

    tempParam = k * np.pi
    tempMatrix = np.multiply(tempParam, tempMatrix)
    return np.cos(tempMatrix)


# Task 2: Quantization
def optimalQuantizationImage(img, k):
    image = cv2.imread(img)
    pixelsNum = image.size / 3 #maybe because its gray there's no need to divide

    epsilon = 0.003

    Q = np.random.randint(0, 256, k)
    Q = np.sort(Q)

    bounds = np.zeros(k + 1, int) #there's a chance it should be float
    for i in range(0, k + 1):
        bounds[i] = (Q[i + 1] - Q[i]) / 2

    probs = calcProbs(pixelsNum, countApperances(img))
    while (calcError(k, Q, probs) < epsilon):



    return 0

#gets the image, returns array with # of appearances of each pixel [0-255]
def countApperances(img):
    numericalVal = cv2.imread(img)
    appearances = np.zeros(256, int)

    for x in np.nditer(numericalVal):
        appearances[x] += 1

    return appearances

def calcProbs(pixelsNum,appearances):
    probs = np.zeros(256, float)
    for i in range(0, appearances):
        probs[i] = appearances[i] / pixelsNum

    return probs

def calcError(k, centroids, probs):

    return 0

# Task 3: Image histograms
# a
def getImageHistogram(img):
    histogram = np.zeros(shape=(256))
    for i in range(0, len(img)):
        for j in range(0, len(img[0])):
            index = img[i][j][0]
            histogram[index] += 1
    return histogram

# b
def getConstrastStrechedImage(grayImg):
    histogram = getImageHistogram(grayImg)
    minVal, maxVal = findMinMaxValues(histogram)
    img = np.copy(grayImg)
    for i in range(0, len(grayImg)):
        for j in range(0, len(grayImg[0])):
            val = grayImg[i][j][0]
            newVal = linearEnhancementOf(val, minVal, maxVal)
            img[i][j] = getGrayPixel(newVal)
    return img

def findMinMaxValues(histogram):
    for i in range(0, 256):
        if histogram[i] != 0:
            break
    minVal = i

    for i in range(0, 256):
        if histogram[255 - i] != 0:
            break
    maxVal = 255 - i

    return minVal, maxVal

def linearEnhancementOf(val, minVal, maxVal):
    return (val - minVal) * 255.0 / float(maxVal - minVal)

def getGrayPixel(val):
    return [val, val, val]

# c
def getHistEqImage(img):
    # Compute a scaling factor, α= 255 / num of pixels
    shape = np.shape(img)
    a = 255.0 / (shape[0] * shape[1])

    # Calculate histogram of the image
    histogram = getImageHistogram(img)

    # Create a look up table
    LUT = []
    # LUT[0] =  α * histogram[0]
    LUT.append(a * histogram[0])

    # for all remaining grey levels: LUT[i] = LUT[i-1] + α * histogram[i]
    for i in range(1, 256):
        val = LUT[i - 1] + a * histogram[i]
        LUT.append(val)

    # for all pixel coordinates: g(x, y) = LUT[f(x, y)]
    image = np.copy(img)
    for x in range(0, shape[0]):
        for y in range(0, shape[1]):
            val = LUT[f(x, y, img, histogram)]
            image[x][y] = val
    return image

def getCumulativeDistribution(histogram):
    P = []
    for i in range(0, 256):
        p = histogram[i] / 255.0
        P.append(p)

    cdf = []
    cdf.append(histogram[0])
    for i in range(1, 256):
        c = cdf[i - 1] + histogram[i]
        cdf.append(c)
    return np.array(cdf)

def f(x, y, img, histogram):
    v = img[x][y][0]
    cdf = getCumulativeDistribution(histogram)
    cdfMin, _ = findMinMaxValues(cdf)
    M, N, _ = np.shape(img)
    return int(255.0 * (cdf[v] - cdfMin) / ((M * N) - 1))
