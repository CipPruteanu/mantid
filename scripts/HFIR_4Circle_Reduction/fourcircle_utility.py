#pylint: disable=W0633,R0913,too-many-branches
import os
import urllib2
import socket
import numpy
import math

from mantid.api import AnalysisDataService

__author__ = 'wzz'


NUM_DET_ROW = 256


def check_url(url, read_lines=False):
    """ Check whether a URL is valid
    :param url:
    :param read_lines
    :return: boolean, error message
    """
    lines = None
    try:
        # Access URL
        url_stream = urllib2.urlopen(url, timeout=2)

        # Read lines
        if read_lines is True:
            lines = url_stream.readlines()
    except urllib2.URLError as url_error:
        url_stream = url_error
    except socket.timeout:
        return False, 'Time out. Try again!'

    # Return result
    if url_stream.code in (200, 401):
        url_good = True
    else:
        url_good = False

    # Close connect
    url_stream.close()

    # Return
    if read_lines is True:
        return url_good, lines
    if url_good is False:
        error_message = 'Unable to access %s.  Check internet access. Code %d' % (url, url_stream.code)
    else:
        error_message = ''

    return url_good, error_message


def convert_to_wave_length(m1_position):
    """ Convert motor m1's position to HB3A's neutron wave length
    Mapping:
    m1 = -25.87 --> 1.0030
       = -39.17 --> 1.5424
    :param m1_position: float, m1's position
    :return: wave length
    """
    assert isinstance(m1_position, float)

    if abs(m1_position - (-25.870000)) < 0.2:
        wave_length = 1.003
    elif abs(m1_position - (-39.17)) < 0.2:
        wave_length = 1.5424
    else:
        raise RuntimeError('m1 position %f is not a recognized position for wave length.' % m1_position)

    return wave_length


def generate_mask_file(file_path, ll_corner, ur_corner, rectangular=True):
    """ Generate a Mantid RIO/Mask XML file
    Requirements:
    1. file_path is writable;
    2. ll_corner and ur_corner are both 2-tuples
    3. ll_corner is to the left-lower to ur corner
    :param ll_corner:
    :param ur_corner:
    :param rectangular:
    :return:
    """
    # check
    assert isinstance(file_path, str), 'File path must be a string but not a %s.' % str(type(file_path))
    assert len(ll_corner) == 2 and len(ur_corner) == 2

    if rectangular is False:
        raise RuntimeError('Non-rectangular detector is not supported yet.')

    print '[INFO] Mask from %s to %s.' % (str(ll_corner), str(ur_corner))

    # part 1
    xml_str = '<?xml version="1.0"?>\n'
    xml_str += '<detector-masking>\n'
    xml_str += '     <group>\n'
    xml_str += '          <detids>'

    # part 2: all the masked detectors
    start_row = int(ll_corner[0])
    start_col = int(ll_corner[1])

    end_row = int(ur_corner[0])
    end_col = int(ur_corner[1])

    assert start_col < end_col

    det_sub_xml = ''
    for col_number in xrange(start_col, end_col+1):
        start_det_id = 1 + col_number * NUM_DET_ROW + start_row
        end_det_id = 1 + col_number * NUM_DET_ROW + end_row
        det_sub_xml += '%d-%d,' % (start_det_id, end_det_id)
    # END-FOR
    # remove last ','
    det_sub_xml = det_sub_xml[:-1]
    # add to xml string
    xml_str += det_sub_xml

    # part 3
    xml_str += '</detids>\n'
    xml_str += '     </group>\n'
    xml_str += '</detector-masking>'

    # write to file
    xml_file = open(file_path, 'w')
    xml_file.write(xml_str)
    xml_file.close()

    return


def get_hb3a_wavelength(m1_motor_pos):
    """ Get HB3A's wavelength according to motor 'm1''s position.
    :param m1_motor_pos:
    :return: wavelength.  None for no mapping
    """
    assert isinstance(m1_motor_pos, float), 'Motor m1\'s position %s must be a float but not %s.' \
                                            '' % (str(m1_motor_pos), type(m1_motor_pos))

    # hard-coded HB3A m1 position and wavelength mapping
    m1_pos_list = [(-25.870, 1.003),
                   (-39.170, 1.5424)]

    motor_pos_tolerance = 0.2

    for m1_tup in m1_pos_list:
        this_pos = m1_tup[0]
        if abs(m1_motor_pos-this_pos) < motor_pos_tolerance:
            return m1_tup[1]
    # END-FOR

    return None


