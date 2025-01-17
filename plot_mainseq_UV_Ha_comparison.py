"""
NAME:
    plot_mainseq_UV_Ha_comparison.py

PURPOSE:
    This code plots a comparison between Halpha and UV luminosities (the
    latter of which is 'nu_L_nu'). Then, the ratio of the two is plotted as a
    function of stellar mass.
    With the GALEX command line option, if GALEX is typed, then GALEX files
    files used/output. Otherwise, the files without GALEX photometry are used.

INPUTS:
    'Catalogs/nb_ia_zspec.txt'
    'FAST/outputs/NB_IA_emitters_allphot.emagcorr.ACpsf_fast'+fileend+'.fout'
    'Catalogs/NB_IA_emitters.nodup.colorrev.fix.fits'
    'Main_Sequence/mainseq_corrections_tbl.txt'
    'FAST/outputs/BEST_FITS/NB_IA_emitters_allphot.emagcorr.ACpsf_fast'
         +fileend+'_'+str(ID[ii])+'.fit'

CALLING SEQUENCE:
    main body -> get_nu_lnu -> get_flux
              -> make_scatter_plot, make_ratio_plot
              -> make_all_ratio_plot -> (make_all_ratio_legend,
                                         get_binned_stats)

OUTPUTS:
    'Plots/main_sequence_UV_Ha/'+ff+'_'+ltype+fileend+'.pdf'
    'Plots/main_sequence_UV_Ha/ratios/'+ff+'_'+ltype+fileend+'.pdf'
    'Plots/main_sequence_UV_Ha/ratios/all_filt_'+ltype+fileend+'.pdf'
    
REVISION HISTORY:
    Created by Kaitlyn Shin 13 August 2015
"""

import numpy as np, astropy.units as u, matplotlib.pyplot as plt, sys
from scipy import interpolate
from astropy import constants
from astropy.io import fits as pyfits, ascii as asc
from astropy.cosmology import FlatLambdaCDM
cosmo = FlatLambdaCDM(H0 = 70 * u.km / u.s / u.Mpc, Om0=0.3)

# emission line wavelengths (air)
HA = 6562.80

FULL_PATH = '/Users/kaitlynshin/GoogleDrive/NASA_Summer2015/'


def get_flux(ID, lambda_arr):
    '''
    Reads in the relevant SED spectrum file and then interpolates the
    function to obtain a flux, the array of which is then returned.
    '''
    newflux = np.zeros(len(ID))
    for ii in range(len(ID)):
        tempfile = asc.read(FULL_PATH+
            'FAST/outputs/BEST_FITS/NB_IA_emitters_allphot.emagcorr.ACpsf_fast'+
            fileend+'_'+str(ID[ii])+'.fit', guess=False,Reader=asc.NoHeader)
        wavelength = np.array(tempfile['col1'])
        flux = np.array(tempfile['col2'])
        f = interpolate.interp1d(wavelength, flux)
        newflux[ii] = f(lambda_arr[ii])

    return newflux


def get_lnu(filt_index_haii, ff):
    '''
    Calls get_flux with an array of redshifted wavelengths in order to get
    the corresponding flux values. Those f_lambda values are then converted
    into f_nu values, which is in turn converted into L_nu, the log of which
    is returned as nu_lnu.
    '''
    ID = corrID[filt_index_haii]
    zspec = corrzspec0[filt_index_haii]

    goodz = np.where((zspec >= 0) & (zspec < 9))[0]
    badz  = np.where((zspec <= 0) | (zspec > 9))[0]

    tempz = np.zeros(len(filt_index_haii))
    tempz[goodz] = zspec[goodz]
    tempz[badz] = centr_filts[ff]

    lambda_arr = (1+tempz)*1500

    f_lambda = get_flux(ID, lambda_arr)
    f_nu = f_lambda*(1E-19*(lambda_arr**2*1E-10)/(constants.c.value))
    # L_nu = f_nu*4*np.pi*(cosmo.luminosity_distance(tempz).to(u.cm).value)**2
    # return np.log10(L_nu*((constants.c.value)/1.5E-7)) # getting nu from 1500AA
    log_L_nu = np.log10(f_nu*4*np.pi) + \
        2*np.log10(cosmo.luminosity_distance(tempz).to(u.cm).value)
    return log_L_nu


