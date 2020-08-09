from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from cbirtools import Descriptor, Distance
from imagemanager import ImageManager
import cv2

class CBIR(Frame):
    def __init__(self, root, imageManager, w, h):
        self.w, self.h = w, h
        self.root = root
        # variables
        self.imgManager = imageManager # image manager
        self.imageList = imageManager.get_imageList()
        self.photoList = imageManager.get_photoList()
        self.indexBase = imageManager.getIndexBase()

        self.xmax = imageManager.get_xmax() + 20
        self.ymax = imageManager.get_ymax() + 10
        self.currentPhotoList = imageManager.get_photoList()
        self.currentImageList = imageManager.get_imageList()

        # COLORS
        self.bgc = '#ffffff' # background
        self.btc = '#15CCF4' # buttons
        self.abtc = '#c6ffeb' # active button
        self.fgc = '#ffffff' # forground
        self.bth = 5 # button height
        self.currentPage = 0
        self.totalPages = self.get_totalPages()
        self.weights = []

        # main frame
        #self.mainframe = Frame(root, bg=self.bgc, width=1366,  height=768)
        #self.mainframe.pack()

        # section frames

        #############################
        ####### Query Frame #########
        #############################
        self.queryFrame = LabelFrame(self.root, 
                                     bg=self.bgc, 
                                     height=768,
                                     text="Query section")
        self.queryFrame.grid(row=0, column=0)

        # control panel (Buttons)
        self.dbQueryPanel = Frame(self.queryFrame, bg=self.bgc)
        self.dbQueryPanel.pack()

        # Database control
        self.lbl_dbQueryPanel = Label(self.dbQueryPanel, 
            text="Options: Requête et Bases de données",
            fg="black",
            width=50,
            height=2,
            font=('Arial',10,'bold'))
        self.lbl_dbQueryPanel.pack()

        self.var_choix = StringVar()
        self.canva_BDD = Canvas(self.dbQueryPanel)
        self.canva_BDD.pack(pady=2)
        self.rdio_ByImages = Radiobutton(self.canva_BDD, 
                                        text="Dossier d'images", 
                                        variable=self.var_choix,
                                        value="Dossier d'images : ", 
                                        width=25)

        self.rdio_ByCSVs = Radiobutton(self.canva_BDD, 
                                        text="Dossier CSVs", 
                                        variable=self.var_choix,
                                        value="Dossier CSVs : ",
                                        width=25)
        self.var_choix.set("Dossier d'images : ")
        self.rdio_ByImages.grid(row=0, column=0)
        self.rdio_ByCSVs.grid(row=0, column=1)
        
        ######## Folder selection
        self.folder_path = StringVar()
        self.canva_folder = Canvas(self.dbQueryPanel)
        self.canva_folder.pack()

        self.label_folder = Label(self.canva_folder, textvariable=self.var_choix)
        self.label_folder.grid(row=0, column=0)
        self.entryFolder = Entry(self.canva_folder, width=40, textvariable=self.folder_path)
        self.entryFolder.grid(row=0, column=1)
        self.btn_browse = Button(self.canva_folder, text="Browse", command=self.browse_button)
        self.btn_browse.grid(row=0, column=2)

        self.btn_indexer = Button(self.dbQueryPanel, 
                                 text="Indexer",
                                 font=('Arial',10,'bold'),
                                 width=10, 
                                 border=5, 
                                 bg=self.btc,
                                 fg=self.fgc, 
                                 activebackground=self.abtc,
                                 command=lambda: self.indexer())
        self.btn_indexer.pack()

        ######## Query image selection
        self.query_path = StringVar()
        self.canva_query = Canvas(self.dbQueryPanel)
        self.canva_query.pack()

        self.label_query = Label(self.canva_query, text="Image requête:")
        self.label_query.grid(row=0, column=0)
        self.entryQuery = Entry(self.canva_query, width=40, textvariable=self.query_path)
        self.entryQuery.grid(row=0, column=1)
        self.btn_browseQ = Button(self.canva_query, text="Browse", command=self.browse_buttonQ)
        self.btn_browseQ.grid(row=0, column=2)


        # selected image window
        self.selectedImage = Label(self.dbQueryPanel,
                                   width=320,
                                   height=200,
                                   bg=self.bgc)
        self.selectedImage.pack(pady=5)
        self.update_preview(self.imageList[0].filename)
        #___________________________________________________________________________#

        ########### Buttond
        self.canva_btns = Canvas(self.dbQueryPanel)
        self.canva_btns.pack()
        self.btn_search = Button(self.canva_btns, 
                                 text="Search",
                                 font=('Arial',10,'bold'),
                                 width=10, 
                                 pady=self.bth, 
                                 border=5, 
                                 bg=self.btc,
                                 fg=self.fgc, 
                                 activebackground=self.abtc,
                                 command=lambda: self.find())
        self.btn_search.grid(row=0, column=0)

        self.btn_reset = Button(self.canva_btns, 
                                text="Reset",
                                font=('Arial',10,'bold'),
                                width=10, 
                                pady=self.bth, 
                                border=5, 
                                bg="#CF1F1F",
                                fg=self.fgc, 
                                activebackground=self.abtc,
                                command=lambda: self.reset())
        self.btn_reset.grid(row=0, column=1)
        #___________________________________________________________________________#
    
        self.lbl_descriptrs = Label(self.dbQueryPanel, 
            text="Options: Choix de descripteur",
            fg="black",
            width=50,
            height=2,
            font=('Arial',10,'bold'))
        self.lbl_descriptrs.pack()

        ######## Descriptor selection
        self.var_desciptor = StringVar()
        optionList = ('Moments Statistiques', '      Histogramme     ', '           Moyenne         ')
        self.canva_desc = Canvas(self.dbQueryPanel)
        self.canva_desc.pack(pady=5)

        self.label_desc = Label(self.canva_desc, text="Choix du descripteur : ")
        self.label_desc.grid(row=0, column=0)
        self.var_desciptor.set(optionList[0])
        self.om = OptionMenu(self.canva_desc, self.var_desciptor, *optionList)
        self.om.grid(row=0, column=1)
        #___________________________________________________________________________#

        self.lbl_distances = Label(self.dbQueryPanel, 
            text="Options: Choix de la mesure de similarité",
            fg="black",
            width=50,
            height=2,
            font=('Arial',10,'bold'))
        self.lbl_distances.pack()

        ######## Distance selection
        self.var_distance = StringVar()
        optionListD = ('D. Euclidien', '      CHi square     ', '          Interesect        ')
        self.canva_dist = Canvas(self.dbQueryPanel)
        self.canva_dist.pack(pady= 5)

        self.label_dist = Label(self.canva_dist, text="Choix du distance : ")
        self.label_dist.grid(row=0, column=0)
        self.var_distance.set(optionListD[0])
        self.omd = OptionMenu(self.canva_dist, self.var_distance, *optionListD)
        self.omd.grid(row=0, column=1)

        #__________________________________________________________________________________

        self.lbl_search = Label(self.dbQueryPanel, 
            text="Options: Recherche M-tree",
            fg="black",
            width=50,
            height=2,
            font=('Arial',10,'bold'))
        self.lbl_search.pack()

        self.var_searchMethod = StringVar()
        self.var_searchMethod.set("Le nombre k : ")
        self.canva_SM = Canvas(self.dbQueryPanel)
        self.canva_SM.pack(pady=5)
        self.knn = Radiobutton(self.canva_SM, 
                                text="k-NN", 
                                variable=self.var_searchMethod,
                                value="Le nombre k : ",
                                width =25)
        self.rquery = Radiobutton(self.canva_SM, 
                                  text="Range query", 
                                  variable=self.var_searchMethod,
                                  value="Le rayon r : ",
                                  width =25)
        self.knn.grid(row=0, column=0)
        self.rquery.grid(row=0, column=1)

        self.KRange = IntVar()
        self.KRange.set(10)
        self.canva_KRange = Canvas(self.dbQueryPanel)
        self.canva_KRange.pack(pady=2)
        self.label_KRange = Label(self.canva_KRange, textvariable=self.var_searchMethod)
        self.label_KRange.grid(row=0, column=0)
        self.entryKRange = Spinbox(self.canva_KRange, width=4, from_ = 0, to = 100, textvariable=self.KRange)
        self.entryKRange.grid(row=0, column=1)


        # _______________________________________________________________________ #
        ##################################
        # results frame
        ##################################
        
        self.resultsViewFrame = LabelFrame(self.root, 
                                           bg=self.bgc, 
                                           text="Result section")
        self.resultsViewFrame.grid(row=0, column=1)

        instr = Label(self.resultsViewFrame,
                      bg=self.bgc, 
                      fg='#aaaaaa',
                      text="Click image to select. Checkboxes indicate relevance.")
        instr.pack(pady=10)

        self.resultPanel = LabelFrame(self.resultsViewFrame, bg=self.bgc)
        self.resultPanel.pack(pady=5, padx=5)
        self.canvas = Canvas(self.resultPanel ,
                             bg="white",
                             width=920,
                             height=550,
                             highlightthickness=2
                            )
        self.canvas.pack()

        # page navigation
        self.pageButtons = Frame(self.resultsViewFrame, bg=self.bgc)
        self.pageButtons.pack()

        self.btn_prev = Button(self.pageButtons, text="<< Previous page",
                               width=30, border=5, bg=self.btc,
                               fg=self.fgc, activebackground=self.abtc,
                               command=lambda: self.prevPage())
        self.btn_prev.pack(side=LEFT)

        self.pageLabel = Label(self.pageButtons,
                               text="Page 1 of " + str(self.totalPages),
                               width=43, bg=self.bgc, fg='#aaaaaa')
        self.pageLabel.pack(side=LEFT)

        self.btn_next = Button(self.pageButtons, text="Next page >>",
                               width=30, border=5, bg=self.btc,
                               fg=self.fgc, activebackground=self.abtc,
                               command=lambda: self.nextPage())
        self.btn_next.pack(side=RIGHT)

        

    
    def browse_button(self):
        # Allow user to select a directory and store it in global var
        # called folder_path
        filename = filedialog.askdirectory()
        self.folder_path.set(filename)

    def browse_buttonQ(self):
        # Allow user to select a file and store it in global var
        # called query_path
        filename = filedialog.askopenfilename()
        self.query_path.set(filename)
        self.update_preview(filename)

    def indexer(self):
        if self.folder_path.get() == "":
            print("empty")
        else:
            print(self.folder_path.get())
        
        DESC = Descriptor.getAvgs
        DIST = Distance.euclid

        if self.var_desciptor.get() == 'Moments Statistiques':
            DESC = Descriptor.getCMoments
        elif self.var_desciptor.get() == '      Histogramme     ':
            DESC = Descriptor.getHist
        elif self.var_desciptor.get() == '           Moyenne         ':
            DESC = Descriptor.getAvgs
        
        if self.var_desciptor.get() == 'D. Euclidien':
            DIST = Distance.euclid
        elif self.var_desciptor.get() == '      CHi square     ':
            DIST = Distance.chi
        elif self.var_desciptor.get() == '          Interesect        ':
            DIST = Distance.intersect
       
        self.imgManager = ImageManager(self.root, DESC, DIST, self.folder_path.get()+"/*.jpg")
        self.imageList = self.imgManager.get_imageList()
        self.photoList = self.imgManager.get_photoList()
        self.indexBase = self.imgManager.getIndexBase()

        self.xmax = self.imgManager.get_xmax() + 20
        self.ymax = self.imgManager.get_ymax() + 10
        self.currentPhotoList = self.imgManager.get_photoList()
        self.currentImageList = self.imgManager.get_imageList()
        self.totalPages = self.get_totalPages()

    def find(self):
        # TODO: use cv2
        #im = Image.open(self.selected.filename)
        #queryFeature = Descriptor.getHist(list(im.getdata()))

        im = cv2.imread(self.selected.filename)
        queryFeature = self.imgManager.descriptor(list(im))
        results = self.imgManager.executeImageSearch(queryFeature, self.KRange.get())
        self.currentImageList, self.currentPhotoList = [], []
        for img in results:
            if img != 'None':
                im = Image.open(img.replace("'", ""))
                # Resize the image for thumbnails.
                resized = im.resize((128, 128), Image.ADAPTIVE)
                photo = ImageTk.PhotoImage(resized)
                self.currentImageList.append(im)
                self.currentPhotoList.append(photo)

        iL = self.currentImageList[:24]
        pL = self.currentPhotoList[:24]
        self.currentPage = 0
        self.update_results((iL, pL))

   
    def reset(self):
        """
        Resets the GUI to its initial state
        """
        # initial display photos
        self.update_preview(self.imageList[0].filename)
        self.currentImageList = self.imageList
        self.currentPhotoList = self.photoList
        il = self.currentImageList[:24]
        pl = self.currentPhotoList[:24]
        self.update_results((il, pl))


    def get_pos(self, filename):
        """
        find selected image position
        :param filename:
        """
        pos = -1
        for i in range(len(self.imageList)):
            f = self.imageList[i].filename.replace("\\", "/")
            if filename == f:
                pos = i
        return pos


    def update_results(self, st):
        """
        Updates the photos in results window (used from sample)
        :param st: (image, photo)
        """
        
        txt = "Page "+str(self.currentPage + 1)+" of "+str(self.totalPages)
        self.pageLabel.configure(text=txt)
        cols = 6 # number of columns
        self.canvas.delete(ALL)


        #################################################
        self.canvas.config(width=920, height=550)
        self.canvas.pack()

        photoRemain = [] # photos to show
        for i in range(len(st[0])):
            f = st[0][i].filename
            img = st[1][i]
            photoRemain.append((f, img))

        rowPos = 0
        while photoRemain:
            photoRow = photoRemain[:cols]
            photoRemain = photoRemain[cols:]
            colPos = 0
            # Put a row
            for (filename, img) in photoRow:
                imagesFrame = Frame(self.canvas, bg=self.bgc, border=0)
                imagesFrame.pack(padx = 15)
                
                lbl = Label(imagesFrame,text=filename)
                lbl.pack()
                # Put image as a button
                handler = lambda f=filename: self.update_preview(f)
                btn_image = Button(imagesFrame,
                                   image=img,
                                   border=4,
                                   bg="white",
                                   width= 128,#self.imgManager.get_xmax()+20,
                                   activebackground=self.bgc
                                   )
                btn_image.config(command=handler)
                btn_image.pack(side=LEFT, padx=15)

                self.canvas.create_window(colPos,
                                          rowPos,
                                          anchor=NW,
                                          window=imagesFrame,
                                          width=self.xmax,
                                          height=self.ymax)
                colPos += self.xmax
            rowPos += self.ymax

    def update_preview(self, f):
        """
        Updates the selected images window. Image show!
        :param f: image identifier (the first image by default)
        """
        self.selected = Image.open(f.replace("\\", "/"))
        self.selectedPhoto = ImageTk.PhotoImage(self.selected)
        self.selectedImage.configure(image=self.selectedPhoto)

    # updates results page to previous page
    def prevPage(self):
        self.currentPage -= 1
        if self.currentPage < 0:
            self.currentPage = self.totalPages - 1
        start = self.currentPage * 24
        end = start + 24
        iL = self.currentImageList[start:end]
        pL = self.currentPhotoList[start:end]
        self.update_results((iL, pL))

    # updates results page to next page
    def nextPage(self):
        self.currentPage += 1
        if self.currentPage >= self.totalPages:
            self.currentPage = 0
        start = self.currentPage * 24
        end = start + 24
        iL = self.currentImageList[start:end]
        pL = self.currentPhotoList[start:end]
        self.update_results((iL, pL))

    # computes total pages in results
    def get_totalPages(self):
        pages = len(self.photoList) // 24
        if len(self.photoList) % 24 > 0:
            pages += 1
        return pages
