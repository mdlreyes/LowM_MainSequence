"""
NAME:
    create_ordered_AP_arrays

PURPOSE:
    This code cross-references all of the data in different
    fits files and orders the relevant data in the standard
    9264 order. Meant to be used as a module.

INPUTS:
    'Catalogs/nb_ia_zspec.txt'
    'Main_Sequence/Catalogs/MMT/MMTS_all_line_fit.fits'
    'Main_Sequence/Catalogs/MMT/MMT_single_line_fit.fits'
    'Main_Sequence/Catalogs/Keck/DEIMOS_single_line_fit.fits'
    'Main_Sequence/Catalogs/Keck/DEIMOS_00_all_line_fit.fits'
    'Main_Sequence/Catalogs/merged/MMT_Keck_line_fit.fits'

OUTPUTS:
    A dictionary with ordered AP, <instr>_LMIN0/LMAX0 arrays as values
"""

import numpy as np
from astropy.io import fits as pyfits, ascii as asc

def make_AP_arr_MMT(slit_str0):
    '''
    Creates an AP (aperture) array with the slit_str0 input from
    nb_ia_zspec.txt. At the indexes of the slit_str0 where there existed a
    type of AP ('N/A', 'S./A./D./1./2./3./4.###'), the indexes of the new
    AP array were replaced with those values with the remaining values
    renamed as 'not_MMT' before the array was returned.

    Takes care of N/A and MMT,
    '''
    AP = np.array(['x.xxx']*len(slit_str0))

    #N/A
    slit_NA_index = np.array([x for x in range(len(slit_str0))
                              if slit_str0[x] == 'N/A'])
    AP[slit_NA_index] = slit_str0[slit_NA_index]

    #MMT,
    slit_S_index  = np.array([x for x in range(len(slit_str0))
                              if 'S.' == slit_str0[x][:2] and
                              len(slit_str0[x])==6], dtype=np.int32)
    AP[slit_S_index] = slit_str0[slit_S_index]

    slit_A_index  = np.array([x for x in range(len(slit_str0))
                              if 'A.' == slit_str0[x][:2] and
                              len(slit_str0[x])==6], dtype=np.int32)
    AP[slit_A_index] = slit_str0[slit_A_index]
    
    slit_D_index  = np.array([x for x in range(len(slit_str0))
                              if 'D.' == slit_str0[x][:2] and
                              len(slit_str0[x])==6], dtype=np.int32)
    AP[slit_D_index] = slit_str0[slit_D_index]
    
    slit_1_index  = np.array([x for x in range(len(slit_str0))
                              if '1.' == slit_str0[x][:2] and
                              len(slit_str0[x])==6], dtype=np.int32)
    AP[slit_1_index] = slit_str0[slit_1_index]
    
    slit_2_index  = np.array([x for x in range(len(slit_str0))
                              if '2.' == slit_str0[x][:2] and
                              len(slit_str0[x])==6], dtype=np.int32)
    AP[slit_2_index] = slit_str0[slit_2_index]
    
    slit_3_index  = np.array([x for x in range(len(slit_str0))
                              if '3.' == slit_str0[x][:2] and
                              len(slit_str0[x])==6], dtype=np.int32)
    AP[slit_3_index] = slit_str0[slit_3_index]
    
    slit_4_index  = np.array([x for x in range(len(slit_str0))
                              if '4.' == slit_str0[x][:2] and
                              len(slit_str0[x])==6], dtype=np.int32)
    AP[slit_4_index] = slit_str0[slit_4_index]

    bad_index = np.array([x for x in range(len(AP)) if AP[x] == 'x.xxx'])
    APgood = np.array(AP, dtype='|S20')
    APgood[bad_index] = 'not_MMT'
    
    return APgood


