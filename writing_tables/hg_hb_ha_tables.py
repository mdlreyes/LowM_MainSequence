"""
NAME:
    hg_hb_ha_tables.py

PURPOSE:
    Provides a module where table-writing functions can be called from 
    stack_spectral_data.py for Hg/Hb/Ha (MMT) plots
"""

def table_arr_appends(num, table_arrays, label, subtitle, flux, flux2, flux3, ew, ew_emission, ew_absorption, ew_check, median, pos_amplitude, neg_amplitude):
    (tablenames, tablefluxes, nii6548fluxes, nii6583fluxes, ewlist, 
        ewposlist , ewneglist, ewchecklist, medianlist, pos_amplitudelist, 
        neg_amplitudelist) = table_arrays
    if not (subtitle=='NB973' and num%3==2):
        tablenames.append(label+'_'+subtitle)
        tablefluxes.append(flux)
        nii6548fluxes.append(flux2)
        nii6583fluxes.append(flux3)
        ewlist.append(ew)
        ewposlist.append(ew_emission)
        ewneglist.append(ew_absorption)
        ewchecklist.append(ew_check)
        medianlist.append(median)
        pos_amplitudelist.append(pos_amplitude)
        neg_amplitudelist.append(neg_amplitude)
    #endif
    return table_arrays
#enddef