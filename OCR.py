from __future__ import print_function

import inspect
import os
from nothreads import myPopen
import shutil
import fileinput


TESSERACT_PATH = os.path.dirname(inspect.getfile(inspect.currentframe())) + "/tesseract"
TRAINING_PATH = TESSERACT_PATH + "/train"
FONT_PATH = TESSERACT_PATH + "/fonts"
LATEX_PATH = TESSERACT_PATH + "/latex"

QT_BOX_EDITOR="/home/me/Apps/QtBoxEditor/zdenop-qt-box-editor-86691a2/qt-box-editor-1.12dev"
TESSBOXES = "/home/me/Apps/tessboxes-0.8/src/tessboxes"

# The user object deals with user info 
class OCR():
   
   def __init__(self, name=None):
      
      pass
   
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
      
      
   def generateTrainingSet(self, fontfile, method='luatex'):
      
      if method == 'luatex':
         self.generateTrainingSetWithLatex(fontfile)


      
      
   def train(self, fontfile, use_lua_boxes=True):
      
      self.generateTrainingSet(fontfile)
      
      fontname = os.path.splitext(os.path.basename(fontfile))[0]
      
      old_path = self.changePath(TRAINING_PATH)
      
      ##########################
      # Create character boxes #
      ##########################
      
      if not use_lua_boxes:
         myPopen("tesseract %s.tif %s batch.nochop makebox"%(fontname, fontname))
         # ^ This step must be repeated for all training images / fonts
         
         # This method must be inspected!!! Make changes where needed
         myPopen(QT_BOX_EDITOR + " %s.lua.tif"%fontname)
         
      else:
      
         shutil.copy2("%s/%s.box"%(LATEX_PATH, fontname), "./%s.box"%fontname)
         
         # Modify LUA box file so it matches the Tesseract format 
         for line in fileinput.input("./%s.box"%fontname, inplace=True):
            line_no_commas = line.replace(',', '')
            line_no_newlines = line_no_commas.replace('\n', ' 0 \n')
            print(line_no_newlines, end='')
         
#       myPopen(QT_BOX_EDITOR + " %s.lua.tif"%fontname)
      
      myPopen("%s.tif %s nobatch box.train"%(fontname,fontname))
      
      # Generate the set of known characters
      myPopen("unicharset_extractor %s.box"%(fontname))
      
      # Generate font info / clustering
      # format: <fontname> <italic> <bold> <fixed> <serif> <fraktur>
      file = open('font_properties', 'w+')
      file.write("%s 0 1 1 0 0"%fontname)
      file.close()
      
      
      myPopen("shapeclustering -F font_properties -U unicharset %s.tr"%fontname)
      myPopen("mftraining -F font_properties -U unicharset -O non.unicharset %s.tr"%fontname)
      myPopen("cntraining %s.tr"%fontname)
      
      # Combine everything
      shutil.copy2("inttemp", "eng.inttemp")
      shutil.copy2("normproto", "eng.normproto")
      shutil.copy2("pffmtable", "eng.pffmtable")
      shutil.copy2("shapetable", "eng.shapetable")
      shutil.copy2("unicharset", "eng.unicharset")

      myPopen("combine_tessdata eng.")
      
      
#       
#       cp inttemp non.inttemp
#       cp normproto non.normproto
#       cp pffmtable non.pffmtable
#       cp shapetable non.shapetable
#       cp unicharset non.unicharset
#       
#       combine_tessdata non.
#       
#       cp non.traineddata ../../

      
      
      
      
      
      self.changePath(old_path)
      
      

#       self.current = user
#       self.accounts = self.listAccounts()
#       
#       printAction("Current user:")
#       myPrint(user)
#       
#       os.chdir(old_dir)
      
#       
#    def getCurrent(self):
#       
#       return self.current
#    
#    
#    def listAccounts(self):
#       
#       account = Accounts()
#       return account.getAccountsFor(self.current)
   

      
      
if __name__ == "__main__":
   
   ocr = OCR()

   ocr.train("eng.Supercell-Magic.exp0.ttf")
   
   pass