def make_AP_arr_DEIMOS(AP, slit_str0):
    '''
    Accepts the AP array made by make_AP_arr_MMT and the slit_str0 array.
    Then, at the indices of slit_str0 where '##.###' exists (that's not a
    FOCAS detection), those indices of the AP array are replaced and then
    after modification is done, returned.

    Those with '08.' as a detection were ignored for now.

    Takes care of Keck, and Keck,Keck,
    '''

    #Keck,
    temp_index1 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x]) == 7 and 'f' not in slit_str0[x]
                            and '08.'!=slit_str0[x][:3]])
    AP[temp_index1] = slit_str0[temp_index1]
    AP[temp_index1] = np.array([x[:6] for x in AP[temp_index1]])

    temp_index2 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x]) == 7 and 'f' not in slit_str0[x]
                            and '08.'==slit_str0[x][:3]])
    AP[temp_index2] = 'INVALID_KECK'

    #Keck,Keck,
    temp_index3 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x])==14 and 'f' not in slit_str0[x]
                            and '08.'==slit_str0[x][7:10] and
                            '08.'==slit_str0[x][:3]])
    AP[temp_index3] = 'INVALID_KECK'

    temp_index4 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x])==14 and 'f' not in slit_str0[x]
                            and '08.'==slit_str0[x][:3] and
                            '08.'!=slit_str0[x][7:10]])
    AP[temp_index4] = slit_str0[temp_index4]
    AP[temp_index4] = np.array([x[7:13] for x in AP[temp_index4]])
    
    return AP


def make_AP_arr_merged(AP, slit_str0):
    '''
    Accepts the AP array made by make_AP_arr_DEIMOS and the slit_str0 array.
    Then, at the indices where there were multiple detections (not including
    a FOCAS detection), those indices were replaced and returned.

    Takes care of merged, and MMT,Keck, and merged,FOCAS,
    '''

    #merged,
    temp_index1 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x]) == 13 and slit_str0[x][5] == ','
                            and 'f' not in slit_str0[x] and
                            '08.'!= slit_str0[x][6:9]])
    AP[temp_index1] = slit_str0[temp_index1]
    AP[temp_index1] = np.array([x[:12] for x in AP[temp_index1]])

    #MMT,Keck, means MMT,
    temp_index2 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x]) == 13 and slit_str0[x][5] == ','
                            and 'f' not in slit_str0[x] and
                            '08.'== slit_str0[x][6:9]])
    AP[temp_index2] = slit_str0[temp_index2]
    AP[temp_index2] = np.array([x[:5] for x in AP[temp_index2]])

    #merged,FOCAS,
    temp_index3 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x]) > 13 and 'f'==slit_str0[x][13]
                            and '08.' not in slit_str0[x][:13]], dtype=np.int32)
    AP[temp_index3] = slit_str0[temp_index3]
    AP[temp_index3] = np.array([x[:12] for x in AP[temp_index3]])
    
    return AP


def make_AP_arr_FOCAS(AP, slit_str0):
    '''
    Accepts the AP array made by make_AP_arr_DEIMOS and the slit_str0 array.
    Same idea as the other make_AP_arr functions.

    Takes care of FOCAS, and FOCAS,FOCAS,FOCAS, and FOCAS,FOCAS, and
    MMT,FOCAS, and Keck,FOCAS, and Keck,Keck,FOCAS, and Keck,FOCAS,FOCAS,
    '''

    #FOCAS,
    temp_index1 = np.array([x for x in range(len(slit_str0)) if
                            'f'==slit_str0[x][0] and len(slit_str0[x])==7],
                           dtype=np.int32)
    AP[temp_index1] = 'FOCAS'

    #FOCAS,FOCAS,FOCAS,
    temp_index2 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x])==21 and 'f'==slit_str0[x][0] and
                            'f'==slit_str0[x][7] and 'f'==slit_str0[x][14]])
    AP[temp_index2] = 'FOCAS'

    #FOCAS,FOCAS,
    temp_index3 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x])==14 and 'f'==slit_str0[x][0] and
                            'f'==slit_str0[x][7]])
    AP[temp_index3] = 'FOCAS'

    #MMT,FOCAS,
    temp_index4 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x])==13 and 'f'==slit_str0[x][6]])
    AP[temp_index4] = slit_str0[temp_index4]
    AP[temp_index4] = np.array([x[:5] for x in AP[temp_index4]])

    #Keck,FOCAS,
    temp_index5 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x])==14 and 'f'==slit_str0[x][7] and
                            'f' not in slit_str0[x][:6]])
    AP[temp_index5] = slit_str0[temp_index5]
    AP[temp_index5] = np.array([x[:6] for x in AP[temp_index5]])

    #Keck,Keck,FOCAS,
    temp_index6 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x])==21 and 'f'==slit_str0[x][14] and
                            'f' not in slit_str0[x][:13] and
                            '08.'==slit_str0[x][:3]])
    AP[temp_index6] = slit_str0[temp_index6]
    AP[temp_index6] = np.array([x[7:13] for x in AP[temp_index6]])

    #Keck,FOCAS,FOCAS,
    temp_index7 = np.array([x for x in range(len(slit_str0)) if
                            len(slit_str0[x])==21 and 'f' not in
                            slit_str0[x][:6] and 'f'==slit_str0[x][7] and
                            'f'==slit_str0[x][14]])
    AP[temp_index7] = slit_str0[temp_index7]
    AP[temp_index7] = np.array([x[:6] for x in AP[temp_index7]])
    
    return AP


