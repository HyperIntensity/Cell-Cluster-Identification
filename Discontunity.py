''''
This program is able to detect discontinuity amongst cell clusters. 
Author: Yashvanth Singamaneni
Date: 6/28/2023
Note: Final Working Program  
Inspired by: fmw42(Stackoverflow) and Samhitha Kolla(samhitha.kolla@wustl.edu)
'''''

#Import Statments
import cv2
import numpy as np
import pandas as pd
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
import math
import warnings
import os
warnings.filterwarnings("ignore")

#Loading multiple files to process together.
Folder_Name = 'Cluster_Images'
File_Names = os.listdir(Folder_Name)
print(len(File_Names))

for i in range(len(File_Names)):
   pathfile = os.path.join(Folder_Name,File_Names[i])

   #Reading path file and performing necessary operations
   img = cv2.imread(pathfile)
   gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
   ret, thresh = cv2.threshold(gray, 127, 255, 1)

   #Creating a structuring element to perform morphological operations
   kernel = np.ones((7, 7),np.uint8)
   erosion = cv2.morphologyEx(thresh, cv2.MORPH_ERODE, kernel, iterations = 2)

   ret, thresh1 = cv2.threshold(erosion, 127, 255, 1)
   blur = cv2.blur(thresh1, (15, 15))

   ret, thresh2 = cv2.threshold(blur, 145, 255, 0)

   #Performing a second morphological operation.
   kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
   final = cv2.morphologyEx(thresh2, cv2.MORPH_ERODE, kernel1, iterations = 2)

   #Finding Contours within the image
   contours,hierarchy = cv2.findContours(final, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

   #Credit: Samhitha Kolla
   def count_points(roi):
      """
      This function counts the number of points(secretions) within the clusters
      :param roi: Region of Interest
      :return: labels, unique label counts
      """
      # Performing Mean Shift Filtering
      shifted = cv2.pyrMeanShiftFiltering(roi, 21, 51)

      # Converting the image to grayscale
      gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)

      # Thresholding using Binary and OTSU
      thrsh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
      # Using Watershed Algorithm
      D = ndimage.distance_transform_edt(thrsh)
      localMax = peak_local_max(D, indices=False, min_distance=1, labels=thrsh)
      markers = ndimage.label(localMax)[0]
      lbls = watershed(-D, markers, mask=thrsh)

      return lbls, len(np.unique(lbls)) - 1

   # Find the convex hull for all the contours
   ClusterCounter = 0
   for cnt in contours:
      x, y, w, h = cv2.boundingRect(cnt)
      size = 89 #Change the size according to the images(Refer to README)

      # Filtering out smaller clusters.
      """
      Refer to the commented code below this program to 
      utilize the Contours_Area function instead of this if this function produces unwanted results.
      """
      if size < w < final.shape[0] and size < h < final.shape[1]:
         hull = cv2.convexHull(cnt)

         # Comment for a Silhouette Contour
         #final = cv2.drawContours(img,[cnt],0,(0,255,0),10)

         # Comment for a polygon Countour
         final = cv2.drawContours(img,[hull],0,(0,0,255),10)
         ClusterCounter += 1
         ROI = final[y:y + h, x:x + w]

         # Counting the number of secretions within each cluster
         lbls, count = count_points(ROI)


   # Display the image with contours drawn
   cv2.waitKey(0)
   cv2.destroyAllWindows()
   filename = pathfile.split(".")[0]
   cv2.imwrite(pathfile + '_Output.jpg', final)
   with open(filename + "_Output.txt", "w") as file:
      file.write("Image Captured: " + str(filename) + "\n")
      cv2.imwrite(pathfile + '_Output.jpg', final)
      file.write("Clusters: " + str(ClusterCounter) + "\n")


""""
Use this function to get efficient cell cluster identification:

Contour_Size = 80
   if cv2.contourArea(cnt) > size:
   ##############################
   ##                          ##
   ##    Draw Contours here    ##
   ##                          ##
   ##############################
   
"""""