def get_mask_ws_name(exp_number, scan_number):
    """
    Generate a standard mask workspace's name based on the experiment number and scan number
    It is assumed that a mask workspace will be applied to a scan; and
    all Pts belonged to the same scan will use the same mask workspace
    :param exp_number:
    :param scan_number:
    :return:
    """
    # check
    assert isinstance(exp_number, int)
    assert isinstance(scan_number, int)

    mask_ws_name = 'Mask_Exp%d_Scan%d' % (exp_number, scan_number)

    return mask_ws_name


def get_mask_xml_temp(work_dir, exp_number, scan_number):
    """
    Generate a temporary mask file in xml format that is conformed to Mantid's format.
    :param work_dir:
    :param exp_number:
    :param scan_number:
    :return:
    """
    # check
    assert isinstance(work_dir, str) and os.path.exists(work_dir)
    assert isinstance(exp_number, int)
    assert isinstance(scan_number, int)

    file_name = os.path.join(work_dir, 'temp_mask_%d_%d.xml' % (exp_number, scan_number))

    return file_name


def get_scans_list(server_url, exp_no, return_list=False):
    """ Get list of scans under one experiment
    :param server_url:
    :param exp_no:
    :param return_list: a flag to control the return value. If true, return a list; otherwise, message string
    :return: message
    """
    if server_url.endswith('/') is False:
        server_url = '%s/' % server_url
    data_dir_url = '%sexp%d/Datafiles' % (server_url, exp_no)

    does_exist, raw_lines = check_url(data_dir_url, read_lines=True)
    if does_exist is False:
        return "Experiment %d's URL %s cannot be found." % (exp_no, data_dir_url)

    # Scan through the index page
    scan_list = []
    header = 'HB3A_exp%04d_scan' % exp_no
    for line in raw_lines:
        if line.count(header) > 0:
            # try to find file HB3A_exp0123_scan6789.dat
            term = line.split(header)[1].split('.dat')[0]
            scan = int(term)
            # check
            if '%04d' % scan == term:
                scan_list.append(scan)
    # END_FOR
    scan_list = sorted(scan_list)
    if return_list is True:
        return scan_list

    message = 'Experiment %d: Scan from %d to %d' % (exp_no, scan_list[0], scan_list[-1])

    return message


def get_scans_list_local_disk(local_dir, exp_no):
    """ Get scans from a specified directory on local disk
    :param local_dir:
    :param exp_no:
    :return:
    """
    scan_list = []

    file_names = os.listdir(local_dir)
    header = 'HB3A_exp%04d_scan' % exp_no
    for name in file_names:
        if name.count(header) > 0:
            scan = int(name.split(header)[1].split('.dat')[0])
            scan_list.append(scan)

    scan_list = sorted(scan_list)

    if len(scan_list) == 0:
        message = 'Experiment %d: No scan can be found.' % exp_no
    else:
        message = 'Experiment %d: Scan from %d to %d ' % (exp_no, scan_list[0], scan_list[-1])
        num_skip_scans = scan_list[-1] - scan_list[0] + 1 - len(scan_list)
        if num_skip_scans > 0:
            message += 'with %d ' % num_skip_scans
        else:
            message += 'without '
        message += 'missing scans.'

    return message


def parse_int_array(int_array_str):
    """ Validate whether the string can be divided into integer strings.
    Allowed: a, b, c-d, e, f
    :param int_array_str:
    :return:
    """
    int_array_str = str(int_array_str)
    if int_array_str == "":
        return True, []

    # Split by ","
    term_level_0 = int_array_str.split(",")
    integer_list = []

    # For each term
    err_msg = ""
    ret_status = True

    for level0_term in term_level_0:
        level0_term = level0_term.strip()

        # split upon dash -
        num_dashes = level0_term.count("-")
        if num_dashes == 0:
            # one integer
            value_str = level0_term
            try:
                int_value = int(value_str)
                if str(int_value) != value_str:
                    ret_status = False
                    err_msg = "Contains non-integer string %s." % value_str
            except ValueError:
                ret_status = False
                err_msg = "String %s is not an integer." % value_str
            else:
                integer_list.append(int_value)

        elif num_dashes == 1:
            # Integer range
            two_terms = level0_term.split("-")
            temp_list = []
            for i in xrange(2):
                value_str = two_terms[i]
                try:
                    int_value = int(value_str)
                    if str(int_value) != value_str:
                        ret_status = False
                        err_msg = "Contains non-integer string %s." % value_str
                except ValueError:
                    ret_status = False
                    err_msg = "String %s is not an integer." % value_str
                else:
                    temp_list.append(int_value)

                # break loop
                if ret_status is False:
                    break
            # END_FOR(i)
            integer_list.extend(range(temp_list[0], temp_list[1]+1))

        else:
            # Undefined situation
            ret_status = False
            err_msg = "Term %s contains more than 1 dash." % level0_term
        # END-IF-ELSE

        # break loop if something is wrong
        if ret_status is False:
            break
    # END-FOR(level0_term)

    # Return with false
    if ret_status is False:
        return False, err_msg

    return True, integer_list


