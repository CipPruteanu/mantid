# Copyright &copy; 2014,2015 ISIS Rutherford Appleton Laboratory, NScD
# Oak Ridge National Laboratory & European Spallation Source
#
# This file is part of Mantid.
# Mantid is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mantid is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File change history is stored at: <https://github.com/mantidproject/mantid>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>
"""
Do a tomographic reconstruction, including:
- Pre-processing of input raw images,
- 3d volume reconstruction using a third party tomographic reconstruction tool
- Post-processing of reconstructed volume
- Saving reconstruction results (and pre-processing results, and self-save this script and subpackages)

Example command lines:

ipython -- tomo_reconstruct.py --help

ipython -- tomo_reconstruct.py\
 --input-path=stack_larmor_metals_summed_all_bands/ --output-path=recon_out_larmor_metals_fbp500\
 --tool tomopy --algorithm sirt --cor 129

ipython -- tomo_reconstruct.py\
 --input-path=CannonTomo/SampleA/ --output-path=recon_out_canon_a\
 --tool tomopy --algorithm gridrec --cor 504


# more up-to-date:

ipython -- scripts/Imaging/IMAT/tomo_reconstruct.py\
 --input-path=../tomography-tests/stack_larmor_metals_summed_all_bands/ --output-path=REMOVE_ME\
 --tool tomopy --algorithm gridrec  --cor 123 --max-angle 360 --in-img-format=tiff\
 --region-of-interest='[5, 252, 507, 507]'

"""
import os
import sys
import time

import numpy as np

# For 3d median filter
try:
    import scipy
except ImportError:
    raise ImportError("Could not find the package scipy which is required for image pre-/post-processing")

try:
    from scipy import ndimage
except ImportError:
    raise ImportError("Could not find the subpackage scipy.ndimage, required for image pre-/post-processing")

import tomorec.io as tomoio
import tomorec.reconstruction_command as tomocmd


# MCP correction - horizontal line!!!
#  normalize proton charge

def apply_prep_filters(data, cfg, white, dark):
    """
    @param data ::
    @param cfg ::
    @param white ::
    @param dark ::
    """
    print " * Beginning pre-processing with pixel data type:", data.dtype
    if 'float64' == data.dtype:
        data = data.astype(dtype='float32')
        print " * Note: pixel data type changed to:", data.dtype

    too_verbose = False
    # quick test of a (wrong) transmission=>absorption conversion
    if False:
        for idx in range(0, data.shape[0]):
            dmax = np.amax(data[idx])

            data[idx, :, :] = dmax*dmax - data[idx, :, :]*data[idx, :, :]

    # list with first-x, first-y, second-x, second-y
    if cfg.crop_coords:
        if  isinstance(cfg.crop_coords, list) and 4 == len(cfg.crop_coords):
            data = data[:, cfg.crop_coords[1]:cfg.crop_coords[3], cfg.crop_coords[0]:cfg.crop_coords[2]]
        else:
            print("Error in crop (region of interest) parameter (expecting a list with four integers. "
                  "Got: {0}.".format(crop))

        print " * Finished crop step, with pixel data type: {0}.".format(data.dtype)
    else:
        print " * Note: not applying crop."

    if cfg.crop_coords:
        air_sums = []
        for idx in range(0, data.shape[0]):
            air_data_sum = data[idx, cfg.crop_coords[1]:cfg.crop_coords[3],
                                cfg.crop_coords[0]:cfg.crop_coords[2]].sum()
            air_sums.append(air_data_sum)
            #print "Shape of air data: ", air_data.shape
            #sum_air = air_data.sum()
            #print "Sum air, idx {0}: {1}".format(idx, sum_air)
        if too_verbose:
            print "air sums: ", air_sums
        avg = np.average(air_sums)
        if too_verbose:
            print("Air avg: {0}, max ratio: {1}, min ratio: {2}".format(
                avg, np.max(air_sums)/avg, np.min(air_sums)/avg))

    if False and cfg.normalize_flat_dark:
        norm_divide = None
        if norm_dark_img:
            norm_divide = norm_flat_img - norm_dark_img
        if cfg.crop_coords:
            norm_divide = norm_divide[:, cfg.crop_coords[1]:cfg.crop_coords[3],
                                      cfg.crop_coords[0]:cfg.crop_coords[2]]
        # prevent divide-by-zero issues
        norm_divide[norm_divide==0] = 1e-6

        for idx in range(0, data.shape[0]):
            data[idx, :, :] = np.true_divide(data[idx, :, :] - norm_dark_img, norm_divide)
        # true_divide produces float64, we assume that precision not needed (definitely not
        # for 16-bit depth images as we usually have.
        print " * Finished normalization by flat/dark images with pixel data type: {0}.".format(data.dtype)
    else:
        print " * Note: not applying normalization by flat/dark images."

    # Apply cut-off for the normalization?
    if cfg.cut_off_level and cfg.cut_off_level:
        print "* Applying cut-off with level: {0}".format(cfg.cut_off_level)
        dmin = np.amin(data)
        dmax = np.amax(data)
        rel_cut_off = dmin + cfg.cut_off_level * (dmax - dmin)
        data[data < rel_cut_off] = dmin
        print " * Finished cut-off stepa, with pixel data type: {0}".format(data.dtype)
    else:
        print " * Note: not applying cut-off."

    if cfg.mcp_corrections:
        print " * MCP corrections not implemented in this version"

    if cfg.scale_down:
        print " * Scale down not implemented in this version"

    if cfg.median_filter_size and cfg.median_filter_size > 1:
        for idx in range(0, data.shape[0]):
            data[idx] = scipy.ndimage.median_filter(data[idx], cfg.median_filter_size, mode='mirror')
            #, mode='nearest')
        print " * Finished noise filter / median, with pixel data type: {0}.".format(data.dtype)
    else:
        print " * Note: not applying noise filter /median."

    rotate = -1
    data_rotated = np.zeros((data.shape[0], data.shape[2], data.shape[1]), dtype=data.dtype)
    if rotate:
        for idx in range(0, data.shape[0]):
            # Rotation 90 degrees counterclockwise (or -90 degrees)
            data_rotated[idx] = np.rot90(data[idx,:,:], rotate)
        print " * Finished rotation step, with pixel data type: {0}".format(data_rotated.dtype)

    return data_rotated

