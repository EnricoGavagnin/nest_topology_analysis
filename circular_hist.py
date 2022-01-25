def circular_hist(data, bins=36, title=''):
    
    import numpy as np
    import matplotlib.pylab as plt
    from scipy.stats import circvar, circmean
    
    # bins width
    width = (2 * np.pi) / bins
    theta = np.linspace(-np.pi, np.pi + width, num=bins + 2, endpoint=True) - width/2
    theta[0] = -np.pi
    theta[-1] = np.pi
    
    radii = np.histogram(data, theta)[0]
    radii[0] += radii[-1]
    radii = radii[:-1]    
    # Construct ax with polar projection
    ax = plt.subplot(111, polar=True)
    
    # Set Orientation
    ax.set_theta_zero_location('E')
    ax.set_theta_direction(-1)
    ax.set_xlim(-np.pi/1.000001, np.pi/1.000001)  # workaround for a weird issue
    ax.set_xticks([-np.pi/1.000001 + i/8 * 2*np.pi/1.000001 for i in range(8)],
                  [r'$-\pi$',r'$-\frac{3\pi}{4}$',r'$-\frac{\pi}{2}$',r'$-\frac{\pi}{4}$',r'$0$',r'$\frac{\pi}{4}$',r'$\frac{\pi}{2}$',r'$\frac{3\pi}{4}$'])

    
    
    # Plot bars:
    bars = ax.bar(x=np.linspace(-np.pi, np.pi-width, num=bins), height=radii, width=width)
    # Plot Line:
    #line = ax.plot(x, y, linewidth=1, color='red', zorder=3)

    # Grid settings
    M = np.max(radii)
    ax.set_rgrids(np.arange(50, M, 50), angle=0, weight='black')
    
    # compute circular mean and variance
    cmean = circmean(data, np.pi, -np.pi)
    cvar = circvar(data, np.pi, -np.pi)
    
    # Display mean and variance 
    ax.text(40,280, 'c-mean={:.4f}\n'.format(cmean)+'c-var={:.4f}\n'.format(cvar))
    
    # Title
    ax.set_title(title, va='bottom')
    plt.show()
    
    return ax
