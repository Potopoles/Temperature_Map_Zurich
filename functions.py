import numpy as np

#def hourly_ts_to_diurnal(ts):
#    """
#    Converts a time series (vector with hourly mean values)) into
#    diurnal matrix (2 D matrix (days,hours of the day))
#
#    """
#    nDays = int(ts.shape[0]/24)
#    diurnal = np.zeros((nDays,24))
#    for hr in range(0,24):
#        diurnal[:,hr] = ts[np.arange(0,len(ts),24)+hr]
#    return(diurnal)



def plot_map(grid,values,hashes):
    """
    Converts a time series (vector with hourly mean values)) into
    diurnal matrix (2 D matrix (days,hours of the day))

    """
    zlim0 = np.min(values)
    zlim1 = np.max(values)


    # color normalization
    #cmap = cm.get_cmap('YlOrRd')
    cmap = cm.get_cmap('jet')
    norm = Normalize(vmin=zlim0, vmax=zlim1)
    quit()

    cells = []
    colors = []
    #predictions = []
    for hash in hashes:
        x0 = model[hash]['chx0']
        x1 = model[hash]['chx1']
        y0 = model[hash]['chy0']
        y1 = model[hash]['chy1']

        cell = Rectangle((x0, y0), x1-x0, y1-y0)
        cells.append(cell)

        col = cmap(norm(model[hash]['pred_absT']))
        colors.append(col)

    pc = PatchCollection(cells, facecolor=colors, alpha=0.3)

    ax.add_collection(pc)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([zlim0,zlim1])
    fig.colorbar(mappable)

    factor = 400
    fig.set_size_inches((maxx-minx)/factor,(maxy-miny)/factor)
    fig.tight_layout()

    if i_save_fig:
        plt.savefig(img_out_path)
        plt.close('all')
    else:
        plt.show()
        plt.close('all')