def astra_reconstruct3d(sinogram, angles, shape, depth, alg_cfg):
    # Some of these have issues depending on the GPU setup
    algs_avail = "[FP3D_CUDA], [BP3D_CUDA]], [FDK_CUDA], [SIRT3D_CUDA], [CGLS3D_CUDA]"

    if not alg_cfg.algorithm.upper() in algs_avail:
        raise ValueError("Invalid algorithm requested for the Astra package: {0}. "
                         "Supported algorithms: {1}".format(alg_cfg.algorithm, algs_avail))
    det_rows = sinogram.shape[0]
    det_cols = sinogram.shape[2]

    vol_geom = astra.create_vol_geom(shape[0], depth, shape[1])
    proj_geom = astra.create_proj_geom('parallel3d', 1.0, 1.0, det_cols,
                                       det_rows, np.deg2rad(angles))

    sinogram_id = astra.data3d.create("-sino", proj_geom, sinogram)
    # Create a data object for the reconstruction
    rec_id = astra.data3d.create('-vol', vol_geom)

    cfg = astra.astra_dict(alg_cfg.algorithm)
    cfg['ReconstructionDataId'] = rec_id
    cfg['ProjectionDataId'] = sinogram_id

    # Create the algorithm object from the configuration structure
    alg_id = astra.algorithm.create(cfg)
    # This will have a runtime in the order of 10 seconds.
    astra.algorithm.run(alg_id, alg_cfg.num_iter)
    #if "CUDA" in params[0] and "FBP" not in params[0]:
    #self.res += astra.algorithm.get_res_norm(alg_id)**2
    #print math.sqrt(self.res)

    # Get the result
    rec = astra.data3d.get(rec_id)

    astra.algorithm.delete(alg_id)
    astra.data3d.delete(rec_id)
    astra.data3d.delete(sinogram_id)

    rec = rec[:160, :160, 1]

    return rec

def get_max_frames(algorithm):
    frames = 8 if "3D" in algorithm else 1
    return frames

def run_reconstruct_3d_astra(proj_data, proj_angles, alg_cfg):
    nSinos = get_max_frames(algorithm=algorithm)
    iterations = alg_cfg.num_iter
    print " astra recon - doing {0} iterations".format(iterations)

    # swaps outermost dimensions so it is sinogram layout
    sinogram = proj_data
    sinogram = np.swapaxes(sinogram, 0, 1)


    #ctr = cor
    #width = sinogram.shape[1]
    #pad = 50

    #sino = np.nan_to_num(1./sinogram)

    # pad the array so that the centre of rotation is in the middle
    #alen = ctr
    #blen = width - ctr
    #mid = width / 2.0

    #if ctr > mid:
        #plow = pad
        #phigh = (alen - blen) + pad
    #else:
        #plow = (blen - alen) + pad
        #phigh = pad

    #logdata = np.log(sino+1)

    sinogram = np.tile(sinogram.reshape((1,)+sinogram.shape),
                       (8, 1, 1))

    vol_shape = (proj_data.shape[1], sinogram.shape[2], proj_data.shape[1]) # ?
    rec = astra_reconstruct3d(sinogram, proj_angles, shape=vol_shape, depth=nSinos,
                              alg_cfg=alg_cfg)

    return rec

