# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './dgs_sample_setup.ui'
#
# Created: Thu Jul 18 11:48:15 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName(_fromUtf8("Frame"))
        Frame.resize(1020, 793)
        Frame.setFrameShape(QtGui.QFrame.StyledPanel)
        Frame.setFrameShadow(QtGui.QFrame.Raised)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Frame)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.sample_label = QtGui.QLabel(Frame)
        self.sample_label.setMinimumSize(QtCore.QSize(170, 0))
        self.sample_label.setObjectName(_fromUtf8("sample_label"))
        self.horizontalLayout.addWidget(self.sample_label)
        self.sample_edit = QtGui.QLineEdit(Frame)
        self.sample_edit.setObjectName(_fromUtf8("sample_edit"))
        self.horizontalLayout.addWidget(self.sample_edit)
        self.sample_browse = QtGui.QPushButton(Frame)
        self.sample_browse.setObjectName(_fromUtf8("sample_browse"))
        self.horizontalLayout.addWidget(self.sample_browse)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.output_ws_label = QtGui.QLabel(Frame)
        self.output_ws_label.setMinimumSize(QtCore.QSize(170, 0))
        self.output_ws_label.setObjectName(_fromUtf8("output_ws_label"))
        self.horizontalLayout_9.addWidget(self.output_ws_label)
        self.output_ws_edit = QtGui.QLineEdit(Frame)
        self.output_ws_edit.setObjectName(_fromUtf8("output_ws_edit"))
        self.horizontalLayout_9.addWidget(self.output_ws_edit)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.detcal_label = QtGui.QLabel(Frame)
        self.detcal_label.setMinimumSize(QtCore.QSize(170, 0))
        self.detcal_label.setObjectName(_fromUtf8("detcal_label"))
        self.horizontalLayout_8.addWidget(self.detcal_label)
        self.detcal_edit = QtGui.QLineEdit(Frame)
        self.detcal_edit.setObjectName(_fromUtf8("detcal_edit"))
        self.horizontalLayout_8.addWidget(self.detcal_edit)
        self.detcal_browse = QtGui.QPushButton(Frame)
        self.detcal_browse.setObjectName(_fromUtf8("detcal_browse"))
        self.horizontalLayout_8.addWidget(self.detcal_browse)
        self.label_3 = QtGui.QLabel(Frame)
        self.label_3.setMinimumSize(QtCore.QSize(15, 0))
        self.label_3.setText(_fromUtf8(""))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_8.addWidget(self.label_3)
        self.relocate_dets_cb = QtGui.QCheckBox(Frame)
        self.relocate_dets_cb.setObjectName(_fromUtf8("relocate_dets_cb"))
        self.horizontalLayout_8.addWidget(self.relocate_dets_cb)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.inc_energy_gb = QtGui.QGroupBox(Frame)
        self.inc_energy_gb.setObjectName(_fromUtf8("inc_energy_gb"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.inc_energy_gb)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        self.ei_guess_label = QtGui.QLabel(self.inc_energy_gb)
        self.ei_guess_label.setMinimumSize(QtCore.QSize(147, 0))
        self.ei_guess_label.setObjectName(_fromUtf8("ei_guess_label"))
        self.horizontalLayout_10.addWidget(self.ei_guess_label)
        self.ei_guess_edit = QtGui.QLineEdit(self.inc_energy_gb)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ei_guess_edit.sizePolicy().hasHeightForWidth())
        self.ei_guess_edit.setSizePolicy(sizePolicy)
        self.ei_guess_edit.setObjectName(_fromUtf8("ei_guess_edit"))
        self.horizontalLayout_10.addWidget(self.ei_guess_edit)
        self.ei_units_label = QtGui.QLabel(self.inc_energy_gb)
        self.ei_units_label.setObjectName(_fromUtf8("ei_units_label"))
        self.horizontalLayout_10.addWidget(self.ei_units_label)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem3)
        self.use_ei_guess_chkbox = QtGui.QCheckBox(self.inc_energy_gb)
        self.use_ei_guess_chkbox.setObjectName(_fromUtf8("use_ei_guess_chkbox"))
        self.horizontalLayout_10.addWidget(self.use_ei_guess_chkbox)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tzero_guess_label = QtGui.QLabel(self.inc_energy_gb)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tzero_guess_label.sizePolicy().hasHeightForWidth())
        self.tzero_guess_label.setSizePolicy(sizePolicy)
        self.tzero_guess_label.setMinimumSize(QtCore.QSize(147, 0))
        self.tzero_guess_label.setObjectName(_fromUtf8("tzero_guess_label"))
        self.horizontalLayout_2.addWidget(self.tzero_guess_label)
        self.tzero_guess_edit = QtGui.QLineEdit(self.inc_energy_gb)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tzero_guess_edit.sizePolicy().hasHeightForWidth())
        self.tzero_guess_edit.setSizePolicy(sizePolicy)
        self.tzero_guess_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.tzero_guess_edit.setObjectName(_fromUtf8("tzero_guess_edit"))
        self.horizontalLayout_2.addWidget(self.tzero_guess_edit)
        self.tzero_guess_unit_label = QtGui.QLabel(self.inc_energy_gb)
        self.tzero_guess_unit_label.setObjectName(_fromUtf8("tzero_guess_unit_label"))
        self.horizontalLayout_2.addWidget(self.tzero_guess_unit_label)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.monitor_specid_label = QtGui.QLabel(self.inc_energy_gb)
        self.monitor_specid_label.setMinimumSize(QtCore.QSize(147, 0))
        self.monitor_specid_label.setObjectName(_fromUtf8("monitor_specid_label"))
        self.horizontalLayout_7.addWidget(self.monitor_specid_label)
        self.monitor1_specid_edit = QtGui.QLineEdit(self.inc_energy_gb)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.monitor1_specid_edit.sizePolicy().hasHeightForWidth())
        self.monitor1_specid_edit.setSizePolicy(sizePolicy)
        self.monitor1_specid_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.monitor1_specid_edit.setObjectName(_fromUtf8("monitor1_specid_edit"))
        self.horizontalLayout_7.addWidget(self.monitor1_specid_edit)
        self.label_2 = QtGui.QLabel(self.inc_energy_gb)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_7.addWidget(self.label_2)
        self.monitor2_specid_edit = QtGui.QLineEdit(self.inc_energy_gb)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.monitor2_specid_edit.sizePolicy().hasHeightForWidth())
        self.monitor2_specid_edit.setSizePolicy(sizePolicy)
        self.monitor2_specid_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.monitor2_specid_edit.setObjectName(_fromUtf8("monitor2_specid_edit"))
        self.horizontalLayout_7.addWidget(self.monitor2_specid_edit)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.verticalLayout_3.addWidget(self.inc_energy_gb)
        self.et_range_box = QtGui.QGroupBox(Frame)
        self.et_range_box.setCheckable(False)
        self.et_range_box.setChecked(False)
        self.et_range_box.setObjectName(_fromUtf8("et_range_box"))
        self.verticalLayout = QtGui.QVBoxLayout(self.et_range_box)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.etr_low_label = QtGui.QLabel(self.et_range_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.etr_low_label.sizePolicy().hasHeightForWidth())
        self.etr_low_label.setSizePolicy(sizePolicy)
        self.etr_low_label.setMinimumSize(QtCore.QSize(60, 0))
        self.etr_low_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.etr_low_label.setObjectName(_fromUtf8("etr_low_label"))
        self.horizontalLayout_6.addWidget(self.etr_low_label)
        self.etr_low_edit = QtGui.QLineEdit(self.et_range_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.etr_low_edit.sizePolicy().hasHeightForWidth())
        self.etr_low_edit.setSizePolicy(sizePolicy)
        self.etr_low_edit.setObjectName(_fromUtf8("etr_low_edit"))
        self.horizontalLayout_6.addWidget(self.etr_low_edit)
        self.etr_width_label = QtGui.QLabel(self.et_range_box)
        self.etr_width_label.setObjectName(_fromUtf8("etr_width_label"))
        self.horizontalLayout_6.addWidget(self.etr_width_label)
        self.etr_width_edit = QtGui.QLineEdit(self.et_range_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.etr_width_edit.sizePolicy().hasHeightForWidth())
        self.etr_width_edit.setSizePolicy(sizePolicy)
        self.etr_width_edit.setObjectName(_fromUtf8("etr_width_edit"))
        self.horizontalLayout_6.addWidget(self.etr_width_edit)
        self.etr_high_label = QtGui.QLabel(self.et_range_box)
        self.etr_high_label.setObjectName(_fromUtf8("etr_high_label"))
        self.horizontalLayout_6.addWidget(self.etr_high_label)
        self.etr_high_edit = QtGui.QLineEdit(self.et_range_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.etr_high_edit.sizePolicy().hasHeightForWidth())
        self.etr_high_edit.setSizePolicy(sizePolicy)
        self.etr_high_edit.setObjectName(_fromUtf8("etr_high_edit"))
        self.horizontalLayout_6.addWidget(self.etr_high_edit)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem7)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.et_range_box)
        self.label.setMinimumSize(QtCore.QSize(25, 0))
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.et_is_distribution_cb = QtGui.QCheckBox(self.et_range_box)
        self.et_is_distribution_cb.setChecked(True)
        self.et_is_distribution_cb.setObjectName(_fromUtf8("et_is_distribution_cb"))
        self.horizontalLayout_3.addWidget(self.et_is_distribution_cb)
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem8)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addWidget(self.et_range_box)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.hardmask_label = QtGui.QLabel(Frame)
        self.hardmask_label.setMinimumSize(QtCore.QSize(110, 0))
        self.hardmask_label.setObjectName(_fromUtf8("hardmask_label"))
        self.horizontalLayout_4.addWidget(self.hardmask_label)
        self.hardmask_edit = QtGui.QLineEdit(Frame)
        self.hardmask_edit.setObjectName(_fromUtf8("hardmask_edit"))
        self.horizontalLayout_4.addWidget(self.hardmask_edit)
        self.hardmask_browse = QtGui.QPushButton(Frame)
        self.hardmask_browse.setObjectName(_fromUtf8("hardmask_browse"))
        self.horizontalLayout_4.addWidget(self.hardmask_browse)
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem9)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.grouping_label = QtGui.QLabel(Frame)
        self.grouping_label.setMinimumSize(QtCore.QSize(110, 0))
        self.grouping_label.setObjectName(_fromUtf8("grouping_label"))
        self.horizontalLayout_5.addWidget(self.grouping_label)
        self.grouping_edit = QtGui.QLineEdit(Frame)
        self.grouping_edit.setObjectName(_fromUtf8("grouping_edit"))
        self.horizontalLayout_5.addWidget(self.grouping_edit)
        self.grouping_browse = QtGui.QPushButton(Frame)
        self.grouping_browse.setObjectName(_fromUtf8("grouping_browse"))
        self.horizontalLayout_5.addWidget(self.grouping_browse)
        spacerItem10 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem10)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.show_workspaces_cb = QtGui.QCheckBox(Frame)
        self.show_workspaces_cb.setObjectName(_fromUtf8("show_workspaces_cb"))
        self.horizontalLayout_11.addWidget(self.show_workspaces_cb)
        spacerItem11 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem11)
        self.verticalLayout_3.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout_13.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.savedir_label = QtGui.QLabel(Frame)
        self.savedir_label.setMinimumSize(QtCore.QSize(170, 0))
        self.savedir_label.setObjectName(_fromUtf8("savedir_label"))
        self.horizontalLayout_13.addWidget(self.savedir_label)
        self.savedir_edit = QtGui.QLineEdit(Frame)
        self.savedir_edit.setObjectName(_fromUtf8("savedir_edit"))
        self.horizontalLayout_13.addWidget(self.savedir_edit)
        self.savedir_browse = QtGui.QPushButton(Frame)
        self.savedir_browse.setObjectName(_fromUtf8("savedir_browse"))
        self.horizontalLayout_13.addWidget(self.savedir_browse)
        spacerItem12 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem12)
        self.verticalLayout_3.addLayout(self.horizontalLayout_13)
        spacerItem13 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem13)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QtGui.QApplication.translate("Frame", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.sample_label.setText(QtGui.QApplication.translate("Frame", "Sample Data", None, QtGui.QApplication.UnicodeUTF8))
        self.sample_edit.setToolTip(QtGui.QApplication.translate("Frame", "Data runs to be processed", None, QtGui.QApplication.UnicodeUTF8))
        self.sample_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Dtata runs to be processed", None, QtGui.QApplication.UnicodeUTF8))
        self.sample_browse.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.output_ws_label.setText(QtGui.QApplication.translate("Frame", "Output Workspace Name", None, QtGui.QApplication.UnicodeUTF8))
        self.detcal_label.setText(QtGui.QApplication.translate("Frame", "DetCal File", None, QtGui.QApplication.UnicodeUTF8))
        self.detcal_browse.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.relocate_dets_cb.setText(QtGui.QApplication.translate("Frame", "Relocate Detectors", None, QtGui.QApplication.UnicodeUTF8))
        self.inc_energy_gb.setTitle(QtGui.QApplication.translate("Frame", "Incident Energy Calculation", None, QtGui.QApplication.UnicodeUTF8))
        self.ei_guess_label.setText(QtGui.QApplication.translate("Frame", "Incident Energy Guess", None, QtGui.QApplication.UnicodeUTF8))
        self.ei_units_label.setText(QtGui.QApplication.translate("Frame", "meV", None, QtGui.QApplication.UnicodeUTF8))
        self.use_ei_guess_chkbox.setText(QtGui.QApplication.translate("Frame", "Use Guess (No Calculation)", None, QtGui.QApplication.UnicodeUTF8))
        self.tzero_guess_label.setText(QtGui.QApplication.translate("Frame", "TZero Guess", None, QtGui.QApplication.UnicodeUTF8))
        self.tzero_guess_unit_label.setText(QtGui.QApplication.translate("Frame", "microseconds", None, QtGui.QApplication.UnicodeUTF8))
        self.monitor_specid_label.setToolTip(QtGui.QApplication.translate("Frame", "Override the default monitor spectrum IDs for Ei calculation.", None, QtGui.QApplication.UnicodeUTF8))
        self.monitor_specid_label.setText(QtGui.QApplication.translate("Frame", "Monitor Spectrum IDs", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Frame", "and", None, QtGui.QApplication.UnicodeUTF8))
        self.et_range_box.setTitle(QtGui.QApplication.translate("Frame", "Energy Transfer Range (meV)", None, QtGui.QApplication.UnicodeUTF8))
        self.etr_low_label.setText(QtGui.QApplication.translate("Frame", "Low", None, QtGui.QApplication.UnicodeUTF8))
        self.etr_low_edit.setToolTip(QtGui.QApplication.translate("Frame", "Minimum energy transfer in the output file", None, QtGui.QApplication.UnicodeUTF8))
        self.etr_low_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Minimum energy transfer in the output file", None, QtGui.QApplication.UnicodeUTF8))
        self.etr_width_label.setText(QtGui.QApplication.translate("Frame", "Width", None, QtGui.QApplication.UnicodeUTF8))
        self.etr_high_label.setText(QtGui.QApplication.translate("Frame", "High", None, QtGui.QApplication.UnicodeUTF8))
        self.etr_high_edit.setToolTip(QtGui.QApplication.translate("Frame", "Maximum energy transfer in the output file", None, QtGui.QApplication.UnicodeUTF8))
        self.etr_high_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Maximum energy transfer in the output file", None, QtGui.QApplication.UnicodeUTF8))
        self.et_is_distribution_cb.setText(QtGui.QApplication.translate("Frame", "S(Phi, E) is distribution", None, QtGui.QApplication.UnicodeUTF8))
        self.hardmask_label.setText(QtGui.QApplication.translate("Frame", "Hard Mask", None, QtGui.QApplication.UnicodeUTF8))
        self.hardmask_edit.setToolTip(QtGui.QApplication.translate("Frame", "Name of the hard mask file", None, QtGui.QApplication.UnicodeUTF8))
        self.hardmask_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Name of the hard mask file", None, QtGui.QApplication.UnicodeUTF8))
        self.hardmask_browse.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.grouping_label.setText(QtGui.QApplication.translate("Frame", "Grouping", None, QtGui.QApplication.UnicodeUTF8))
        self.grouping_edit.setToolTip(QtGui.QApplication.translate("Frame", "Name of the grouping file", None, QtGui.QApplication.UnicodeUTF8))
        self.grouping_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Name of the grouping file", None, QtGui.QApplication.UnicodeUTF8))
        self.grouping_browse.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.show_workspaces_cb.setText(QtGui.QApplication.translate("Frame", "Show Intermediate Workspaces", None, QtGui.QApplication.UnicodeUTF8))
        self.savedir_label.setText(QtGui.QApplication.translate("Frame", "Save to folder", None, QtGui.QApplication.UnicodeUTF8))
        self.savedir_edit.setToolTip(QtGui.QApplication.translate("Frame", "Folder where output data is going to be saved", None, QtGui.QApplication.UnicodeUTF8))
        self.savedir_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Folder where output data is going to be saved", None, QtGui.QApplication.UnicodeUTF8))
        self.savedir_browse.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))