def get_LMIN0_LMAX0(all_AP, detect_AP, all_MMT_LMIN0, detect_MMT_LMIN0,
    all_MMT_LMAX0, detect_MMT_LMAX0, all_KECK_LMIN0, detect_KECK_LMIN0,
    all_KECK_LMAX0, detect_KECK_LMAX0):
    '''
    Accepts, modifies, and returns '<instr>_LMIN0/LMAX0' (passed in as 'all_<__>').
    'all_AP' is the complete AP column with all the information, while
    'detect_AP' and every input subsequent until the last four are the arrays
    specific to the Main_Sequence catalog.

    There are 5 different types of catalogs, so this method is called 5 times.

    This method looks at the indices where the detect_AP is in the all_AP and
    appends the overlapping indices of the all_AP array. Then, at those
    overlapping indices, the zero values in all_AP are replaced by the
    corresponding detected values.
    '''
    # indexes of data that correspond to indexes in 9264-AP-ordering
    index1 = np.array([x for x in range(len(detect_AP)) if detect_AP[x]
                       in all_AP], dtype=np.int32)

    # indexes of 9264-AP-ordering that correspond to indexes in data
    index2 = np.array([])
    for mm in range(len(detect_AP)):
        index2 = np.append(index2, np.where(all_AP == detect_AP[mm])[0])
    #endfor
    index2 = np.array(index2, dtype=np.int32)

    all_MMT_LMIN0[index2] = detect_MMT_LMIN0[index1]
    all_MMT_LMAX0[index2] = detect_MMT_LMAX0[index1]
    all_KECK_LMIN0[index2] = detect_KECK_LMIN0[index1]
    all_KECK_LMAX0[index2] = detect_KECK_LMAX0[index1]

    return all_MMT_LMIN0,all_MMT_LMAX0,all_KECK_LMIN0,all_KECK_LMAX0
#enddef