def get_det_xml_file_name(instrument_name, exp_number, scan_number, pt_number):
    """
    Get detector XML file name (from SPICE)
    :param instrument_name:
    :param exp_number:
    :param scan_number:
    :param pt_number:
    :return:
    """
    # check
    assert isinstance(instrument_name, str)
    assert isinstance(exp_number, int), 'Experiment number must be an int but not %s.' % str(type(exp_number))
    assert isinstance(scan_number, int), 'Scan number must be an int but not %s.' % str(type(scan_number))
    assert isinstance(pt_number, int), 'Pt number must be an int but not %s.' % str(type(pt_number))

    # get name
    xml_file_name = '%s_exp%d_scan%04d_%04d.xml' % (instrument_name, exp_number,
                                                    scan_number, pt_number)

    return xml_file_name


def get_det_xml_file_url(server_url, instrument_name, exp_number, scan_number, pt_number):
    """ Get the URL to download the detector counts file in XML format
    :param server_url:
    :param instrument_name:
    :param exp_number:
    :param scan_number:
    :param pt_number:
    :return:
    """
    assert isinstance(server_url, str) and isinstance(instrument_name, str)
    assert isinstance(exp_number, int) and isinstance(scan_number, int) and isinstance(pt_number, int)

    base_file_name = get_det_xml_file_name(instrument_name, exp_number, scan_number, pt_number)
    file_url = '%s/exp%d/Datafiles/%s' % (server_url, exp_number, base_file_name)

    return file_url


def get_spice_file_name(instrument_name, exp_number, scan_number):
    """
    Get standard HB3A SPICE file name from experiment number and scan number
    :param instrument_name
    :param exp_number:
    :param scan_number:
    :return:
    """
    assert isinstance(instrument_name, str)
    assert isinstance(exp_number, int) and isinstance(scan_number, int)
    file_name = '%s_exp%04d_scan%04d.dat' % (instrument_name, exp_number, scan_number)

    return file_name


def get_spice_file_url(server_url, instrument_name, exp_number, scan_number):
    """ Get the SPICE file's URL from server
    :param server_url:
    :param instrument_name:
    :param exp_number:
    :param scan_number:
    :return:
    """
    assert isinstance(server_url, str) and isinstance(instrument_name, str)
    assert isinstance(exp_number, int) and isinstance(scan_number, int)

    file_url = '%sexp%d/Datafiles/%s_exp%04d_scan%04d.dat' % (server_url, exp_number,
                                                              instrument_name, exp_number, scan_number)

    return file_url


def get_spice_table_name(exp_number, scan_number):
    """ Form the name of the table workspace for SPICE
    :param exp_number:
    :param scan_number:
    :return:
    """
    # table_name = 'HB3A_Exp%03d_%04d_SpiceTable' % (exp_number, scan_number)
    table_name = 'HB3A_exp%04d_scan%04d' % (exp_number, scan_number)

    return table_name


def get_raw_data_workspace_name(exp_number, scan_number, pt_number):
    """ Form the name of the matrix workspace to which raw pt. XML file is loaded
    :param exp_number:
    :param scan_number:
    :param pt_number:
    :return:
    """
    ws_name = 'HB3A_exp%d_scan%04d_%04d' % (exp_number, scan_number, pt_number)

    return ws_name


def get_integrated_peak_ws_name(exp_number, scan_number, pt_list, mask=False,
                                normalized_by_monitor=False,
                                normalized_by_time=False):
    """
    Get/form the integrated peak workspace's name
    :param exp_number:
    :param scan_number:
    :param pt_list: a list OR None
    :return:
    """
    # check
    assert isinstance(exp_number, int)
    assert isinstance(scan_number, int)
    assert isinstance(pt_list, list) or pt_list is None
    if isinstance(pt_list, list):
        assert len(pt_list) > 0

    # form the name
    ws_name = 'Integrated_exp%d_scan%d' % (exp_number, scan_number)
    if pt_list is not None:
        ws_name += 'Pt%d_%d' % (pt_list[0], pt_list[-1])

    if mask:
        ws_name += '_Masked'

    if normalized_by_monitor:
        ws_name += '_NormMon'

    if normalized_by_time:
        ws_name += '_NormTime'

    return ws_name


