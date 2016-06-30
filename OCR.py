from __future__ import print_function

import inspect
import os
from nothreads import myPopen, myRun
from printing import myPrint
import numpy as np
import pylab as pl
import shutil
import fileinput
from Settings import Settings
import cv2

TESSERACT_PATH = os.path.dirname(inspect.getfile(inspect.currentframe())) + "/tesseract"
TRAINING_PATH = TESSERACT_PATH + "/train"
FONT_PATH = TESSERACT_PATH + "/fonts"
LATEX_PATH = TESSERACT_PATH + "/latex"

QT_BOX_EDITOR="/home/me/Apps/QtBoxEditor/zdenop-qt-box-editor-86691a2/qt-box-editor-1.12dev"
TESSBOXES = "/home/me/Apps/tessboxes-0.8/src/tessboxes"

# The user object deals with user info 
class ImageAnalysis():
   
   def __init__(self, settings):
      self.settings = settings
   
   def changePath(self, new_path):
      old_path = os.getcwd()
      if not os.path.exists(new_path):
         os.mkdir(new_path)
      os.chdir(new_path)
      
      return old_path
   


   
   def generateTrainingSetWthLatex(self, fontfile):
      old_path = self.changePath(LATEX_PATH)
      
      # Get a copy of the font
      shutil.copy2("%s/%s"%(FONT_PATH, fontfile), "./")
      
      # Make not of fontname
      fontname = os.path.splitext(os.path.basename(fontfile))[0]
      
      # Create the LUA LaTeX file
      file = open(fontname+".tex", 'w')
      file.write(
         "\documentclass{article}                                          \n" +
         "\usepackage{fontspec}                                            \n" +
         "\setlength{\parindent}{0pt}                                      \n" +
         "\setlength{\\baselineskip}{12pt}                                   \n" +
         "\\renewcommand{\\baselinestretch}{1}                                \n" +
         "\setlength{\parskip}{0pt}                                   \n" +
         "                                                                 \n" +
         "% Total left margin: 1in + \hoffset + odd-/evensidemargin        \n" +
         "\setlength\hoffset{0pt}                                          \n" +
         "\setlength\oddsidemargin{0pt}                                    \n" +
         "\setlength\evensidemargin{0pt}                                   \n" +
         "                                                                 \n" +
         "% Total top margin: 1in+\voffset-\topmargin+\headheight+\headsep \n" +
         "\setlength\\voffset{2.5pt}                                          \n" +
         "\setlength\\topmargin{0pt}                                        \n" +
         "\setlength\headheight{0pt}                                       \n" +
         "\setlength\headsep{0pt}                                          \n" +
         "                                                                 \n" +
         "\usepackage[resolution=300,startx=1in,starty=1in]{boxes}         \n" +
         "\setmainfont{%s}\n"%fontfile +
         "\\begin{document}\n" +
         "\\typeout{\\the\\baselineskip}\n" +
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ\\\\\n" +
         "abcdefghijklmnopqrstuvwxyz\\\\\n" +
         "0123456789\n" +
         "\end{document}"
         )
      file.close()
   
      # Run LuaLaTex
      myPopen("lualatex "+fontname+".tex")
      
      # Convert PDF to Tif
      myPopen("gs -q -r300x300 -dNOPAUSE -sDEVICE=tiffg4 -sOutputFile=%s/%s.tif %s.pdf -c quit"\
              %(TRAINING_PATH, fontname, fontname))
      
      # Convert to pbm and use texboxes command to visualize the result
      myPopen("pdftoppm -mono -freetype yes -aa yes -r 300 %s.pdf > %s.pbm"%(fontname, fontname))
      
      myPopen(TESSBOXES + " %s.pbm %s.box > %s/%s_box_overlay.pbm"%(fontname, fontname, fontname))
      
      self.changePath(old_path)
      
      
   def generateTrainingSetWithTesseract(self, fontfile, training_text=''):
      old_path = self.changePath(TRAINING_PATH)
      
      # Extract font name
      fontname = os.path.splitext(os.path.basename(fontfile))[0]
      fontname_short = fontname.replace(".exp0","")
      fontname_short = fontname_short.replace("eng.","")
      
      if training_text == '':
         shutil.copy2("sample_training_text.txt", "training_text.txt")
      else:
         ext = os.path.splitext(training_text)[1]
         
         if ext == '':
            file = open("training_text.txt", 'w')
            file.write(training_text)
            file.close()
         
         elif training_text != "training_text.txt":
            shutil.copy2(training_text, "training_text.txt")
      
      myPopen("%s/text2image --text=training_text.txt --outputbase=%s --fonts_dir=%s --font='%s'"\
              %(self.settings.TESSERACT_PATH, fontname, self.settings.TESSERACT_FONTS_PATH, fontname_short))
      
      self.changePath(old_path)
      
   def generateTrainingSet(self, fontfile, method='tesseract', training_text=''):
      
      if method == 'luatex':
         self.generateTrainingSetWithLatex(fontfile)
   
      elif method == "tesseract":
         self.generateTrainingSetWithTesseract(fontfile, training_text)


      
      
   def train(self, fontfile, method='tesseract', training_text=''):
      
      self.generateTrainingSet(fontfile, method, training_text)
      
      fontname = os.path.splitext(os.path.basename(fontfile))[0]
      fontname_short = fontname.replace(".exp0","")
      fontname_short = fontname_short.replace("eng.","")
      
      old_path = self.changePath(TRAINING_PATH)
      
      ##########################
      # Create character boxes #
      ##########################
      
      if method == 'manual':
         myPopen("%s/tesseract %s.tif %s batch.nochop makebox"%(self.settings.TESSERACT_PATH, fontname, fontname))
         # ^ This step must be repeated for all training images / fonts
          
         # This method must be inspected!!! Make changes where needed
         myPopen(QT_BOX_EDITOR + " %s.lua.tif"%fontname)
          
      elif method == 'luatex':
       
         shutil.copy2("%s/%s.box"%(LATEX_PATH, fontname), "./%s.box"%fontname)
          
         # Modify LUA box file so it matches the Tesseract format 
         for line in fileinput.input("./%s.box"%fontname, inplace=True):
            line_no_commas = line.replace(',', '')
            line_no_newlines = line_no_commas.replace('\n', ' 0 \n')
            print(line_no_newlines, end='')
          