def get_LMIN0_LMAX0_merged(all_AP, mergedAP, all_MMT_LMIN0, all_MMT_LMAX0, all_KECK_LMIN0,
    all_KECK_LMAX0, MMTallAP, MMTallLMIN0, MMTallLMAX0, MMTsingleAP,
    MMTsingleLMIN0, MMTsingleLMAX0, DEIMOSAP, DEIMOSLMIN0, DEIMOSLMAX0,
    DEIMOS00AP, DEIMOS00LMIN0, DEIMOS00LMAX0):
    '''
    '''
    for ii in range(len(mergedAP)):
        bothap = mergedAP[ii]
        mmt = bothap.split(',')[0]
        keck = bothap.split(',')[1]

        # index in 9264-ordering corresponding to index in data
        jj = [x for x in range(len(all_AP)) if mmt==all_AP[x][:5]]

        # below: index in data corresponding to index in 9264-ordering
        # mmt part
        m1 = [x for x in range(len(MMTallAP)) if mmt==MMTallAP[x]]
        m2 = [x for x in range(len(MMTsingleAP)) if mmt==MMTsingleAP[x]]

        if len(m1) > 0:
            all_MMT_LMIN0[jj] = MMTallLMIN0[m1]
            all_MMT_LMAX0[jj] = MMTallLMAX0[m1]
        elif len(m2) > 0:
            all_MMT_LMIN0[jj] = MMTsingleLMIN0[m2]
            all_MMT_LMAX0[jj] = MMTsingleLMAX0[m2]

        # keck part
        k1 = [x for x in range(len(DEIMOSAP)) if keck==DEIMOSAP[x]]
        k2 = [x for x in range(len(DEIMOS00AP)) if keck==DEIMOS00AP[x]]
        if len(k1) > 0:
            all_KECK_LMIN0[jj] = DEIMOSLMIN0[k1]
            all_KECK_LMAX0[jj] = DEIMOSLMAX0[k1]
        elif len(k2) > 0:
            all_KECK_LMIN0[jj] = DEIMOS00LMIN0[k2]
            all_KECK_LMAX0[jj] = DEIMOS00LMAX0[k2]
    #endfor


    return all_MMT_LMIN0,all_MMT_LMAX0,all_KECK_LMIN0,all_KECK_LMAX0


def get_SNRs_FLUXs(all_AP, detect_AP, all_NIIASNR_FLUX, all_NIIBSNR_FLUX, detect_NIIASNR_FLUX, detect_NIIBSNR_FLUX,
    all_HASNR_FLUX, detect_HASNR_FLUX, all_HBSNR_FLUX, detect_HBSNR_FLUX,
    all_HGSNR_FLUX, detect_HGSNR_FLUX):
    '''
    Accepts, modifies, and returns '<line>_SNR' or '<line>_FLUX' (passed in as 'all_<__>').
    'all_AP' is the complete AP column with all the information, while
    'detect_AP' and every input subsequent until the last four are the arrays
    specific to the Main_Sequence catalog.

    There are 5 different types of catalogs, so this method is called 5 times.

    This method looks at the indices where the detect_AP is in the all_AP and
    appends the overlapping indices of the all_AP array. Then, at those
    overlapping indices, the zero values in all_AP are replaced by the
    corresponding detected values.
    '''
    # indexes of data that correspond to indexes in 9264-AP-ordering
    index1 = np.array([x for x in range(len(detect_AP)) if detect_AP[x]
                       in all_AP], dtype=np.int32)

    # indexes of 9264-AP-ordering that correspond to indexes in data
    index2 = np.array([])
    for mm in range(len(detect_AP)):
        index2 = np.append(index2, np.where(all_AP == detect_AP[mm])[0])
    #endfor
    index2 = np.array(index2, dtype=np.int32)

    all_NIIASNR_FLUX[index2] = detect_NIIASNR_FLUX[index1]
    all_NIIBSNR_FLUX[index2] = detect_NIIBSNR_FLUX[index1]
    all_HASNR_FLUX[index2] = detect_HASNR_FLUX[index1]
    all_HBSNR_FLUX[index2] = detect_HBSNR_FLUX[index1]
    all_HGSNR_FLUX[index2] = detect_HGSNR_FLUX[index1]

    return all_NIIASNR_FLUX,all_NIIBSNR_FLUX,all_HASNR_FLUX,all_HBSNR_FLUX,all_HGSNR_FLUX