def get_nu_lnu(filt_index_haii, ff):
    '''
    Calls get_lnu to get log(L_nu) and multiplied by log(nu), which is
    then returned as log(nu_lnu)
    '''
    log_L_nu = get_lnu(filt_index_haii, ff)
    return (np.log10(constants.c.value) - np.log10((1500*u.AA).to(u.m).value)) \
        + log_L_nu


def make_scatter_plot(nu_lnu, l_ha, ff, ltype):
    '''
    Makes a scatter plot (by filter) of nu_lnu vs l_ha, then saves and
    closes the figure.

    There is a value in the filter NB921 which has flux=='NAN'. That is
    ignored.
    '''
    plt.scatter(nu_lnu, l_ha, color='b', edgecolor='k', s=12)
    plt.gca().minorticks_on()
    plt.gca().tick_params(axis='both', which='both', direction='in')
    plt.xlabel('log['+r'$\nu$'+'L'+r'$_{\nu}$'+'(1500 '+r'$\AA$'+')]')
    plt.ylabel('log[L'+r'$_{H\alpha}$'+']')    
    plt.xlim(36.0, 48.0)
    plt.ylim(37.0, 44.0)
    plt.savefig(FULL_PATH+'Plots/main_sequence_UV_Ha/'+ff+'_'+ltype+
        fileend+'.pdf')
    plt.close()


def make_ratio_plot(nu_lnu, l_ha, stlr, ff, ltype):
    '''
    Makes a ratio plot (by filter) of stellar mass vs. (nu_lnu/l_ha), then
    saves and closes the figure.

    There is a value in the filter NB921 which has flux=='NAN'. That is
    ignored.
    '''
    ratio = nu_lnu-l_ha
    plt.scatter(stlr, ratio, s=12)
    plt.gca().minorticks_on()
    plt.gca().tick_params(axis='both', which='both', direction='in')
    plt.xlabel('log[M/M'+r'$_{\odot}$'+']')
    plt.ylabel('log['+r'$\nu$'+'L'+r'$_{\nu}$'+'/L(H'+r'$\alpha$'+')'+']')
    plt.savefig(FULL_PATH+'Plots/main_sequence_UV_Ha/ratios/'+ff+'_'+ltype+
        fileend+'.pdf')
    plt.close()


def make_all_ratio_legend(filtlabel):
    '''
    Makes a legend for the plot with all ratios (as a function of mass) of
    all the filters on the same plot.

    red='NB704', orange='NB711', green='NB816', blue='NB921', purple='NB973'
    '''
    import matplotlib.patches as mpatches

    red_patch = mpatches.Patch(color='red', label='H'+r'$\alpha$'+'-NB7 '
                               +filtlabel['NB7'], alpha=0.5)
    orange_patch = mpatches.Patch(color='orange', label='H'+r'$\alpha$'+'-NB816 '
                                 +filtlabel['NB816'], alpha=0.5)
    green_patch = mpatches.Patch(color='green', label='H'+r'$\alpha$'+'-NB921 '
                                +filtlabel['NB921'], alpha=0.5)
    blue_patch = mpatches.Patch(color='blue', label='H'+r'$\alpha$'
                                  +'-NB973 '+filtlabel['NB973'], alpha=0.5)

    legend0 = plt.legend(handles=[red_patch,orange_patch,green_patch,
                                  blue_patch],fontsize=9,
                         loc='lower right', frameon=False)
    plt.gca().add_artist(legend0)


def get_binned_stats(xposdata, yposdata):
    '''
    From the min to the max x-values of the graph, 'bins' of interval 0.25
    are created. If there are more than 3 x values in a particular bin, the
    average of the corresponding y values are plotted, and their std dev
    values are plotted as error bars as well.

    In order to clearly stand out from the rainbow scatter plot points, these
    'binned' points are black.
    '''
    bins = np.arange(min(plt.xlim()), max(plt.xlim())+0.25, 0.25)
    for bb in range(len(bins)-1):
        valid_index = np.array([x for x in range(len(xposdata)) if
                                xposdata[x] >= bins[bb] and xposdata[x] <
                                bins[bb+1]])
        if len(valid_index) > 3:
            xpos = np.mean((bins[bb], bins[bb+1]))
            ypos = np.mean(yposdata[valid_index])
            yerr = np.std(yposdata[valid_index])
            plt.scatter(xpos, ypos, facecolor='k', edgecolor='none', alpha=0.7)
            plt.errorbar(xpos, ypos, yerr=yerr, ecolor='k', alpha=0.7,
                         fmt='none')