def get_log_data(spice_table, log_name):
    """
    Purpose: Get the sample log data of a scan, which contains a few of Pt.
    Requirements: SPICE table workspace and a valid log name (a column's name) in the table workspace
    Guarantee: a numpy array is created and returned.  Each item is the log value for a Pt.
    :param spice_table: SPICE TableWorkspace
    :param log_name: the name of the log to get retrieve.
    :return:
    """
    assert isinstance(log_name, str), 'Log name must be a string.'

    col_names = spice_table.getColumnNames()
    log_col_index = col_names.index(log_name)
    if log_col_index >= len(col_names):
        raise KeyError('Log name %s does not exist in SPICE table.' % log_name)

    num_rows = spice_table.rowCount()
    log_vector = numpy.ndarray((num_rows,), 'float')
    for i in range(num_rows):
        log_vector[i] = spice_table.cell(i, log_col_index)

    return log_vector


def get_step_motor_parameters(log_value_vector):
    """
    Calculate some statistic parameters of a motor log (motor position) of a scan containing Pt.
    Requirements: input is a numpy array
    Guarantee: the standard deviation of motor position, increment of motor position and standard deviation
               of the increment of motor positions are calculated
    :param log_value_vector:
    :return: 3-tuple as (1) standard deviation of motor position, (2) average increment of the motor position,
                    and (3) standard deviation of the increment of motor position.
    """
    std_dev = numpy.std(log_value_vector)

    step_vector = log_value_vector[1:] - log_value_vector[:-1]
    assert len(step_vector) > 0, 'Log value vector size = %d. Step vector size = 0 is not allowed.' \
                                 '' % len(log_value_vector)
    step_dev = numpy.std(step_vector)
    step = sum(step_vector)/len(step_vector)

    return std_dev, step, step_dev


def get_merged_md_name(instrument_name, exp_no, scan_no, pt_list):
    """
    Build the merged scan's MDEventworkspace's name under convention
    Requirements: experiment number and scan number are integer. Pt list is a list of integer
    :param instrument_name:
    :param exp_no:
    :param scan_no:
    :param pt_list:
    :return:
    """
    # check
    assert isinstance(instrument_name, str)
    assert isinstance(exp_no, int) and isinstance(scan_no, int)
    assert isinstance(pt_list, list)
    assert len(pt_list) > 0

    merged_ws_name = '%s_Exp%d_Scan%d_Pt%d_%d_MD' % (instrument_name, exp_no, scan_no,
                                                     pt_list[0], pt_list[-1])

    return merged_ws_name


def get_merged_hkl_md_name(instrument_name, exp_no, scan_no, pt_list):
    """
    Build the merged scan's MDEventworkspace's name under convention
    Requirements: experiment number and scan number are integer. Pt list is a list of integer
    :param instrument_name:
    :param exp_no:
    :param scan_no:
    :param pt_list:
    :return:
    """
    # check
    assert isinstance(instrument_name, str)
    assert isinstance(exp_no, int) and isinstance(scan_no, int)
    assert isinstance(pt_list, list)
    assert len(pt_list) > 0

    merged_ws_name = '%s_Exp%d_Scan%d_Pt%d_%d_HKL_MD' % (instrument_name, exp_no, scan_no,
                                                         pt_list[0], pt_list[-1])

    return merged_ws_name


def get_merge_pt_info_ws_name(exp_no, scan_no):
    """ Create the standard table workspace's name to contain the information to merge Pts. in a scan
    :param exp_no:
    :param scan_no:
    :return:
    """
    ws_name = 'ScanPtInfo_Exp%d_Scan%d' % (exp_no, scan_no)

    return ws_name


def get_peak_ws_name(exp_number, scan_number, pt_number_list):
    """
    Form the name of the peak workspace
    :param exp_number:
    :param scan_number:
    :param pt_number_list:
    :return:
    """
    # check
    assert isinstance(exp_number, int) and isinstance(scan_number, int)
    assert isinstance(pt_number_list, list) and len(pt_number_list) > 0

    ws_name = 'Peak_Exp%d_Scan%d_Pt%d_%d' % (exp_number, scan_number,
                                             pt_number_list[0],
                                             pt_number_list[-1])

    return ws_name


def get_single_pt_md_name(exp_number, scan_number, pt_number):
    """ Form the name of the MDEvnetWorkspace for a single Pt. measurement
    :param exp_number:
    :param scan_number:
    :param pt_number:
    :return:
    """
    ws_name = 'HB3A_Exp%d_Scan%d_Pt%d_MD' % (exp_number, scan_number, pt_number)

    return ws_name