#       myPopen(QT_BOX_EDITOR + " %s.lua.tif"%fontname)
       
      # Train Tesseract on the tif-image
      myPopen("%s/tesseract %s.tif %s nobatch box.train"%(self.settings.TESSERACT_PATH, fontname, fontname))
       
      # Generate the set of known characters
      myPopen("%s/unicharset_extractor %s.box"%(self.settings.TESSERACT_PATH, fontname))
       
      # Generate font info / clustering
      # format: <fontname> <italic> <bold> <fixed> <serif> <fraktur>
      file = open('font_properties', 'w+')
      file.write("%s 0 1 1 0 0"%fontname_short)
      file.close()
       
       
      myPopen("%s/shapeclustering -F font_properties -U unicharset %s.tr"%(self.settings.TESSERACT_PATH, fontname))
      myPopen("%s/mftraining -F font_properties -U unicharset -O eng.unicharset %s.tr"%(self.settings.TESSERACT_PATH, fontname))
      myPopen("%s/cntraining %s.tr"%(self.settings.TESSERACT_PATH,fontname))
       
      # Combine everything
      
      os.rename("inttemp",    "eng.inttemp")
      os.rename("normproto",  "eng.normproto")
      os.rename("pffmtable",  "eng.pffmtable")
      os.rename("shapetable", "eng.shapetable")
