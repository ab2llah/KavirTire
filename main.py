import cv2
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import convolve2d as conv2
from skimage import color, data, restoration

vidcap = cv2.VideoCapture('2.mpg')
totalFrames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)

# indicator constant parameters
_height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
_width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))

_IndicatorHeight = int(0.04 * _height)
_IndicatorOffset = int(0.5 * _height)

def enhance(frame):

    # RGB to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # remove sides
    ret2, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    openedBinaryImage = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # equalize histogram
    equalized = cv2.equalizeHist(openedBinaryImage * gray)

    # denoising
    #denoised = cv2.fastNlMeansDenoising(equalized)

    return equalized
    # # deconvolution
    # psf = np.ones((5, 5)) / 25
    # gray = restoration.richardson_lucy(gray, psf, iterations=30)

    #gaussian = cv2.GaussianBlur(denoised,(5,5),0)
    # laplacianKernel = np.array((
    #     [-1, -1, -1],
    #     [-1, 10, -1],
    #     [-1, -1, -1]), dtype="int")
    #
    # laplacian = cv2.filter2D(denoised,-1,laplacianKernel)
    # laplacianKernel = cv2.Laplacian(denoised, cv2.CV_64F)
    # laplacianKernel += abs(np.min(laplacianKernel))
    # laplacianKernel *= (255/np.max(laplacianKernel))
    # laplacian = denoised * laplacianKernel
    # laplacian *= (255 / np.max(laplacian))
    # laplacian = np.array(laplacian).astype(np.uint8)

    #return denoised

def findIndicator(frame, indicator):
    # Apply template Matching
    res = cv2.matchTemplate(frame, indicator, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum

    top_left = max_loc
    bottom_right = (top_left[0] + _width, top_left[1] + _IndicatorHeight)

    return [top_left, bottom_right]

# constructing the result image


resultImage = np.zeros((1, _width))
outputImage = np.zeros((1,_width))

def appendToImage(frameNumber):
    print(frameNumber)
    global resultImage,outputImage
    success, originalFrame = vidcap.read()
    frame = enhance(originalFrame)
    gray = cv2.cvtColor(originalFrame, cv2.COLOR_RGB2GRAY)

    if frameNumber == 1:
        rect = frame[0:_IndicatorOffset+_IndicatorHeight, 0:_width]
        grayRect = gray[0:_IndicatorOffset+_IndicatorHeight, 0:_width]
        resultImage = np.append(resultImage, rect, axis=0)
        outputImage = np.append(outputImage, grayRect, axis=0)
        appendToImage(frameNumber+1)
    elif frameNumber < totalFrames-2:
        resultImageHeight, resultImageWidth = np.shape(resultImage)
        indicator = np.array(resultImage[resultImageHeight-1-_IndicatorHeight:resultImageHeight-1, 0:resultImageWidth]).astype(np.uint8)
        topLeft, bottomRight = findIndicator(frame, indicator)
        if bottomRight[1] < _IndicatorOffset :
            print("moving to next indicator")
            rect = frame[bottomRight[1]:bottomRight[1]+_IndicatorHeight, 0:_width]
            grayRect = gray[bottomRight[1]:bottomRight[1] + _IndicatorHeight, 0:_width]
            resultImage = np.append(resultImage, rect, axis=0)
            outputImage = np.append(outputImage, grayRect, axis=0)
            appendToImage(frameNumber + 1)
        else:
            print("diff: ", bottomRight[1] - _IndicatorOffset)
            appendToImage(frameNumber + 1)
    else:
        resultImageHeight, resultImageWidth = np.shape(resultImage)
        indicator = np.array(resultImage[resultImageHeight - 1 - _IndicatorHeight:resultImageHeight - 1, 0:resultImageWidth]).astype(np.uint8)
        topLeft, bottomRight = findIndicator(frame, indicator)
        rect = frame[bottomRight[1]:_height, 0:_width]
        grayRect = gray[bottomRight[1]:_height, 0:_width]
        resultImage = np.append(resultImage, rect, axis=0)
        outputImage = np.append(outputImage, grayRect, axis=0)

appendToImage(1)
plt.imshow(resultImage)
plt.show()
plt.imsave("test.4.raw.jpg", resultImage)