def make_all_ratio_plot(L_ha, ltype, xarr_type='stlr'):
    '''
    Similar as make_ratio_plot, except each filter is plotted on the graph,
    and sources with good zspec are filled points while those w/o good zspec
    are plotted as empty points. get_binned_stats and make_all_ratio_legend
    are called, before the plot is duly modified, saved, and closed.
    '''
    print ltype, '('+xarr_type+')'
    xposdata = np.array([])
    yposdata = np.array([])
    filtlabel = {}
    for (ff, cc) in zip(['NB7','NB816','NB921','NB973'], color_arr):
        print ff

        if ff == 'NB816': # GALEX file ID#4411 has flux==0
            filt_index_haii = np.array([x for x in range(len(corr_tbl)) if ff in
                corrfilts[x] and corrNAME0[x] != 'Ha-NB816_172306_OII-NB921_176686'])
        else:
            filt_index_haii = np.array([x for x in range(len(corr_tbl)) if ff in
                corrfilts[x]])
        l_ha = L_ha[filt_index_haii]

        zspec = corrzspec0[filt_index_haii]
        if xarr_type=='stlr':
            xpos_arr = corrstlr0[filt_index_haii]
        elif xarr_type=='sfr':
            xpos_arr = corr_sfr[filt_index_haii]
        else:
            raise ValueError('Incorrect xarr_type provided (must be either \'stlr\' or \'sfr\'')

        nu_lnu = get_nu_lnu(filt_index_haii, ff)
        lmbda = (1500*u.AA).to(u.um).value
        K_1500 = (2.659*(-2.156 + 1.509/lmbda - 0.198/lmbda**2 + 0.011/lmbda**3)+ 4.05)
        A_1500 = K_1500 * corr_tbl['EBV'].data[filt_index_haii]
        nu_lnu += 0.4*A_1500 # (dust correction: A_V = A(1500AA) = 10.33)
 
        ratio = nu_lnu-l_ha
        xposdata = np.append(xposdata, xpos_arr)
        yposdata = np.append(yposdata, ratio)

        good_z = np.array([x for x in range(len(zspec)) if zspec[x] > 0. and
                           zspec[x] < 9.])
        bad_z  = np.array([x for x in range(len(zspec)) if zspec[x] <= 0. or
                           zspec[x] >= 9.])
        filtlabel[ff] = '('+str(len(good_z))+', '+str(len(bad_z))+')'

        plt.scatter(xpos_arr[good_z], ratio[good_z], facecolor=cc, edgecolor='none',
                    alpha=0.5, s=12)
        plt.scatter(xpos_arr[bad_z], ratio[bad_z], facecolor='none', edgecolor=cc,
                    linewidth=0.5, alpha=0.5, s=12)


    get_binned_stats(xposdata, yposdata)
    plt.gca().minorticks_on()
    plt.gca().tick_params(axis='both', which='both', direction='in')
    plt.ylabel('log['+r'$\nu$'+'L'+r'$_{\nu}$'+'(1500 '+r'$\AA$'+')/L'
               +r'$_{H\alpha}$'+']')
    make_all_ratio_legend(filtlabel)
    plt.plot(plt.xlim(), [2.05, 2.05], 'k--', alpha=0.3, linewidth=3.0)
    if xarr_type=='stlr':
        plt.xlim(4, 11)
        plt.ylim(-2.5, 4)
        plt.xlabel('log[M/M'+r'$_{\odot}$'+']')
        plt.savefig(FULL_PATH+'Plots/main_sequence_UV_Ha/ratios/all_filt_'+ltype+
                    fileend+'.pdf')
    elif xarr_type=='sfr':
        plt.xlabel('log(SFR[H'+r'$\alpha$'+']/M'+r'$_{\odot}$'+' yr'+r'$^{-1}$'+')')
        plt.savefig(FULL_PATH+'Plots/main_sequence_UV_Ha/ratios/all_filt_'+ltype+
                    '_with_SFRs'+fileend+'.pdf')
    plt.close()