#       shutil.copy2("unicharset", "eng.unicharset")
 
      myPopen("%s/combine_tessdata eng."%self.settings.TESSERACT_PATH)
      
      
      self.changePath(old_path)
      
      
   def readImage(self, image_file, xbounds=None, ybounds_old=None):
      try:
         image = myRun(cv2.imread, image_file)
      except Exception, e:
         myPrint(e)
         myPrint("Unable to read image %"%image_file, msg_type='error')
         
      if not xbounds:
         if not ybounds_old:
            return image
         else:
            return image[ybounds_old[0]:ybounds_old[1], :]
      else:
         if not ybounds_old:
            return image[:, xbounds[0]:xbounds[1]].copy()
         else:
            return image[ybounds_old[0]:ybounds_old[1], xbounds[0]:xbounds[1]].copy()
      
      
   def preOCR(self, image_name, color_mask=(1, 1, 1), threshold=180, invert=True, xbounds=None, ybounds_old=None):
      
      import scipy.interpolate as interpolate
      import pylab as pl
      
      DEBUG = False
   
      image = self.readImage(image_name, xbounds, ybounds_old)
   #   image = self.readImage(image_name)
      
      # Adjust color information
      image[:, :, 0] = image[:, :, 0] * color_mask[0]
      image[:, :, 1] = image[:, :, 1] * color_mask[1]
      image[:, :, 2] = image[:, :, 2] * color_mask[2]
      
      if DEBUG:
         pl.imshow(image)
         pl.show()
      
      # Convert to grey scale
      image = myRun(cv2.cvtColor, image, cv2.COLOR_BGR2GRAY)
      
      if DEBUG:
         pl.imshow(image, cmap=pl.cm.Greys_r)
         pl.show()
      
      # Normalize
      img_min, img_max = image.min(), image.max()
      image = 255 * (image - float(img_min)) / (float(img_max) - img_min)
      
      if DEBUG:
         pl.imshow(image, cmap=pl.cm.Greys_r)
         pl.show()
      
      #Upinterpolate
      M, N = image.shape
      m_idx = np.linspace(0, 1, M)
      n_idx = np.linspace(0, 1, N)
      
      K = 2 # Upsampling factor
      m_up_idx = np.linspace(0, 1, M * K)
      n_up_idx = np.linspace(0, 1, N * K)
         
      image = interpolate.RectBivariateSpline(m_idx, n_idx, image, kx=4, ky=4)(m_up_idx, n_up_idx)
         
      #Inversion
      if invert:
         image = 255 - image
         
      if DEBUG:
         pl.imshow(image, cmap=pl.cm.Greys_r)
         pl.show()
         
      # Thresholding
      img = image ** 20
      image = 255 * img / (img + float(threshold) ** 20)
   #   image = 255/(1+(float(threshold)/image)**20)
      
   #   image[image>=threshold] = 255
   #   image[image< threshold] = 0
   
      # Reverting to int8
      image = image.astype('uint8')
      
      myRun(cv2.imwrite, image_name.strip('.png') + '_processed.png', image)
      
      return image
      
   
   def runOCR(self, image, mode='', lang='eng'):
      
      if mode == 'line':
         psm = '-psm 7'
      elif mode == '':
         psm = ''
      else:
         myPrint("ERROR: runOCR() - Mode %s is not supported")
         return ''
      
      if lang == 'event_enemy':
         language = 'non'
      else:
         language = 'eng'
      
      myRun(cv2.imwrite, 'tmp.png', image)
      myPopen("echo '' > text.txt")
      myPopen("tesseract tmp.png text %s -l %s >/dev/null 2>&1" % (psm, language))
      
      if os.path.getsize('text.txt') == 1:
         myPrint("ERROR: runOCR() returned no output")
         return ''
      
      # TODO make sure file is not empty!!!
      text = open('text.txt', 'r').read()
   #   text  = re.sub(r'\s', '', text) # Remove whitespaces
   #   text  = re.sub(r',', '', text) # Remove commas
      text = re.sub(r'\n', '', text) # Remove newlines
      
      return text

      
      
if __name__ == "__main__":
   
   settings = Settings()
   
   ocr = ImageAnalysis(settings)

   ocr.train(fontfile="eng.Supercell-Magic.exp0.ttf", method="tesseract", training_text="/home/me/clash/coc_training_text.txt")
   
   pass