def run_reconstruct_3d_astra_simple(proj_data, proj_angles, alg_cfg, cor=None):
    """

    @param proj_data :: projection images
    @param alg_cfg :: tool/algorithm configuration
    @param cor :: center of rotation
    @param proj_angles :: angles corresponding to the projection images
    """
    sinograms = proj_data

    sinograms = np.swapaxes(sinograms, 0, 1)

    plow = (proj_data.shape[2] - cor*2)
    phigh = 0

    # minval = np.amin(sinograms)
    sinograms = np.pad(sinograms, ((0,0),(0,0),(plow,phigh)), mode='reflect')

    proj_geom = astra.create_proj_geom('parallel3d', .0, 1.0, proj_data.shape[1],
                                       sinograms.shape[2], proj_angles)
    sinogram_id = astra.data3d.create('-sino', proj_geom, sinograms)

    vol_geom = astra.create_vol_geom(proj_data.shape[1], sinograms.shape[2], proj_data.shape[1])
    recon_id = astra.data3d.create('-vol', vol_geom)
    alg_cfg = astra.astra_dict(alg_cfg.algorithm)
    alg_cfg['ReconstructionDataId'] = recon_id
    alg_cfg['ProjectionDataId'] = sinogram_id
    alg_id = astra.algorithm.create(alg_cfg)

    number_of_iters=100
    astra.algorithm.run(alg_id, number_of_iters)
    recon = astra.data3d.get(recon_id)

    astra.algorithm.delete(alg_id)
    astra.data3d.delete(recon_id)
    astra.data3d.delete(sinogram_id)

    return recon

def run_reconstruct_3d(proj_data, preproc_cfg, alg_cfg):
    """
    A 3D reconstruction

    @param proj_data :: Input projected images
    @param tool :: reconstruction tool to call/use

    Returns :: reconstructed volume
    """
    num_proj = proj_data.shape[0]
    inc = float(preproc_cfg.max_angle)/(num_proj-1)

    proj_angles=np.arange(0, num_proj*inc, inc)
    # For tomopy
    proj_angles = np.radians(proj_angles)

    verbosity = 1
    if 'astra' == alg_cfg.tool:
        #run_reconstruct_3d_astra(proj_data, algorithm, cor, proj_angles=proj_angles)
        return run_reconstruct_3d_astra_simple(proj_data, proj_angles, alg_cfg, preproc_cfg.cor)

    for slice_idx in [200]: # examples to check: [30, 130, 230, 330, 430]:
        print " > Finding center with tomopy find_center, slice_idx: {0}...".format(slice_idx)
        import tomorec.tool_imports as tti
        try:
            tomopy = tti.import_tomo_tool('tomopy')
            tomopy_cor = tomopy.find_center(tomo=proj_data, theta=proj_angles, ind=slice_idx, emission=False)
            if not preproc_cfg.cor:
                preproc_cfg.cor = tomopy_cor
            print " > Center of rotation found by tomopy.find_center:  {0}".format(tomopy_cor)
        except ImportError as exc:
            print(" * WARNING: could not import tomopy so could not use the tomopy method to find the center "
                  "of rotation. Details: {0}".format(exc))


    print "Using center of rotation: {0}".format(preproc_cfg.cor)
    start = time.time()
    if 'tomopy' == alg_cfg.tool and 'gridrec' != alg_cfg.algorithm and 'fbp' != alg_cfg.algorithm:
        if not alg_cfg.num_iter:
            alg.cfg_num_iter = tomorec.PreProcConfig.DEF_NUM_ITER
        # For ref, some typical run times with 4 cores:
        # 'bart' with num_iter=20 => 467.640s ~= 7.8m
        # 'sirt' with num_iter=30 => 698.119 ~= 11.63
        if verbosity >= 1:
            print("Running iterative method with tomopy. Algorithm: {0}, "
                  "number of iterations: {1}".format(algorithm, alg_cfg.num_iter))
        rec = tomopy.recon(tomo=proj_data, theta=proj_angles, center=cor,
                           algorithm=alg_cfg.algorithm, num_iter=alg_cfg.num_iter) #, filter_name='parzen')
    else:
        if verbosity >= 1:
            print("Running non-iterative reconstruction algorithm with tomopy. "
                  "Algorithm: {0}".format(alg_cfg.algorithm))
        rec = tomopy.recon(tomo=proj_data, theta=proj_angles, center=preproc_cfg.cor, algorithm=alg_cfg.algorithm)
    tnow = time.time()
    print "Reconstructed 3D volume. Time elapsed in reconstruction algorithm: {0:.3f}".format(tnow - start)

    return rec

