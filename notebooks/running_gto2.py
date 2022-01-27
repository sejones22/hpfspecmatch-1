#!/usr/bin/env python
# coding: utf-8

# In[67]:


from importlib import reload
import os
import glob2
import pandas as pd
import numpy as np
import sys


# In[68]:


import hpfspec
import hpfspecmatch


# In[69]:


# List of fitsfiles
LIBRARY_DIR = '../library/20201008_specmatch_nir/'
library_fitsfiles = glob2.glob(LIBRARY_DIR+'FITS/*/*.fits')


# In[70]:


# Read in all files as a HPFSpecList object
HLS = hpfspec.HPFSpecList(filelist=library_fitsfiles)


# In[71]:


# Read in required information on all of the 
# This has the Teff, Fe/H, and logg for all of the stars
# OBJECT_ID is the HPF name of the star
df_lib = pd.read_csv(LIBRARY_DIR+'20201008_specmatch_nir.csv')


# In[72]:


def specmatch(inputfile, inputobjectsimbad, outputdirectory):
    # Target data
    targetfilename = inputfile
    Htarget = hpfspec.HPFSpectrum(targetfilename,targetname=inputobjectsimbad)

    # Which orders are good in HPF ?
    orders = list(hpfspecmatch.BOUNDS.keys())
    
    # Reference data
    Hrefs   = HLS.splist
    # Run spectral matching algorithm for first two orders
    # in principle we should run all orders, just first two as an example
    for o in orders:
        print("########################")
        print("Order {}".format(o))
        print("########################")
        wmin = hpfspecmatch.BOUNDS[o][0] # Lower wavelength bound in A
        wmax = hpfspecmatch.BOUNDS[o][1] # Upper wavelength bound in A
        ww = np.arange(wmin,wmax,0.01)   # Wavelength array to resample to
        v = np.linspace(-125,125,1501)   # Velocities in km/s to use for absolute RV consideration
        savefolder = '../output/{}/{}_{}/'.format(outputdirectory,Htarget.object,o) # foldername to save

        #############################################################
        # Run first Spectral Matching Step: Loop through the full library to find which ones are best
        #############################################################
        df_chi, df_chi_best, Hbest = hpfspecmatch.chi2spectraPolyLoop(ww,            # Wavelength to resample to
                                                                      Htarget,       # Target class
                                                                      HLS.splist,    # Target library spectra
                                                                      plot_all=False,# if True, will create a lot more plots 
                                                                      verbose=True,  # if verbose
                                                                      vsini=True)    # recommend always having on

        #############################################################
        # Run the Second step: creating the composite spectrum
        #############################################################
        t,f,l,vis,te,fe,le,df_chi,LCS = hpfspecmatch.run_specmatch(Htarget,   # Target class
                                                                   HLS.splist,# Library spectra
                                                                   ww,        # Wavelength to resample to
                                                                   v,         # velocity range to use for absolute rv
                                                                   df_lib,    # dataframe with info on Teff/FeH/logg for the library stars
                                                                   savefolder=savefolder)


# In[76]:


gto_files = pd.read_csv('../input/20201020_hpf_gto_targets/20201020_hpf_gto_specmatch_filenames_sncut600.csv')
targets = gto_files['filename'].values
#targets[:55]#47
#targets[55:101]#46
#targets[101:]#46
for i,x in enumerate(targets[71:101]):
    if x is not np.nan:
        inputfile = '../input/20201020_hpf_gto_targets/{}'.format(os.path.basename(x))
        inputobjectsimbad = gto_files['name'][i+71]
        outputdirectory = '20201020_hpf_gto_targets/{}'.format(inputobjectsimbad)
        specmatch(inputfile, inputobjectsimbad, outputdirectory)

