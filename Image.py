'''
Created on 21. apr. 2016

@author: jbs
'''

import cv2
import traceback

import numpy as np
import pylab as pl
# from gfuncs import isScalar


class Image:
   def __init__(self):
      self.debug = False
      
   def plotBeforeAfter(self, img_before, img_after, title, filename=None):
         fn = pl.figure()
         fn.set_size_inches(img_before.shape[1]/100, 2*img_before.shape[0]/100)

#          axS = fn.add_subplot(111)
#          axS.set_title(title)
         ax = fn.add_axes([0,0,0.5,1.0])
#          ax = fn.add_subplot(211)
         ax.imshow(cv2.cvtColor(img_before, cv2.COLOR_BGR2RGB))
         ax.set_title("Before")
         ax2 = fn.add_axes([0,0.5,0.5,1.0])
         ax2.imshow(cv2.cvtColor(img_after, cv2.COLOR_BGR2RGB))
         ax2.set_title("After")
         
         if filename:
            fn.savefig(filename, dpi=100)
         else:
            fn.show()
   
   def opening(self, img, kernel=np.ones((3,3)), iterations = 1, debug=False):
      img_res = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations = iterations)
   
      if debug or self.debug:
         self.plotBeforeAfter(img, img_res, "Image::opening()")
      
      return img_res
   
   def dilate(self, img, kernel=np.ones((3,3)), iterations=1, debug=False):
      # sure background area
      img_out = cv2.dilate(img, kernel=kernel, iterations=iterations)

      if debug or self.debug:
         self.plotBeforeAfter(img, img_out, "Image::dilate()")
         
      return img_out
   
   def distance(self, img, debug=False):
      img_out = cv2.distanceTransform(img, cv2.DIST_L2, 5)
   
      if debug or self.debug:
         self.plotBeforeAfter(img, img_out, "Image::distance()")
         
      return img_out
   
   def threshold(self, img, threshold=(0x04, 0x98, 0xb), debug=False):
      
      threshold = np.array(threshold)
      
      # If threshold is specified as color we use that
      if threshold.size == 3:
         if len(img.shape) == 3:
            img_out = img.copy()
            right_colored_pixels = np.logical_or(np.logical_or(img[:,:,0] != threshold[0], img[:,:,1] != threshold[1]), img[:,:,2] != threshold[2])
            img_out[:,:,0][right_colored_pixels] = 0
            img_out[:,:,1][right_colored_pixels] = 0
            img_out[:,:,2][right_colored_pixels] = 0
         else:
            img_out = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            threshold_bw = cv2.cvtColor(threshold.reshape((1,1,-1)), cv2.COLOR_BGR2GRAY)
            img_out[img_out == threshold_bw] = 0
            print "ERROR: Image::threshold() - Can not use color to filter a non color image"
      # Greytone image
      else:
         if len(img.shape) == 3:
            img_out = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

         img_out[img_out == threshold] = 0
         
      ret, img_out = cv2.threshold((img_out-img_out.min())*255/(img_out.max()-img_out.min()), 0.5*img_out.max(), 255, 0)
         
      if debug or self.debug:
         self.plotBeforeAfter(img, img_out, "Image::threshold()")
      
      return img_out
         
   def findMoments(self, img, debug=False):
      cnts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]

      moments = []
      for c in cnts:
         try:
            # compute the center of the contour
            if c.shape == (2,1,2):
               cX = int(np.mean(c[:,0,0]))
               cY = int(c[0,0,1])
            else:
               M = cv2.moments(c)
               cX = int(M["m10"] / M["m00"])
               cY = int(M["m01"] / M["m00"])
          
            moments.append([cX, cY])
            
            if debug or self.debug:
               # draw the contour and center of the shape on the image
               cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
               cv2.circle(img, (cX, cY), 1, (255, 255, 255), -1)
               cv2.putText(img, "center", (cX - 20, cY - 20),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
             
               # show the image
               cv2.imshow("Image", img)
               cv2.waitKey(1000)
               
         except Exception as e:
            print e
            print traceback.format_exc()
            
      return np.array(moments)
      