def _make_dirs_if_needed(dirname):
    """
    Makes sure that the directory needed to save the file exists, or creates it

    @param dirname :: (output) directory to check
    """
    absname = os.path.abspath(dirname)
    if not os.path.exists(absname):
        os.makedirs(absname)


def read_in_stack(sample_path, img_format):
    # Note, not giving prefix. It will load all the files found.
    # Example prefixes are prefix = 'tomo_', prefix = 'LARMOR00', prefix = 'angle_agg'

    sample, white, dark = tomoio.read_stack_of_images(sample_path, file_extension=img_format)

    if not isinstance(sample, np.ndarray) or not sample.shape \
       or not isinstance(sample.shape, tuple) or 3 != len(sample.shape):
        raise RuntimeError("Error reading sample images. Could not produce a 3-dimensional array "
                           "of data from the sample images. Got: {0}".format(sample))

    return (sample, white, dark)

def apply_line_projection(imgs_angles):
    """
    Transform pixel values as $- ln (Is/I0)$, where $Is$ is the pixel (intensity) value and $I0$ is a
    reference value (pixel/intensity value for open beam, or maximum in the stack or the image).

    This produces a projection image, $ p(s) = -ln\\frac{I(s)}{I(0)} $,
    with $ I(s) = I(0) e^{-\\int_0^s \\mu(x)dx} $
    where:
    $p(s)$ represents the sum of the density of objects along a line (pixel) of the beam
    I(0) initital intensity of netron beam (white images)
    I(s) neutron count measured by detector/camera

    The integral is the density along the path through objects.
    This is required for example when pixels have neutron count values.

    @param imgs_angles :: stack of images (angular projections) as 3d numpy array. Every image will be
    processed independently, using as reference intensity the maximum pixel value found across all the
    images.

    Returns :: projected data volume (image stack)
    """
    imgs_angles = imgs_angles.astype('float32')
    for idx in range(0, imgs_angles.shape[0]):
        max_img = np.amax(imgs_angles[idx, :, :])
        to_log = np.true_divide(imgs_angles[idx, :, :], max_img)
        if False:
            print("initial img max: {0}. transformed to log scale,  min: {1}, max: {2}".
                  format(max_img, np.amin(to_log), np.amax(to_log)))
        imgs_angles[idx, :, :] = - np.log(to_log +1e-6)

    return imgs_angles

def apply_final_preproc_corrections(preproc_data, cfg):
    """
    Apply additional, optional, pre-processing steps/filters.

    @param preproc_data :: input data as a 3d volume (projection images)
    @param cfg :: pre-processing configuration
    """
    # Remove stripes in sinograms / ring artefacts in reconstructed volume
    if cfg.stripe_removal_method:
        import prep as iprep
        if 'wavelet-fourier' == cfg.stripe_removal_method.lower():
            time1 = time.time()
            print " * Removing stripes/ring artifacts using the method '{0}'".format(cfg.stripe_removal_method)
            #preproc_data = tomopy.prep.stripe.remove_stripe_fw(preproc_data)
            preproc_data = iprep.filters.remove_stripes_ring_artifacts(preproc_data, 'wavelet-fourier')
            time2 = time.time()
            print " * Removed stripes/ring artifacts. Time elapsed: {0:.3f}".format(time2 - time1)
        elif 'titarenko' == cfg.stripe_removal_method.lower():
            time1 = time.time()
            print " * Removing stripes/ring artifacts, using the method '{0}'".format(cfg.stripe_removal_method)
            preproc_data = tomopy.prep.stripe.remove_stripe_ti(preproc_data)
            time2 = time.time()
            print " * Removed stripes/ring artifacts, Time elapsed: {0:.3f}".format(time2 - time1)
        else:
            print(" * WARNING: stripe removal method '{0}' is unknown. Not applying it.".
                  format(cfg.stripe_removal_method))
    else:
        print " * Note: not applying stripe removal."

    if False:
        # preproc_data = tomopy.misc.corr.remove_outlier(preproc_data ...
        preproc_data = tomopy.misc.corr.adjust_range(preproc_data)

    if False:
        preproc_data = tomopy.prep.normalize.normalize_bg(preproc_data, air=5)

    return preproc_data