#----main body---------------------------------------------------------------#
# o Reads relevant inputs
# o Iterating by filter, calls nu_lnu, make_scatter_plot, and
#   make_ratio_plot
# o After the filter iteration, make_all_ratio_plot is called.
# o For each of the functions to make a plot, they're called twice - once for
#   plotting the nii/ha corrected version, and one for plotting the dust
#   corrected version.
#----------------------------------------------------------------------------#
# +190531: only GALEX files will be used
fileend='.GALEX'

zspec = asc.read(FULL_PATH+'Catalogs/nb_ia_zspec.txt',guess=False,
    Reader=asc.CommentedHeader)
zspec0 = np.array(zspec['zspec0'])

fout  = asc.read(FULL_PATH+'FAST/outputs/NB_IA_emitters_allphot.emagcorr.ACpsf_fast'+fileend+'.fout',guess=False,Reader=asc.NoHeader)
zphot0 = np.array(fout['col2'])  # IDK
stlr0 = np.array(fout['col7']) # stlr mass

nbia = pyfits.open(FULL_PATH+'Catalogs/NB_IA_emitters.nodup.colorrev.fix.fits')
nbiadata = nbia[1].data
NAME0 = np.array(nbiadata['NAME'])
ID0   = np.array(nbiadata['ID'])

corr_tbl = asc.read(FULL_PATH+'Main_Sequence/mainseq_corrections_tbl.txt',
    guess=False, Reader=asc.FixedWidthTwoLine)
corrID = np.array(corr_tbl['ID'])
corrNAME0 = np.array(corr_tbl['NAME0'])
corrzspec0 = np.array(corr_tbl['zspec0'])
corrfilts = np.array(corr_tbl['filt'])
corrstlr0 = np.array(corr_tbl['stlr_mass'])
obs_lumin = np.array(corr_tbl['obs_lumin'])
sfr = np.array(corr_tbl['met_dep_sfr'])
dust_corr_factor = np.array(corr_tbl['dust_corr_factor'])
filt_corr_factor = np.array(corr_tbl['filt_corr_factor'])
nii_ha_corr_factor = np.array(corr_tbl['nii_ha_corr_factor'])
corr_factors = filt_corr_factor + nii_ha_corr_factor + dust_corr_factor

corr_fluxes = corr_tbl['obs_fluxes'].data + corr_factors
corr_lumin = obs_lumin + corr_factors
corr_sfr = sfr + corr_factors
print '### done reading input files'

ID_match = np.array([x for x in range(len(ID0)) if ID0[x] in corrID])
color_arr = ['r', 'orange', 'g', 'b']
centr_filts = {'NB7':((7045.0/HA - 1) + (7126.0/HA - 1))/2.0, 
               'NB816':8152.0/HA - 1, 'NB921':9193.0/HA - 1, 'NB973':9749.0/HA - 1}

print '### making scatter_plots and ratio_plots'
for (ff, cc) in zip(['NB7','NB816','NB921','NB973'], color_arr):
    print ff
    
    if ff == 'NB816': # GALEX file ID#4411 has flux==0
        filt_index_haii = np.array([x for x in range(len(corr_tbl)) if ff in
            corrfilts[x] and corrNAME0[x] != 'Ha-NB816_172306_OII-NB921_176686'])
    else:
        filt_index_haii = np.array([x for x in range(len(corr_tbl)) if ff in
            corrfilts[x]])

    nu_lnu = get_nu_lnu(filt_index_haii, ff)
    
    make_scatter_plot(nu_lnu, corr_lumin[filt_index_haii], ff, 'all_corr')

    make_ratio_plot(nu_lnu, corr_lumin[filt_index_haii], corrstlr0[filt_index_haii],
        ff, 'all_corr')


print '### making all_ratio_plots'
make_all_ratio_plot(corr_lumin, 'all_corr')
make_all_ratio_plot(corr_lumin, 'all_corr', xarr_type='sfr')