def create_ordered_AP_arrays(AP_only=False):
    '''
    Reads relevant inputs, combining all of the input data into one ordered
    array for AP by calling make_AP_arr_MMT, make_AP_arr_DEIMOS,
    make_AP_arr_merged, and make_AP_arr_FOCAS. 

    Using the AP order, then creates '9264'-ordered arrays
    '''

    zspec = asc.read('/Users/kaitlynshin/GoogleDrive/NASA_Summer2015/Catalogs/nb_ia_zspec.txt',guess=False,
                     Reader=asc.CommentedHeader)
    slit_str0 = np.array(zspec['slit_str0'])
    inst_str0 = np.array(zspec['inst_str0'])

    MMTall = pyfits.open('/Users/kaitlynshin/GoogleDrive/NASA_Summer2015/Main_Sequence/Catalogs/MMT/MMTS_all_line_fit.fits')
    MMTalldata = MMTall[1].data
    MMTallAP = MMTalldata['AP']
    MMTallLMIN0 = MMTalldata['LMIN0']
    MMTallLMAX0 = MMTalldata['LMAX0']
    MMTallNIIASNR = MMTalldata['NIIA_SNR']
    MMTallNIIBSNR = MMTalldata['NIIB_SNR']
    MMTallHASNR = MMTalldata['HA_SNR']
    MMTallHBSNR = MMTalldata['HB_SNR']
    MMTallHGSNR = MMTalldata['HG_SNR']
    MMTallNIIAFLUX = MMTalldata['NIIA_FLUX_MOD']
    MMTallNIIBFLUX = MMTalldata['NIIB_FLUX_MOD']
    MMTallHAFLUX = MMTalldata['HA_FLUX_MOD']
    MMTallHBFLUX = MMTalldata['HB_FLUX_MOD']
    MMTallHGFLUX = MMTalldata['HG_FLUX_MOD']

    MMTsingle = pyfits.open('/Users/kaitlynshin/GoogleDrive/NASA_Summer2015/Main_Sequence/Catalogs/MMT/MMT_single_line_fit.fits')
    MMTsingledata = MMTsingle[1].data
    MMTsingleAP = MMTsingledata['AP']
    MMTsingleLMIN0 = MMTsingledata['LMIN0']
    MMTsingleLMAX0 = MMTsingledata['LMAX0']
    MMTsingleNIIASNR = MMTsingledata['NIIA_SNR']
    MMTsingleNIIBSNR = MMTsingledata['NIIB_SNR']
    MMTsingleHASNR = MMTsingledata['HA_SNR']
    MMTsingleHBSNR = MMTsingledata['HB_SNR']
    MMTsingleHGSNR = MMTsingledata['HG_SNR']
    MMTsingleNIIAFLUX = MMTsingledata['NIIA_FLUX_MOD']
    MMTsingleNIIBFLUX = MMTsingledata['NIIB_FLUX_MOD']
    MMTsingleHAFLUX = MMTsingledata['HA_FLUX_MOD']
    MMTsingleHBFLUX = MMTsingledata['HB_FLUX_MOD']
    MMTsingleHGFLUX = MMTsingledata['HG_FLUX_MOD']

    DEIMOS = pyfits.open('/Users/kaitlynshin/GoogleDrive/NASA_Summer2015/Main_Sequence/Catalogs/Keck/DEIMOS_single_line_fit.fits')
    DEIMOSdata = DEIMOS[1].data
    DEIMOSAP = DEIMOSdata['AP']
    DEIMOSLMIN0 = DEIMOSdata['LMIN0']
    DEIMOSLMAX0 = DEIMOSdata['LMAX0']
    DEIMOSNIIASNR = DEIMOSdata['NIIA_SNR']
    DEIMOSNIIBSNR = DEIMOSdata['NIIB_SNR']
    DEIMOSHASNR = DEIMOSdata['HA_SNR']
    DEIMOSHBSNR = DEIMOSdata['HB_SNR']
    DEIMOSHGSNR = DEIMOSdata['HG_SNR']
    DEIMOSNIIAFLUX = DEIMOSdata['NIIA_FLUX_MOD']
    DEIMOSNIIBFLUX = DEIMOSdata['NIIB_FLUX_MOD']
    DEIMOSHAFLUX = DEIMOSdata['HA_FLUX_MOD']
    DEIMOSHBFLUX = DEIMOSdata['HB_FLUX_MOD']
    DEIMOSHGFLUX = DEIMOSdata['HG_FLUX_MOD']

    DEIMOS00=pyfits.open('/Users/kaitlynshin/GoogleDrive/NASA_Summer2015/Main_Sequence/Catalogs/Keck/DEIMOS_00_all_line_fit.fits')
    DEIMOS00data = DEIMOS00[1].data
    DEIMOS00AP = DEIMOS00data['AP']
    DEIMOS00LMIN0 = DEIMOS00data['LMIN0']
    DEIMOS00LMAX0 = DEIMOS00data['LMAX0']
    DEIMOS00NIIASNR = DEIMOS00data['NIIA_SNR']
    DEIMOS00NIIBSNR = DEIMOS00data['NIIB_SNR']
    DEIMOS00HASNR = DEIMOS00data['HA_SNR']
    DEIMOS00HBSNR = DEIMOS00data['HB_SNR']
    DEIMOS00HGSNR = DEIMOS00data['HG_SNR']
    DEIMOS00NIIAFLUX = DEIMOS00data['NIIA_FLUX_MOD']
    DEIMOS00NIIBFLUX = DEIMOS00data['NIIB_FLUX_MOD']
    DEIMOS00HAFLUX = DEIMOS00data['HA_FLUX_MOD']
    DEIMOS00HBFLUX = DEIMOS00data['HB_FLUX_MOD']
    DEIMOS00HGFLUX = DEIMOS00data['HG_FLUX_MOD']

    merged = pyfits.open('/Users/kaitlynshin/GoogleDrive/NASA_Summer2015/Main_Sequence/Catalogs/merged/MMT_Keck_line_fit.fits')
    mergeddata = merged[1].data
    mergedAP = mergeddata['AP']
    mergedLMIN0_MMT = mergeddata['MMT_LMIN0']
    mergedLMAX0_MMT = mergeddata['MMT_LMAX0']
    mergedLMIN0_KECK = mergeddata['KECK_LMIN0']
    mergedLMAX0_KECK = mergeddata['KECK_LMAX0']
    mergedNIIASNR = mergeddata['NIIA_SNR']
    mergedNIIBSNR = mergeddata['NIIB_SNR']
    mergedHASNR = mergeddata['HA_SNR']
    mergedHBSNR = mergeddata['HB_SNR']
    mergedHGSNR = mergeddata['HG_SNR']
    mergedNIIAFLUX = mergeddata['NIIA_FLUX_MOD']
    mergedNIIBFLUX = mergeddata['NIIB_FLUX_MOD']
    mergedHAFLUX = mergeddata['HA_FLUX_MOD']
    mergedHBFLUX = mergeddata['HB_FLUX_MOD']
    mergedHGFLUX = mergeddata['HG_FLUX_MOD']

    #end inputs
    print '### done reading input files'

    print '### creating ordered AP arr'
    AP0 = make_AP_arr_MMT(slit_str0)
    AP1 = make_AP_arr_DEIMOS(AP0, slit_str0)
    AP2 = make_AP_arr_merged(AP1, slit_str0)
    AP  = make_AP_arr_FOCAS(AP2, slit_str0)
    print '### done creating ordered AP arr'

    merged_iis = np.array([x for x in range(len(inst_str0)) if 'merged' in inst_str0[x]])
    AP_merged = AP[merged_iis]

    if (AP_only == True):
        MMTall.close()
        MMTsingle.close()
        DEIMOS.close()
        DEIMOS00.close()
        merged.close()

        return {'AP': AP}
    #endif 

    print '### creating ordered LMIN0/LMAX0 arrs'
    MMT_LMIN0 = np.array([-99.99999]*len(AP))
    MMT_LMAX0 = np.array([-99.99999]*len(AP))
    KECK_LMIN0 = np.array([-99.99999]*len(AP))
    KECK_LMAX0 = np.array([-99.99999]*len(AP))
    MMT_LMIN0, MMT_LMAX0, KECK_LMIN0, KECK_LMAX0 = get_LMIN0_LMAX0(AP, MMTallAP, MMT_LMIN0, MMTallLMIN0, 
        MMT_LMAX0, MMTallLMAX0, KECK_LMIN0, MMTallLMIN0, KECK_LMAX0, MMTallLMAX0)
    MMT_LMIN0, MMT_LMAX0, KECK_LMIN0, KECK_LMAX0 = get_LMIN0_LMAX0(AP, MMTsingleAP, MMT_LMIN0, MMTsingleLMIN0, 
        MMT_LMAX0, MMTsingleLMAX0, KECK_LMIN0, MMTsingleLMIN0, KECK_LMAX0, MMTsingleLMAX0)
    MMT_LMIN0, MMT_LMAX0, KECK_LMIN0, KECK_LMAX0 = get_LMIN0_LMAX0(AP, DEIMOSAP, MMT_LMIN0, DEIMOSLMIN0, 
        MMT_LMAX0, DEIMOSLMAX0, KECK_LMIN0, DEIMOSLMIN0, KECK_LMAX0, DEIMOSLMAX0)
    MMT_LMIN0, MMT_LMAX0, KECK_LMIN0, KECK_LMAX0 = get_LMIN0_LMAX0(AP, DEIMOS00AP, MMT_LMIN0, DEIMOS00LMIN0, 
        MMT_LMAX0, DEIMOS00LMAX0, KECK_LMIN0, DEIMOS00LMIN0, KECK_LMAX0, DEIMOS00LMAX0)
    MMT_LMIN0, MMT_LMAX0, KECK_LMIN0, KECK_LMAX0 = get_LMIN0_LMAX0_merged(AP, AP_merged, 
        MMT_LMIN0, MMT_LMAX0, KECK_LMIN0, KECK_LMAX0, MMTallAP, MMTallLMIN0, MMTallLMAX0, 
        MMTsingleAP, MMTsingleLMIN0, MMTsingleLMAX0, DEIMOSAP, DEIMOSLMIN0, DEIMOSLMAX0, 
        DEIMOS00AP, DEIMOS00LMIN0, DEIMOS00LMAX0)
    print '### done creating ordered LMIN0/LMAX0 arr'

    print '### creating ordered SNR arrs'
    NIIA_SNR = np.array([-99.99999]*len(AP))
    NIIB_SNR = np.array([-99.99999]*len(AP))
    HA_SNR = np.array([-99.99999]*len(AP))
    HB_SNR = np.array([-99.99999]*len(AP))
    HG_SNR = np.array([-99.99999]*len(AP))
    NIIA_SNR, NIIB_SNR, HA_SNR, HB_SNR, HG_SNR = get_SNRs_FLUXs(AP, MMTallAP, NIIA_SNR, NIIB_SNR, MMTallNIIASNR, MMTallNIIBSNR, 
        HA_SNR, MMTallHASNR, HB_SNR, MMTallHBSNR, HG_SNR, MMTallHGSNR)
    NIIA_SNR, NIIB_SNR, HA_SNR, HB_SNR, HG_SNR = get_SNRs_FLUXs(AP, MMTsingleAP, NIIA_SNR, NIIB_SNR, MMTsingleNIIASNR, MMTsingleNIIBSNR, 
        HA_SNR, MMTsingleHASNR, HB_SNR, MMTsingleHBSNR, HG_SNR, MMTsingleHGSNR)
    NIIA_SNR, NIIB_SNR, HA_SNR, HB_SNR, HG_SNR = get_SNRs_FLUXs(AP, DEIMOSAP, NIIA_SNR, NIIB_SNR, DEIMOSNIIASNR, DEIMOSNIIBSNR, 
        HA_SNR, DEIMOSHASNR, HB_SNR, DEIMOSHBSNR, HG_SNR, DEIMOSHGSNR)
    NIIA_SNR, NIIB_SNR, HA_SNR, HB_SNR, HG_SNR = get_SNRs_FLUXs(AP, DEIMOS00AP, NIIA_SNR, NIIB_SNR, DEIMOS00NIIASNR, DEIMOS00NIIBSNR, 
        HA_SNR, DEIMOS00HASNR, HB_SNR, DEIMOS00HBSNR, HG_SNR, DEIMOS00HGSNR)
    NIIA_SNR, NIIB_SNR, HA_SNR, HB_SNR, HG_SNR = get_SNRs_FLUXs(AP, mergedAP, NIIA_SNR, NIIB_SNR, mergedNIIASNR, mergedNIIBSNR, 
        HA_SNR, mergedHASNR, HB_SNR, mergedHBSNR, HG_SNR, mergedHGSNR)
    print '### done creating ordered SNR arrs'

    print '### creating ordered FLUX arrs'
    NIIA_FLUX = np.array([-99.99999]*len(AP))
    NIIB_FLUX = np.array([-99.99999]*len(AP))
    HA_FLUX = np.array([-99.99999]*len(AP))
    HB_FLUX = np.array([-99.99999]*len(AP))
    HG_FLUX = np.array([-99.99999]*len(AP))
    NIIA_FLUX, NIIB_FLUX, HA_FLUX, HB_FLUX, HG_FLUX = get_SNRs_FLUXs(AP, MMTallAP, NIIA_FLUX, NIIB_FLUX, MMTallNIIAFLUX, MMTallNIIBFLUX, 
        HA_FLUX, MMTallHAFLUX, HB_FLUX, MMTallHBFLUX, HG_FLUX, MMTallHGFLUX)
    NIIA_FLUX, NIIB_FLUX, HA_FLUX, HB_FLUX, HG_FLUX = get_SNRs_FLUXs(AP, MMTsingleAP, NIIA_FLUX, NIIB_FLUX, MMTsingleNIIAFLUX, MMTsingleNIIBFLUX, 
        HA_FLUX, MMTsingleHAFLUX, HB_FLUX, MMTsingleHBFLUX, HG_FLUX, MMTsingleHGFLUX)
    NIIA_FLUX, NIIB_FLUX, HA_FLUX, HB_FLUX, HG_FLUX = get_SNRs_FLUXs(AP, DEIMOSAP, NIIA_FLUX, NIIB_FLUX, DEIMOSNIIAFLUX, DEIMOSNIIBFLUX, 
        HA_FLUX, DEIMOSHAFLUX, HB_FLUX, DEIMOSHBFLUX, HG_FLUX, DEIMOSHGFLUX)
    NIIA_FLUX, NIIB_FLUX, HA_FLUX, HB_FLUX, HG_FLUX = get_SNRs_FLUXs(AP, DEIMOS00AP, NIIA_FLUX, NIIB_FLUX, DEIMOS00NIIAFLUX, DEIMOS00NIIBFLUX, 
        HA_FLUX, DEIMOS00HAFLUX, HB_FLUX, DEIMOS00HBFLUX, HG_FLUX, DEIMOS00HGFLUX)
    NIIA_FLUX, NIIB_FLUX, HA_FLUX, HB_FLUX, HG_FLUX = get_SNRs_FLUXs(AP, mergedAP, NIIA_FLUX, NIIB_FLUX, mergedNIIAFLUX, mergedNIIBFLUX, 
        HA_FLUX, mergedHAFLUX, HB_FLUX, mergedHBFLUX, HG_FLUX, mergedHGFLUX)
    print '### done creating ordered FLUX arrs'

    MMTall.close()
    MMTsingle.close()
    DEIMOS.close()
    DEIMOS00.close()
    merged.close()

    return ({'AP': AP, 'MMT_LMIN0': MMT_LMIN0, 'MMT_LMAX0': MMT_LMAX0, 
        'KECK_LMIN0': KECK_LMIN0, 'KECK_LMAX0': KECK_LMAX0, 
        'NIIA_SNR': NIIA_SNR, 'NIIB_SNR': NIIB_SNR, 'HA_SNR': HA_SNR, 'HB_SNR': HB_SNR, 'HG_SNR': HG_SNR,
        'NIIA_FLUX': NIIA_FLUX, 'NIIB_FLUX': NIIB_FLUX, 'HA_FLUX': HA_FLUX, 'HB_FLUX': HB_FLUX, 'HG_FLUX': HG_FLUX})


def main():
    AP_dict = create_ordered_AP_arrays()


if __name__ == '__main__':
    main()