def save_preproc_images(output_dir, preproc_data, preproc_cfg,
                        subdir_name='preproc_images', out_dtype='uint16'):
    """

    """
    print " * Pre-processed images (preproc_data) dtype:", preproc_data.dtype
    min_pix = np.amin(preproc_data)
    max_pix = np.amax(preproc_data)
    print "   with min_pix: {0}, max_pix: {1}".format(min_pix, max_pix)
    if preproc_cfg.save_preproc_imgs:
        preproc_dir = os.path.join(output_dir, subdir_name)
        print "* Saving pre-processed images into: {0}".format(preproc_dir)
        _make_dirs_if_needed(preproc_dir)
        for idx in range(0, preproc_data.shape[0]):
            # rescale_intensity has issues with float64=>int16
            tomoio._write_image(preproc_data[idx, :, :], min_pix, max_pix,
                                os.path.join(preproc_dir, 'out_preproc_proj_image' + str(idx).zfill(6)),
                                dtype=out_dtype)#, rescale_intensity=False)
    else:
        print "* NOTE: not saving pre-processed images..."

def apply_postproc_filters(recon_data, cfg):
    """
    Apply all post-processing steps/filters/transformations on a reconstructed volume

    @param cfg :: post-processing configuration
    """
    import prep as iprep

    if cfg.circular_mask:
        recon_data = iprep.filters.circular_mask(recon_data, ratio=cfg.circular_mask)
        print " * Applied circular mask on reconstructed volume"
    else:
        print " * Note: not applied circular mask on reconstructed volume"

    if cfg.cut_off_level and cfg.cut_off_level > 0.0:
        print "=== applying cut-off: {0}".format(cfg.cut_off)
        dmin = np.amin(recon_data)
        dmax = np.amax(recon_data)
        rel_cut_off = dmin + cfg.cut_off * (dmax - dmin)
        recon_data[recon_data < rel_cut_off] = dmin

    if cfg.gaussian_filter_par:
        print " * Gaussian filter not implemented"

    if cfg.median_filter_size and cfg.median_filter_size > 0.0:
        recon_data = scipy.ndimage.median_filter(recon_data, cfg.median_filter_size)
        print (" * Applied median_filter on reconstructed volume, with filtersize: {0}".
               format(cfg.median_filter_size))
    else:
        print " * Note: not applied median_filter on reconstructed volume"

    if cfg.median_filter3d_size and cfg.median_filter3d_size > 0.0:
        kernel_size=3
        # Note this can be extremely slow
        recon_data = scipy.signal.medfilt(recon_data, kernel_size=kernel_size)
        print(" * Applied N-dimensional median filter on reconstructed volume, with filter size: {0} ".
              format(kernel_size))
    else:
        print " * Note: not applied N-dimensional median filter on reconstructed volume"


def save_recon_as_vertical_slices(recon_data, output_dir, name_prefix='out_recon_slice', zero_fill=6):
    """
    Save reconstructed volume (3d) into a series of slices along the Z axis (outermost numpy dimension)
    """
    _make_dirs_if_needed(output_dir)
    #tomopy.io.writer.write_tiff_stack(recon_data)
    min_pix = np.amin(recon_data)
    max_pix = np.amax(recon_data)
    for idx in range(0, recon_data.shape[0]):
        tomoio._write_image(recon_data[idx, :, :], min_pix, max_pix,
                            os.path.join(output_dir, name_prefix + str(idx).zfill(zero_fill)),
                            dtype='uint16')

def save_recon_as_horizontal_slices(recon_data, out_horiz_dir, name_prefix='out_recon_horiz_slice', zero_fill=6):
    """
    Save reconstructed volume (3d) into a series of slices along the Y axis (second numpy dimension)
    """
    _make_dirs_if_needed(out_horiz_dir)
    for idx in range(0, recon_data.shape[1]):
        tomoio._write_image(recon_data[:, idx, :], np.amin(recon_data), np.amax(recon_data),
                            os.path.join(out_horiz_dir, name_prefix + str(idx).zfill(zero_fill)),
                            dtype='uint16')