def get_wave_length(spice_table_name):
    """ Get wave length from a SPICE table workspace for HB3A (4-circle)
    Assumption: in a scan (all Pt. are in a same SPICE table), all m1 value should be same.
    :param spice_table_name: name of the table workspace
    :return: wave length
    """
    # check
    assert isinstance(spice_table_name, str), 'Input SPICE table workspace name must be a string.'
    assert AnalysisDataService.doesExist(spice_table_name)

    spice_table_ws = AnalysisDataService.retrieve(spice_table_name)

    # get the column
    column_name_list = spice_table_ws.getColumnNames()
    col_index_m1 = column_name_list.index('m1')
    assert col_index_m1 < len(column_name_list), 'Column m1 cannot be found.'

    m1_position = float(spice_table_ws.cell(0, col_index_m1))
    wave_length = convert_to_wave_length(m1_position)

    return wave_length


def load_hb3a_md_data(file_name):
    """ Load an ASCii file containing MDEvents and generated by mantid algorithm ConvertCWSDMDtoHKL()
    :param file_name:
    :return:
    """
    # check
    assert isinstance(file_name, str) and os.path.exists(file_name)

    # parse
    data_file = open(file_name, 'r')
    raw_lines = data_file.readlines()
    data_file.close()

    # construct ND data array
    xyz_points = numpy.zeros((len(raw_lines), 3))
    intensities = numpy.zeros((len(raw_lines), ))

    # parse
    for i in xrange(len(raw_lines)):
        line = raw_lines[i].strip()

        # skip empty line
        if len(line) == 0:
            continue

        # set value
        terms = line.split(',')
        for j in xrange(3):
            xyz_points[i][j] = float(terms[j])
        intensities[i] = float(terms[3])
    # END-FOR

    return xyz_points, intensities


def round_hkl_1(hkl):
    """
    Round HKL to nearest integer
    :param hkl:
    :return:
    """
    print type(hkl)

    mi_h = round(hkl[0])
    mi_k = round(hkl[1])
    mi_l = round(hkl[2])

    return mi_h, mi_k, mi_l


def round_hkl(index_h, index_k, index_l):
    """

    :param index_h:
    :param index_k:
    :param index_l:
    :return:
    """
    index_h = math.copysign(1, index_h) * int(abs(index_h) + 0.5)
    index_k = math.copysign(1, index_k) * int(abs(index_k) + 0.5)
    index_l = math.copysign(1, index_l) * int(abs(index_l) + 0.5)

    return index_h, index_k, index_l


def round_miller_index(value, tol):
    """
    round a peak index (h, k, or l) with some tolerance
    :param value:
    :param tol:
    :return:
    """
    round_int = math.copysign(1, value) * int(abs(value) + 0.5)
    if abs(round_int - value) >= tol:
        # it is likely a magnetic peak
        round_int = int(value * 100) * 0.01

    return round_int


def convert_hkl_to_integer(index_h, index_k, index_l, magnetic_tolerance=0.2):
    """
    Convert index (HKL) to integer by considering magnetic peaks
    if any index is not close to an integer (default to 0.2), then it is treated as a magnetic peak's HKL
    :param index_h:
    :param index_k:
    :param index_l:
    :param magnetic_tolerance: tolerance to magnetic peak's indexing
    :return:
    """
    # check inputs' validity
    assert isinstance(magnetic_tolerance, float) and 0. < magnetic_tolerance <= 0.5

    #
    index_h_r = round_miller_index(index_h, magnetic_tolerance)
    index_k_r = round_miller_index(index_k, magnetic_tolerance)
    index_l_r = round_miller_index(index_l, magnetic_tolerance)

    round_error = math.sqrt((index_h - index_h_r) ** 2 +
                            (index_k - index_k_r) ** 2 +
                            (index_l - index_l_r) ** 2)

    return (index_h_r, index_k_r, index_l_r), round_error


def is_peak_nuclear(index_h, index_k, index_l, magnetic_tolerance=0.2):
    """
    Check whether a peak is a nuclear peak by checking its index close enough to integers
    :param index_h:
    :param index_k:
    :param index_l:
    :param magnetic_tolerance:
    :return:
    """
    round_h = math.copysign(1, index_h) * int(abs(index_h) + 0.5)
    if abs(round_h - index_h) >= magnetic_tolerance:
        return False

    round_k = math.copysign(1, index_k) * int(abs(index_k) + 0.5)
    if abs(round_k - index_k) >= magnetic_tolerance:
        return False

    round_l = math.copysign(1, index_l) * int(abs(index_l) + 0.5)
    if abs(round_l - index_l) >= magnetic_tolerance:
        return False

    return True