def save_recon_netcdf(recon_data, output_dir, filename='tomo_recon_vol.nc'):
    """
    A netCDF, for compatibility/easier interoperation with other tools
    """
    try:
        from scipy.io import netcdf_file
    except ImportError as exc:
        print " WARNING: could not save NetCDF file. Import error: {0}".format(exc)

    xsize = recon_data.shape[0]
    ysize = recon_data.shape[1]
    zsize = recon_data.shape[2]

    nc_path = os.path.join(output_dir, filename)
    ncfile = netcdf_file(nc_path, 'w')
    ncfile.createDimension('x', xsize)
    ncfile.createDimension('y', ysize)
    ncfile.createDimension('z', zsize)
    print " Creating netCDF volume data variable"
    data = ncfile.createVariable('data', np.dtype('int16').char, ('x','y','z'))
    print " Data shape: {0}".format(data.shape)
    print " Assigning data..."
    data[:, :, :] = recon_data[0:xsize, 0:ysize, 0:zsize]
    print " Closing netCDF file: {0}".format(nc_path)
    ncfile.close()

def save_recon_output(recon_data, output_dir):
    """
    Save output reconstructed volume in different forms.
    """
    # slices along the vertical (z) axis
    # output_dir = 'output_recon_tomopy'
    print "* Saving slices of the reconstructed volume in: {0}".format(output_dir)
    save_recon_as_vertical_slices(recon_data, output_dir)

    # Sideways slices:
    save_horiz_slices = False
    if save_horiz_slices:
        out_horiz_dir = os.path.join(output_dir, 'horiz_slices')
        print "* Saving horizontal slices in: {0}".format(out_horiz_dir)
        save_recon_as_horizontal_slices(recon_data, out_horiz_dir)

    save_netcdf_vol = True
    if save_netcdf_vol:
        print "* Saving reconstructed volume as NetCDF"
        save_recon_netcdf(recon_data, output_dir)


def do_recon(preproc_cfg, alg_cfg, postproc_cfg, cmd_line=None):
    """
    Run a reconstruction using a particular tool, algorithm and setup

    @param preproc_cfg ::

    @param alg_cfg ::

    @param postproc_cfg ::

    @param cmd_line :: command line text if running from the CLI. When provided it will
    be written in the output readme file(s) for reference.
    """
    tstart = time.time()
    data, white, dark = read_in_stack(preproc_cfg.input_dir, preproc_cfg.in_img_format)
    print "Shape of raw data: {0}, dtype: {1}".format(data.shape, data.dtype)

    raw_data_dtype = data.dtype
    raw_data_shape = data.shape

    # For Cannon. tompoy CoR: 470.8 / oct: 504

    # These imports will raise appropriate exceptions in case of error
    import tomorec.tool_imports as tti
    if 'astra' == alg_cfg.tool:
        astra = tti.import_tomo_tool('astra')
    elif 'tomopy' == alg_cfg.tool:
        tomopy = tti.import_tomo_tool('tomopy')

    median_filter_size = 3

    preproc_data = apply_prep_filters(data, preproc_cfg, white, dark)

    #preproc_data = data
    #data = apply_prep_filters(data, rotate=-1, crop=[0, 256, 512, 512])
    print "Shape of preproc data: {0}".format(preproc_data.shape)


    if preproc_cfg.line_projection:
        preproc_data = apply_line_projection(preproc_data)

    preproc_data = apply_final_preproc_corrections(preproc_data, preproc_cfg)

    #import matplotlib.pyplot as pl
    #pl.imshow(preproc_data[66], cmap='gray')
    #pl.show()

    # Save pre-proc images
    save_preproc_images(postproc_cfg.output_dir, preproc_data, preproc_cfg)

    t_recon_start = time.time()
    recon_data = run_reconstruct_3d(preproc_data, preproc_cfg, alg_cfg)
    t_recon_end = time.time()

    print("Reconstructed volume. Shape: {0}, and pixel data type: {1}".
          format(recon_data.shape, recon_data.dtype))

    apply_postproc_filters(recon_data, postproc_cfg)

    # Save output from the reconstruction
    save_recon_output(recon_data, postproc_cfg.output_dir)

    tend = time.time()

    #run_summary_string = gen_txt_run_summary()
    out_readme_fname = '0.README_reconstruction.txt'
    # generate file with dos/windows line end for windoze users' convenience
    with open(os.path.join(postproc_cfg.output_dir, out_readme_fname), 'w') as oreadme:
        #oreadme.write(run_summary_string)
        oreadme.write('Tomographic reconstruction. Summary of inputs, settings and outputs.\n')
        oreadme.write('Time now (run begin): ' + time.ctime(tstart)) #time.strftime("%c") + "\n")

        alg_hdr = ("\n"
                   "--------------------------\n"
                   "Tool/Algorithm\n"
                   "--------------------------\n")
        oreadme.write(alg_hdr)
        oreadme.write(str(alg_cfg))
        oreadme.write("\n")

        preproc_hdr = ("\n"
                       "--------------------------\n"
                       "Pre-processing parameters\n"
                       "--------------------------\n")
        oreadme.write(preproc_hdr)
        oreadme.write(str(preproc_cfg))
        oreadme.write("\n")

        postproc_hdr = ("\n"
                        "--------------------------\n"
                        "Post-processing parameters\n"
                        "--------------------------\n")
        oreadme.write(postproc_hdr)
        oreadme.write(str(postproc_cfg))
        oreadme.write("\n")

        cmd_hdr = ("\n"
                   "--------------------------\n"
                   "Command line\n"
                   "--------------------------\n")
        oreadme.write(cmd_hdr)
        oreadme.write(cmd_line)
        oreadme.write("\n")

        run_hdr = ("\n"
                   "--------------------------\n"
                   "Run/job details:\n"
                   "--------------------------\n")
        oreadme.write(run_hdr)
        oreadme.write("Dimensions of raw input sample data: {0}\n".format(raw_data_shape))
        oreadme.write("Dimensions of pre-processed sample data: {0}\n".format(preproc_data.shape))
        oreadme.write("Dimensions of reconstructed volume: {0}\n".format(recon_data.shape))
        oreadme.write("Max. angle: {0}\n".format(preproc_cfg.max_angle))

        oreadme.write("Raw input pixel type: {0}\n".format(raw_data_dtype))
        oreadme.write("Output pixel type: {0}\n".format('uint16'))
        oreadme.write("Time elapsed in reconstruction: {0:.3f}s\r\n".format(t_recon_end-t_recon_start))
        oreadme.write("Total time elapsed: {0:.3f}s\r\n".format(tend-tstart))
        oreadme.write('Time now (run end): ' + time.ctime(tend)) #time.strftime("%c") + "\n")

# To save this script (and dependencies) into the output reconstructions
def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    else:
        return os.path.dirname(unicode(__file__, encoding))

def self_save_zipped_scripts(output_path):

    def _zipdir(path, ziph):
        # ziph is zipfile handle
        for root, _, files in os.walk(path):
            for indiv_file in files:
                # Write all files, with the exception of the pyc's
                exclude_extensions = ['pyc']
                if not indiv_file.endswith(tuple(exclude_extensions)):
                    ziph.write(os.path.join(root, indiv_file))

    import inspect
    this_path = os.path.abspath(inspect.getsourcefile(lambda:0))

    scripts_path = os.path.dirname(this_path)

    _make_dirs_if_needed(output_path)
    print ("Saving myself (reconstruction scripts) from: {0} in: {1}".
           format(scripts_path, os.path.abspath(output_path)))
    import zipfile
    # os.path.join(output_path, ... )
    RECON_SCRIPTS_PKG_NAME = '0.reconstruction_scripts.zip'
    with zipfile.ZipFile(os.path.join(output_path, RECON_SCRIPTS_PKG_NAME), 'w', zipfile.ZIP_DEFLATED) as zip_scripts:
        # To write just this file: zipscr.write(this_path)
        _zipdir(scripts_path, zip_scripts)

if __name__=='__main__':
    import argparse
    import ast

    arg_parser = argparse.ArgumentParser(description='Run tomographic reconstruction via third party tools')

    grp_req = arg_parser.add_argument_group('Mandatory/required options')

    grp_req.add_argument("-i","--input-path", required=True, type=str, help="Input directory")

    grp_req.add_argument("-o","--output-path", required=True, type=str,
                         help="Where to write the output slice images (reconstructred volume)")

    grp_req.add_argument("-c","--cor", required=True, type=float,
                         help="Center of rotation (in pixels). rotation around y axis is assumed")

    grp_recon = arg_parser.add_argument_group('Reconstruction options')

    grp_recon.add_argument("-t","--tool", required=False, type=str,
                           help="Tomographic reconstruction tool to use")

    grp_recon.add_argument("-a","--algorithm", required=False, type=str,
                           help="Reconstruction algorithm (tool dependent)")

    grp_recon.add_argument("-n","--num-iter", required=False, type=int,
                           help="Number of iterations (only valid for iterative methods "
                           "(example: SIRT, ART, etc.).")


    grp_recon.add_argument("--max-angle", required=False, type=int,
                           help="Maximum angle (of the last projection), assuming first angle=0, and "
                           "uniform angle increment for every projection (note: this "
                           "is overriden by the angles found in the input FITS headers)")

    grp_pre = arg_parser.add_argument_group('Pre-processing of input raw images/projections')

    grp_pre.add_argument("--in-img-format", required=False, default='fits', type=str,
                         help="Format/file extension expected for the input images. Supported: {0}".
                         format(['tiff', 'fits', 'tif', 'fit', 'png']))

    grp_pre.add_argument("--region-of-interest", required=False, type=str,
                         help="Region of interest (crop original "
                         "images to these coordinates, given as comma separated values: x1,y1,x2,y2. If not "
                         "given, the whole images are used.")

    grp_pre.add_argument("--air-region", required=False, type=str,
                         help="Air region /region for normalization. "
                         "If not provided, the normalization against beam intensity fluctuations will not be "
                         "performed")

    grp_pre.add_argument("--median-filter-width", type=int,
                         required=False, help="Size/width of the median filter (pre-processing")

    grp_pre.add_argument("--remove-stripes", default='wf', required=False, type=str,
                         help="Methods supported: 'wf' (Wavelet-Fourier)")

    grp_pre.add_argument("--rotation", required=False, type=int,
                         help="Rotate images by 90 degrees a number of "
                         "times. The rotation is clockwise unless a negative number is given which indicates "
                         "rotation counterclocwise")

    grp_pre.add_argument("--scale-down", required=False, type=int,
                         help="Scale down factor, to reduce the size of "
                         "the images for faster (lower-resolution) reconstruction. For example a factor of 2 "
                         "reduces 1kx1k images to 512x512 images (combining blocks of 2x2 pixels into a single "
                         "pixel. The output pixels are calculated as the average of the input pixel blocks.")

    grp_pre.add_argument("--mcp-corrections", default='yes', required=False, type=str,
                         help="Perform corrections specific to images taken with the MCP detector")

    grp_post = arg_parser.add_argument_group('Post-processing of the reconstructed volume')

    grp_post.add_argument("--circular-mask", required=False, type=float, default=0.94,
                          help="Radius of the circular mask to apply on the reconstructed volume. "
                          "It is given in [0,1] relative to the size of the smaller dimension/edge "
                          "of the slices. Empty or zero implies no masking.")

    grp_post.add_argument("--cut-off", required=False, type=float,
                          help="Cut off level (percentage) for reconstructed "
                          "volume. pixels below this percentage with respect to maximum intensity in the stack "
                          "will be set to the minimum value.")

    grp_post.add_argument("--out-median-filter", required=False, type=float,
                          help="Apply median filter (2d) on reconstructed volume with the given window size.")

    arg_parser.add_argument("-v", "--verbose", action="count", default=1, help="Verbosity level. Default: 1. "
                            "User zero to supress outputs.")

    args = arg_parser.parse_args()

    # '/home/fedemp/tomography-tests/stack_larmor_metals_summed_all_bands/data_metals/'

    # Save myself
    self_save_zipped_scripts(args.output_path)

    # Grab and check pre-processing options
    pre_config = tomocmd.PreProcConfig()

    pre_config.input_dir = args.input_path

    if args.in_img_format:
        pre_config.in_img_format = args.in_img_format
    pre_config.cor = int(args.cor)


    cmd_line = " ".join(sys.argv)

    if 'yes' == args.mcp_corrections:
        pre_config.mcp_corrections = True

    if 'wf' == args.remove_stripes:
        pre_config.stripe_removal_method = 'wavelet-fourier'

    if args.region_of_interest:
        pre_config.crop_coords = ast.literal_eval(args.region_of_interest)
    else:
        border_pix = 5
        pre_config.crop_coords = [0+border_pix, 252, 512-border_pix, 512-border_pix]

    if args.median_filter_width:
        if not args.num_iter.isdigit():
            raise RuntimeError("The median filter width must be an integer")
        pre_config.median_filter_width = args.median_filter_width

    if args.max_angle:
        pre_config.max_angle = float(args.max_angle)

    # Algorithm and related options
    alg_config = tomocmd.ToolAlgorithmConfig()
    alg_config.tool = args.tool
    alg_config.algorithm = args.algorithm
    if args.num_iter:
        if not args.num_iter.isdigit():
            raise RuntimeError("The number of iterations must be an integer")
        alg_config.num_iter = int(args.num_iter)

    # post-processing options

    post_config = tomocmd.PostProcConfig()

    post_config.output_dir = args.output_path

    if args.circular_mask:
        post_config.circular_mask = float(args.circular_mask)

    if args.cut_off:
        post_config.cut_off_level = float(args.cut_off)

    if args.out_median_filter:
        post_config.median_filter_size = float(args.out_median_filter)

    do_recon(preproc_cfg=pre_config, alg_cfg=alg_config, postproc_cfg=post_config,
             cmd_line=cmd_line)
