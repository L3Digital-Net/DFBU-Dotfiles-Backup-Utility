################################################################################
## Form generated from reading UI file 'main_window_complete.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow:
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1475, 1100)
        MainWindow.setMinimumSize(QSize(1000, 700))
        self.central_widget = QWidget(MainWindow)
        self.central_widget.setObjectName("central_widget")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.central_widget.sizePolicy().hasHeightForWidth()
        )
        self.central_widget.setSizePolicy(sizePolicy)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.headerBar = QWidget(self.central_widget)
        self.headerBar.setObjectName("headerBar")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.headerBar.sizePolicy().hasHeightForWidth())
        self.headerBar.setSizePolicy(sizePolicy1)
        self.headerBar.setMinimumSize(QSize(0, 48))
        self.headerBar.setMaximumSize(QSize(16777215, 48))
        self.headerBarLayout = QHBoxLayout(self.headerBar)
        self.headerBarLayout.setSpacing(12)
        self.headerBarLayout.setContentsMargins(0, 0, 0, 0)
        self.headerBarLayout.setObjectName("headerBarLayout")
        self.headerBarLayout.setContentsMargins(16, 8, 16, 8)
        self.headerIcon = QLabel(self.headerBar)
        self.headerIcon.setObjectName("headerIcon")
        self.headerIcon.setMaximumSize(QSize(24, 24))
        self.headerIcon.setPixmap(QPixmap("../resources/icons/dfbu.svg"))
        self.headerIcon.setScaledContents(True)

        self.headerBarLayout.addWidget(self.headerIcon)

        self.headerTitle = QLabel(self.headerBar)
        self.headerTitle.setObjectName("headerTitle")

        self.headerBarLayout.addWidget(self.headerTitle)

        self.headerSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.headerBarLayout.addItem(self.headerSpacer)

        self.helpButton = QPushButton(self.headerBar)
        self.helpButton.setObjectName("helpButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.helpButton.sizePolicy().hasHeightForWidth())
        self.helpButton.setSizePolicy(sizePolicy2)
        self.helpButton.setMinimumSize(QSize(32, 32))
        self.helpButton.setMaximumSize(QSize(32, 32))

        self.headerBarLayout.addWidget(self.helpButton)

        self.aboutButton = QPushButton(self.headerBar)
        self.aboutButton.setObjectName("aboutButton")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.aboutButton.sizePolicy().hasHeightForWidth())
        self.aboutButton.setSizePolicy(sizePolicy3)
        self.aboutButton.setMinimumSize(QSize(0, 32))

        self.headerBarLayout.addWidget(self.aboutButton)

        self.main_layout.addWidget(self.headerBar)

        self.mainSplitter = QSplitter(self.central_widget)
        self.mainSplitter.setObjectName("mainSplitter")
        self.mainSplitter.setOrientation(Qt.Orientation.Horizontal)
        self.mainSplitter.setChildrenCollapsible(False)
        self.tab_widget = QTabWidget(self.mainSplitter)
        self.tab_widget.setObjectName("tab_widget")
        sizePolicy4 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy4.setHorizontalStretch(65)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.tab_widget.sizePolicy().hasHeightForWidth())
        self.tab_widget.setSizePolicy(sizePolicy4)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.backupTab = QWidget()
        self.backupTab.setObjectName("backupTab")
        sizePolicy.setHeightForWidth(self.backupTab.sizePolicy().hasHeightForWidth())
        self.backupTab.setSizePolicy(sizePolicy)
        self.backupTabLayout = QVBoxLayout(self.backupTab)
        self.backupTabLayout.setSpacing(8)
        self.backupTabLayout.setContentsMargins(0, 0, 0, 0)
        self.backupTabLayout.setObjectName("backupTabLayout")
        self.backupTabLayout.setContentsMargins(12, 12, 12, 12)
        self.backupStackedWidget = QStackedWidget(self.backupTab)
        self.backupStackedWidget.setObjectName("backupStackedWidget")
        self.backupEmptyPage = QWidget()
        self.backupEmptyPage.setObjectName("backupEmptyPage")
        self.emptyStateLayout = QVBoxLayout(self.backupEmptyPage)
        self.emptyStateLayout.setSpacing(0)
        self.emptyStateLayout.setContentsMargins(0, 0, 0, 0)
        self.emptyStateLayout.setObjectName("emptyStateLayout")
        self.emptyTopSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.emptyStateLayout.addItem(self.emptyTopSpacer)

        self.emptyStateIcon = QLabel(self.backupEmptyPage)
        self.emptyStateIcon.setObjectName("emptyStateIcon")
        self.emptyStateIcon.setPixmap(QPixmap("../resources/icons/dfbu.svg"))
        self.emptyStateIcon.setScaledContents(False)
        self.emptyStateIcon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emptyStateIcon.setMaximumSize(QSize(64, 64))

        self.emptyStateLayout.addWidget(
            self.emptyStateIcon, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.emptyStateTitle = QLabel(self.backupEmptyPage)
        self.emptyStateTitle.setObjectName("emptyStateTitle")
        self.emptyStateTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.emptyStateLayout.addWidget(
            self.emptyStateTitle, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.emptyStateDescription = QLabel(self.backupEmptyPage)
        self.emptyStateDescription.setObjectName("emptyStateDescription")
        self.emptyStateDescription.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.emptyStateLayout.addWidget(
            self.emptyStateDescription, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.emptyStateAddButton = QPushButton(self.backupEmptyPage)
        self.emptyStateAddButton.setObjectName("emptyStateAddButton")
        sizePolicy5 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(
            self.emptyStateAddButton.sizePolicy().hasHeightForWidth()
        )
        self.emptyStateAddButton.setSizePolicy(sizePolicy5)

        self.emptyStateLayout.addWidget(
            self.emptyStateAddButton, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.emptyBottomSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.emptyStateLayout.addItem(self.emptyBottomSpacer)

        self.backupStackedWidget.addWidget(self.backupEmptyPage)
        self.backupContentPage = QWidget()
        self.backupContentPage.setObjectName("backupContentPage")
        self.backupContentLayout = QVBoxLayout(self.backupContentPage)
        self.backupContentLayout.setSpacing(8)
        self.backupContentLayout.setContentsMargins(0, 0, 0, 0)
        self.backupContentLayout.setObjectName("backupContentLayout")
        self.backupContentLayout.setContentsMargins(0, 0, 0, 0)
        self.backupToolbarLayout = QHBoxLayout()
        self.backupToolbarLayout.setSpacing(8)
        self.backupToolbarLayout.setObjectName("backupToolbarLayout")
        self.filterLineEdit = QLineEdit(self.backupContentPage)
        self.filterLineEdit.setObjectName("filterLineEdit")
        sizePolicy1.setHeightForWidth(
            self.filterLineEdit.sizePolicy().hasHeightForWidth()
        )
        self.filterLineEdit.setSizePolicy(sizePolicy1)
        self.filterLineEdit.setClearButtonEnabled(True)

        self.backupToolbarLayout.addWidget(self.filterLineEdit)

        self.fileGroupAddFileButton = QPushButton(self.backupContentPage)
        self.fileGroupAddFileButton.setObjectName("fileGroupAddFileButton")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(
            self.fileGroupAddFileButton.sizePolicy().hasHeightForWidth()
        )
        self.fileGroupAddFileButton.setSizePolicy(sizePolicy6)

        self.backupToolbarLayout.addWidget(self.fileGroupAddFileButton)

        self.backupContentLayout.addLayout(self.backupToolbarLayout)

        self.fileGroupFileTable = QTableWidget(self.backupContentPage)
        if self.fileGroupFileTable.columnCount() < 6:
            self.fileGroupFileTable.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.fileGroupFileTable.setObjectName("fileGroupFileTable")
        sizePolicy7 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(1)
        sizePolicy7.setHeightForWidth(
            self.fileGroupFileTable.sizePolicy().hasHeightForWidth()
        )
        self.fileGroupFileTable.setSizePolicy(sizePolicy7)
        self.fileGroupFileTable.setDragEnabled(True)
        self.fileGroupFileTable.setAlternatingRowColors(True)
        self.fileGroupFileTable.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.fileGroupFileTable.setSortingEnabled(True)

        self.backupContentLayout.addWidget(self.fileGroupFileTable)

        self.backupActionBarLayout = QHBoxLayout()
        self.backupActionBarLayout.setSpacing(8)
        self.backupActionBarLayout.setObjectName("backupActionBarLayout")
        self.fileGroupUpdateFileButton = QPushButton(self.backupContentPage)
        self.fileGroupUpdateFileButton.setObjectName("fileGroupUpdateFileButton")
        self.fileGroupUpdateFileButton.setEnabled(False)

        self.backupActionBarLayout.addWidget(self.fileGroupUpdateFileButton)

        self.fileGroupRemoveFileButton = QPushButton(self.backupContentPage)
        self.fileGroupRemoveFileButton.setObjectName("fileGroupRemoveFileButton")
        self.fileGroupRemoveFileButton.setEnabled(False)

        self.backupActionBarLayout.addWidget(self.fileGroupRemoveFileButton)

        self.fileGroupToggleEnabledButton = QPushButton(self.backupContentPage)
        self.fileGroupToggleEnabledButton.setObjectName("fileGroupToggleEnabledButton")
        self.fileGroupToggleEnabledButton.setEnabled(False)

        self.backupActionBarLayout.addWidget(self.fileGroupToggleEnabledButton)

        self.fileGroupSaveFilesButton = QPushButton(self.backupContentPage)
        self.fileGroupSaveFilesButton.setObjectName("fileGroupSaveFilesButton")
        self.fileGroupSaveFilesButton.setEnabled(False)

        self.backupActionBarLayout.addWidget(self.fileGroupSaveFilesButton)

        self.actionBarSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.backupActionBarLayout.addItem(self.actionBarSpacer)

        self.fileGroupTotalSizeLabel = QLabel(self.backupContentPage)
        self.fileGroupTotalSizeLabel.setObjectName("fileGroupTotalSizeLabel")
        sizePolicy8 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(
            self.fileGroupTotalSizeLabel.sizePolicy().hasHeightForWidth()
        )
        self.fileGroupTotalSizeLabel.setSizePolicy(sizePolicy8)

        self.backupActionBarLayout.addWidget(self.fileGroupTotalSizeLabel)

        self.backupContentLayout.addLayout(self.backupActionBarLayout)

        self.backupStackedWidget.addWidget(self.backupContentPage)

        self.backupTabLayout.addWidget(self.backupStackedWidget)

        self.backupOptionsStripLayout = QHBoxLayout()
        self.backupOptionsStripLayout.setSpacing(12)
        self.backupOptionsStripLayout.setObjectName("backupOptionsStripLayout")
        self.backupOptionsLabel = QLabel(self.backupTab)
        self.backupOptionsLabel.setObjectName("backupOptionsLabel")
        sizePolicy5.setHeightForWidth(
            self.backupOptionsLabel.sizePolicy().hasHeightForWidth()
        )
        self.backupOptionsLabel.setSizePolicy(sizePolicy5)

        self.backupOptionsStripLayout.addWidget(self.backupOptionsLabel)

        self.mirrorCheckbox = QCheckBox(self.backupTab)
        self.mirrorCheckbox.setObjectName("mirrorCheckbox")
        sizePolicy5.setHeightForWidth(
            self.mirrorCheckbox.sizePolicy().hasHeightForWidth()
        )
        self.mirrorCheckbox.setSizePolicy(sizePolicy5)
        self.mirrorCheckbox.setChecked(True)

        self.backupOptionsStripLayout.addWidget(self.mirrorCheckbox)

        self.archiveCheckbox = QCheckBox(self.backupTab)
        self.archiveCheckbox.setObjectName("archiveCheckbox")
        sizePolicy5.setHeightForWidth(
            self.archiveCheckbox.sizePolicy().hasHeightForWidth()
        )
        self.archiveCheckbox.setSizePolicy(sizePolicy5)

        self.backupOptionsStripLayout.addWidget(self.archiveCheckbox)

        self.forceBackupCheckbox = QCheckBox(self.backupTab)
        self.forceBackupCheckbox.setObjectName("forceBackupCheckbox")
        sizePolicy5.setHeightForWidth(
            self.forceBackupCheckbox.sizePolicy().hasHeightForWidth()
        )
        self.forceBackupCheckbox.setSizePolicy(sizePolicy5)
        self.forceBackupCheckbox.setChecked(False)

        self.backupOptionsStripLayout.addWidget(self.forceBackupCheckbox)

        self.optionsStripSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.backupOptionsStripLayout.addItem(self.optionsStripSpacer)

        self.startBackupButton = QPushButton(self.backupTab)
        self.startBackupButton.setObjectName("startBackupButton")
        self.startBackupButton.setEnabled(False)
        sizePolicy5.setHeightForWidth(
            self.startBackupButton.sizePolicy().hasHeightForWidth()
        )
        self.startBackupButton.setSizePolicy(sizePolicy5)

        self.backupOptionsStripLayout.addWidget(self.startBackupButton)

        self.backupTabLayout.addLayout(self.backupOptionsStripLayout)

        self.tab_widget.addTab(self.backupTab, "")
        self.configTab = QWidget()
        self.configTab.setObjectName("configTab")
        sizePolicy.setHeightForWidth(self.configTab.sizePolicy().hasHeightForWidth())
        self.configTab.setSizePolicy(sizePolicy)
        self.config_tab_layout = QVBoxLayout(self.configTab)
        self.config_tab_layout.setSpacing(8)
        self.config_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.config_tab_layout.setObjectName("config_tab_layout")
        self.config_tab_layout.setContentsMargins(12, 12, 12, 12)
        self.configScrollArea = QScrollArea(self.configTab)
        self.configScrollArea.setObjectName("configScrollArea")
        self.configScrollArea.setWidgetResizable(True)
        self.configScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.configScrollContent = QWidget()
        self.configScrollContent.setObjectName("configScrollContent")
        self.configScrollLayout = QVBoxLayout(self.configScrollContent)
        self.configScrollLayout.setSpacing(12)
        self.configScrollLayout.setContentsMargins(0, 0, 0, 0)
        self.configScrollLayout.setObjectName("configScrollLayout")
        self.backupPathsGroup = QGroupBox(self.configScrollContent)
        self.backupPathsGroup.setObjectName("backupPathsGroup")
        self.backupPathsLayout = QFormLayout(self.backupPathsGroup)
        self.backupPathsLayout.setSpacing(0)
        self.backupPathsLayout.setContentsMargins(0, 0, 0, 0)
        self.backupPathsLayout.setObjectName("backupPathsLayout")
        self.backupPathsLayout.setHorizontalSpacing(8)
        self.backupPathsLayout.setVerticalSpacing(8)
        self.mirror_path_label = QLabel(self.backupPathsGroup)
        self.mirror_path_label.setObjectName("mirror_path_label")

        self.backupPathsLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.mirror_path_label
        )

        self.mirror_path_layout = QHBoxLayout()
        self.mirror_path_layout.setSpacing(0)
        self.mirror_path_layout.setObjectName("mirror_path_layout")
        self.config_mirror_path_edit = QLineEdit(self.backupPathsGroup)
        self.config_mirror_path_edit.setObjectName("config_mirror_path_edit")

        self.mirror_path_layout.addWidget(self.config_mirror_path_edit)

        self.browse_mirror_btn = QPushButton(self.backupPathsGroup)
        self.browse_mirror_btn.setObjectName("browse_mirror_btn")
        sizePolicy5.setHeightForWidth(
            self.browse_mirror_btn.sizePolicy().hasHeightForWidth()
        )
        self.browse_mirror_btn.setSizePolicy(sizePolicy5)

        self.mirror_path_layout.addWidget(self.browse_mirror_btn)

        self.backupPathsLayout.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.mirror_path_layout
        )

        self.archivePathLabel = QLabel(self.backupPathsGroup)
        self.archivePathLabel.setObjectName("archivePathLabel")

        self.backupPathsLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.archivePathLabel
        )

        self.archivePathLayout = QHBoxLayout()
        self.archivePathLayout.setSpacing(0)
        self.archivePathLayout.setObjectName("archivePathLayout")
        self.configArchivePathEdit = QLineEdit(self.backupPathsGroup)
        self.configArchivePathEdit.setObjectName("configArchivePathEdit")

        self.archivePathLayout.addWidget(self.configArchivePathEdit)

        self.browseArchiveButton = QPushButton(self.backupPathsGroup)
        self.browseArchiveButton.setObjectName("browseArchiveButton")
        sizePolicy5.setHeightForWidth(
            self.browseArchiveButton.sizePolicy().hasHeightForWidth()
        )
        self.browseArchiveButton.setSizePolicy(sizePolicy5)

        self.archivePathLayout.addWidget(self.browseArchiveButton)

        self.backupPathsLayout.setLayout(
            1, QFormLayout.ItemRole.FieldRole, self.archivePathLayout
        )

        self.configScrollLayout.addWidget(self.backupPathsGroup)

        self.backupModesGroup = QGroupBox(self.configScrollContent)
        self.backupModesGroup.setObjectName("backupModesGroup")
        self.backupModesLayout = QGridLayout(self.backupModesGroup)
        self.backupModesLayout.setSpacing(0)
        self.backupModesLayout.setContentsMargins(0, 0, 0, 0)
        self.backupModesLayout.setObjectName("backupModesLayout")
        self.backupModesLayout.setHorizontalSpacing(16)
        self.backupModesLayout.setVerticalSpacing(8)
        self.config_mirror_checkbox = QCheckBox(self.backupModesGroup)
        self.config_mirror_checkbox.setObjectName("config_mirror_checkbox")

        self.backupModesLayout.addWidget(self.config_mirror_checkbox, 0, 0, 1, 1)

        self.config_archive_checkbox = QCheckBox(self.backupModesGroup)
        self.config_archive_checkbox.setObjectName("config_archive_checkbox")

        self.backupModesLayout.addWidget(self.config_archive_checkbox, 0, 1, 1, 1)

        self.config_hostname_checkbox = QCheckBox(self.backupModesGroup)
        self.config_hostname_checkbox.setObjectName("config_hostname_checkbox")

        self.backupModesLayout.addWidget(self.config_hostname_checkbox, 1, 0, 1, 1)

        self.config_date_checkbox = QCheckBox(self.backupModesGroup)
        self.config_date_checkbox.setObjectName("config_date_checkbox")

        self.backupModesLayout.addWidget(self.config_date_checkbox, 1, 1, 1, 1)

        self.configScrollLayout.addWidget(self.backupModesGroup)

        self.archiveOptionsGroup = QGroupBox(self.configScrollContent)
        self.archiveOptionsGroup.setObjectName("archiveOptionsGroup")
        self.archiveOptionsLayout = QFormLayout(self.archiveOptionsGroup)
        self.archiveOptionsLayout.setSpacing(0)
        self.archiveOptionsLayout.setContentsMargins(0, 0, 0, 0)
        self.archiveOptionsLayout.setObjectName("archiveOptionsLayout")
        self.archiveOptionsLayout.setHorizontalSpacing(8)
        self.archiveOptionsLayout.setVerticalSpacing(8)
        self.compressionLabel = QLabel(self.archiveOptionsGroup)
        self.compressionLabel.setObjectName("compressionLabel")

        self.archiveOptionsLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.compressionLabel
        )

        self.config_compression_spinbox = QSpinBox(self.archiveOptionsGroup)
        self.config_compression_spinbox.setObjectName("config_compression_spinbox")
        sizePolicy5.setHeightForWidth(
            self.config_compression_spinbox.sizePolicy().hasHeightForWidth()
        )
        self.config_compression_spinbox.setSizePolicy(sizePolicy5)
        self.config_compression_spinbox.setMinimum(0)
        self.config_compression_spinbox.setMaximum(9)

        self.archiveOptionsLayout.setWidget(
            0, QFormLayout.ItemRole.FieldRole, self.config_compression_spinbox
        )

        self.rotate_label = QLabel(self.archiveOptionsGroup)
        self.rotate_label.setObjectName("rotate_label")

        self.archiveOptionsLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.rotate_label
        )

        self.config_rotate_checkbox = QCheckBox(self.archiveOptionsGroup)
        self.config_rotate_checkbox.setObjectName("config_rotate_checkbox")

        self.archiveOptionsLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.config_rotate_checkbox
        )

        self.max_archives_label = QLabel(self.archiveOptionsGroup)
        self.max_archives_label.setObjectName("max_archives_label")

        self.archiveOptionsLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.max_archives_label
        )

        self.config_max_archives_spinbox = QSpinBox(self.archiveOptionsGroup)
        self.config_max_archives_spinbox.setObjectName("config_max_archives_spinbox")
        sizePolicy5.setHeightForWidth(
            self.config_max_archives_spinbox.sizePolicy().hasHeightForWidth()
        )
        self.config_max_archives_spinbox.setSizePolicy(sizePolicy5)
        self.config_max_archives_spinbox.setMinimum(1)
        self.config_max_archives_spinbox.setMaximum(100)

        self.archiveOptionsLayout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.config_max_archives_spinbox
        )

        self.configScrollLayout.addWidget(self.archiveOptionsGroup)

        self.preRestoreSafetyGroup = QGroupBox(self.configScrollContent)
        self.preRestoreSafetyGroup.setObjectName("preRestoreSafetyGroup")
        self.preRestoreSafetyLayout = QFormLayout(self.preRestoreSafetyGroup)
        self.preRestoreSafetyLayout.setSpacing(0)
        self.preRestoreSafetyLayout.setContentsMargins(0, 0, 0, 0)
        self.preRestoreSafetyLayout.setObjectName("preRestoreSafetyLayout")
        self.preRestoreSafetyLayout.setHorizontalSpacing(8)
        self.preRestoreSafetyLayout.setVerticalSpacing(8)
        self.config_pre_restore_checkbox = QCheckBox(self.preRestoreSafetyGroup)
        self.config_pre_restore_checkbox.setObjectName("config_pre_restore_checkbox")

        self.preRestoreSafetyLayout.setWidget(
            0, QFormLayout.ItemRole.SpanningRole, self.config_pre_restore_checkbox
        )

        self.maxRestoreBackupsLabel = QLabel(self.preRestoreSafetyGroup)
        self.maxRestoreBackupsLabel.setObjectName("maxRestoreBackupsLabel")

        self.preRestoreSafetyLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.maxRestoreBackupsLabel
        )

        self.config_max_restore_spinbox = QSpinBox(self.preRestoreSafetyGroup)
        self.config_max_restore_spinbox.setObjectName("config_max_restore_spinbox")
        sizePolicy5.setHeightForWidth(
            self.config_max_restore_spinbox.sizePolicy().hasHeightForWidth()
        )
        self.config_max_restore_spinbox.setSizePolicy(sizePolicy5)
        self.config_max_restore_spinbox.setMinimum(1)
        self.config_max_restore_spinbox.setMaximum(100)
        self.config_max_restore_spinbox.setValue(5)

        self.preRestoreSafetyLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.config_max_restore_spinbox
        )

        self.restoreBackupDirLabel = QLabel(self.preRestoreSafetyGroup)
        self.restoreBackupDirLabel.setObjectName("restoreBackupDirLabel")

        self.preRestoreSafetyLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.restoreBackupDirLabel
        )

        self.restoreBackupDirLayout = QHBoxLayout()
        self.restoreBackupDirLayout.setSpacing(0)
        self.restoreBackupDirLayout.setObjectName("restoreBackupDirLayout")
        self.config_restore_path_edit = QLineEdit(self.preRestoreSafetyGroup)
        self.config_restore_path_edit.setObjectName("config_restore_path_edit")

        self.restoreBackupDirLayout.addWidget(self.config_restore_path_edit)

        self.browse_restore_btn = QPushButton(self.preRestoreSafetyGroup)
        self.browse_restore_btn.setObjectName("browse_restore_btn")
        sizePolicy5.setHeightForWidth(
            self.browse_restore_btn.sizePolicy().hasHeightForWidth()
        )
        self.browse_restore_btn.setSizePolicy(sizePolicy5)

        self.restoreBackupDirLayout.addWidget(self.browse_restore_btn)

        self.preRestoreSafetyLayout.setLayout(
            2, QFormLayout.ItemRole.FieldRole, self.restoreBackupDirLayout
        )

        self.configScrollLayout.addWidget(self.preRestoreSafetyGroup)

        self.verificationGroup = QGroupBox(self.configScrollContent)
        self.verificationGroup.setObjectName("verificationGroup")
        self.verificationLayout = QVBoxLayout(self.verificationGroup)
        self.verificationLayout.setSpacing(8)
        self.verificationLayout.setContentsMargins(0, 0, 0, 0)
        self.verificationLayout.setObjectName("verificationLayout")
        self.config_verify_checkbox = QCheckBox(self.verificationGroup)
        self.config_verify_checkbox.setObjectName("config_verify_checkbox")

        self.verificationLayout.addWidget(self.config_verify_checkbox)

        self.config_hash_checkbox = QCheckBox(self.verificationGroup)
        self.config_hash_checkbox.setObjectName("config_hash_checkbox")

        self.verificationLayout.addWidget(self.config_hash_checkbox)

        self.configScrollLayout.addWidget(self.verificationGroup)

        self.sizeManagementGroup = QGroupBox(self.configScrollContent)
        self.sizeManagementGroup.setObjectName("sizeManagementGroup")
        self.sizeManagementLayout = QFormLayout(self.sizeManagementGroup)
        self.sizeManagementLayout.setSpacing(0)
        self.sizeManagementLayout.setContentsMargins(0, 0, 0, 0)
        self.sizeManagementLayout.setObjectName("sizeManagementLayout")
        self.sizeManagementLayout.setHorizontalSpacing(8)
        self.sizeManagementLayout.setVerticalSpacing(8)
        self.config_size_check_checkbox = QCheckBox(self.sizeManagementGroup)
        self.config_size_check_checkbox.setObjectName("config_size_check_checkbox")

        self.sizeManagementLayout.setWidget(
            0, QFormLayout.ItemRole.SpanningRole, self.config_size_check_checkbox
        )

        self.sizeWarningLabel = QLabel(self.sizeManagementGroup)
        self.sizeWarningLabel.setObjectName("sizeWarningLabel")

        self.sizeManagementLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.sizeWarningLabel
        )

        self.config_size_warning_spinbox = QSpinBox(self.sizeManagementGroup)
        self.config_size_warning_spinbox.setObjectName("config_size_warning_spinbox")
        sizePolicy5.setHeightForWidth(
            self.config_size_warning_spinbox.sizePolicy().hasHeightForWidth()
        )
        self.config_size_warning_spinbox.setSizePolicy(sizePolicy5)
        self.config_size_warning_spinbox.setMinimum(1)
        self.config_size_warning_spinbox.setMaximum(10000)
        self.config_size_warning_spinbox.setValue(10)

        self.sizeManagementLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.config_size_warning_spinbox
        )

        self.sizeAlertLabel = QLabel(self.sizeManagementGroup)
        self.sizeAlertLabel.setObjectName("sizeAlertLabel")

        self.sizeManagementLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.sizeAlertLabel
        )

        self.config_size_alert_spinbox = QSpinBox(self.sizeManagementGroup)
        self.config_size_alert_spinbox.setObjectName("config_size_alert_spinbox")
        sizePolicy5.setHeightForWidth(
            self.config_size_alert_spinbox.sizePolicy().hasHeightForWidth()
        )
        self.config_size_alert_spinbox.setSizePolicy(sizePolicy5)
        self.config_size_alert_spinbox.setMinimum(1)
        self.config_size_alert_spinbox.setMaximum(10000)
        self.config_size_alert_spinbox.setValue(100)

        self.sizeManagementLayout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.config_size_alert_spinbox
        )

        self.sizeCriticalLabel = QLabel(self.sizeManagementGroup)
        self.sizeCriticalLabel.setObjectName("sizeCriticalLabel")

        self.sizeManagementLayout.setWidget(
            3, QFormLayout.ItemRole.LabelRole, self.sizeCriticalLabel
        )

        self.config_size_critical_spinbox = QSpinBox(self.sizeManagementGroup)
        self.config_size_critical_spinbox.setObjectName("config_size_critical_spinbox")
        sizePolicy5.setHeightForWidth(
            self.config_size_critical_spinbox.sizePolicy().hasHeightForWidth()
        )
        self.config_size_critical_spinbox.setSizePolicy(sizePolicy5)
        self.config_size_critical_spinbox.setMinimum(1)
        self.config_size_critical_spinbox.setMaximum(100000)
        self.config_size_critical_spinbox.setValue(1024)

        self.sizeManagementLayout.setWidget(
            3, QFormLayout.ItemRole.FieldRole, self.config_size_critical_spinbox
        )

        self.configScrollLayout.addWidget(self.sizeManagementGroup)

        self.configScrollArea.setWidget(self.configScrollContent)

        self.config_tab_layout.addWidget(self.configScrollArea)

        self.configButtonLayout = QHBoxLayout()
        self.configButtonLayout.setSpacing(8)
        self.configButtonLayout.setObjectName("configButtonLayout")
        self.configButtonSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.configButtonLayout.addItem(self.configButtonSpacer)

        self.saveConfigButton = QPushButton(self.configTab)
        self.saveConfigButton.setObjectName("saveConfigButton")
        self.saveConfigButton.setEnabled(False)
        sizePolicy5.setHeightForWidth(
            self.saveConfigButton.sizePolicy().hasHeightForWidth()
        )
        self.saveConfigButton.setSizePolicy(sizePolicy5)

        self.configButtonLayout.addWidget(self.saveConfigButton)

        self.config_tab_layout.addLayout(self.configButtonLayout)

        self.tab_widget.addTab(self.configTab, "")
        self.restoreTab = QWidget()
        self.restoreTab.setObjectName("restoreTab")
        sizePolicy.setHeightForWidth(self.restoreTab.sizePolicy().hasHeightForWidth())
        self.restoreTab.setSizePolicy(sizePolicy)
        self.restore_layout = QVBoxLayout(self.restoreTab)
        self.restore_layout.setSpacing(0)
        self.restore_layout.setContentsMargins(0, 0, 0, 0)
        self.restore_layout.setObjectName("restore_layout")
        self.restore_layout.setContentsMargins(12, 12, 12, 12)
        self.restoreSourceGroup = QWidget(self.restoreTab)
        self.restoreSourceGroup.setObjectName("restoreSourceGroup")
        sizePolicy9 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum
        )
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(
            self.restoreSourceGroup.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceGroup.setSizePolicy(sizePolicy9)
        self.restore_source_layout = QVBoxLayout(self.restoreSourceGroup)
        self.restore_source_layout.setSpacing(6)
        self.restore_source_layout.setContentsMargins(0, 0, 0, 0)
        self.restore_source_layout.setObjectName("restore_source_layout")
        self.restore_source_layout.setContentsMargins(6, 0, 6, 6)
        self.restoreSourceLabelContainer = QWidget(self.restoreSourceGroup)
        self.restoreSourceLabelContainer.setObjectName("restoreSourceLabelContainer")
        sizePolicy9.setHeightForWidth(
            self.restoreSourceLabelContainer.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceLabelContainer.setSizePolicy(sizePolicy9)
        self.restoreSourceLabelLayout = QHBoxLayout(self.restoreSourceLabelContainer)
        self.restoreSourceLabelLayout.setSpacing(0)
        self.restoreSourceLabelLayout.setContentsMargins(0, 0, 0, 0)
        self.restoreSourceLabelLayout.setObjectName("restoreSourceLabelLayout")
        self.restoreSourceLabelLayout.setContentsMargins(-1, -1, -1, 0)
        self.restoreSourceLabel = QLabel(self.restoreSourceLabelContainer)
        self.restoreSourceLabel.setObjectName("restoreSourceLabel")
        sizePolicy9.setHeightForWidth(
            self.restoreSourceLabel.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceLabel.setSizePolicy(sizePolicy9)
        self.restoreSourceLabel.setMargin(6)

        self.restoreSourceLabelLayout.addWidget(self.restoreSourceLabel)

        self.restore_source_layout.addWidget(self.restoreSourceLabelContainer)

        self.restoreSourceLine = QFrame(self.restoreSourceGroup)
        self.restoreSourceLine.setObjectName("restoreSourceLine")
        sizePolicy9.setHeightForWidth(
            self.restoreSourceLine.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceLine.setSizePolicy(sizePolicy9)
        self.restoreSourceLine.setFrameShape(QFrame.Shape.HLine)
        self.restoreSourceLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.restore_source_layout.addWidget(self.restoreSourceLine)

        self.restoreSourceInfoButtonContainer = QWidget(self.restoreSourceGroup)
        self.restoreSourceInfoButtonContainer.setObjectName(
            "restoreSourceInfoButtonContainer"
        )
        sizePolicy9.setHeightForWidth(
            self.restoreSourceInfoButtonContainer.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceInfoButtonContainer.setSizePolicy(sizePolicy9)
        self.restoreSourceInfoButtonLayout = QHBoxLayout(
            self.restoreSourceInfoButtonContainer
        )
        self.restoreSourceInfoButtonLayout.setSpacing(6)
        self.restoreSourceInfoButtonLayout.setContentsMargins(0, 0, 0, 0)
        self.restoreSourceInfoButtonLayout.setObjectName(
            "restoreSourceInfoButtonLayout"
        )
        self.restoreSourceInfoButtonLayout.setContentsMargins(6, 0, 0, 0)
        self.restoreSourceInfoLabel = QLabel(self.restoreSourceInfoButtonContainer)
        self.restoreSourceInfoLabel.setObjectName("restoreSourceInfoLabel")
        sizePolicy9.setHeightForWidth(
            self.restoreSourceInfoLabel.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceInfoLabel.setSizePolicy(sizePolicy9)
        self.restoreSourceInfoLabel.setWordWrap(True)
        self.restoreSourceInfoLabel.setMargin(5)

        self.restoreSourceInfoButtonLayout.addWidget(self.restoreSourceInfoLabel)

        self.restoreSourceInfoButtonLine = QFrame(self.restoreSourceInfoButtonContainer)
        self.restoreSourceInfoButtonLine.setObjectName("restoreSourceInfoButtonLine")
        sizePolicy3.setHeightForWidth(
            self.restoreSourceInfoButtonLine.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceInfoButtonLine.setSizePolicy(sizePolicy3)
        self.restoreSourceInfoButtonLine.setMinimumSize(QSize(0, 50))
        self.restoreSourceInfoButtonLine.setFrameShape(QFrame.Shape.VLine)
        self.restoreSourceInfoButtonLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.restoreSourceInfoButtonLayout.addWidget(
            self.restoreSourceInfoButtonLine, 0, Qt.AlignmentFlag.AlignHCenter
        )

        self.restoreSourceButton = QPushButton(self.restoreSourceInfoButtonContainer)
        self.restoreSourceButton.setObjectName("restoreSourceButton")
        self.restoreSourceButton.setEnabled(False)
        sizePolicy9.setHeightForWidth(
            self.restoreSourceButton.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceButton.setSizePolicy(sizePolicy9)
        self.restoreSourceButton.setMinimumSize(QSize(0, 0))

        self.restoreSourceInfoButtonLayout.addWidget(
            self.restoreSourceButton, 0, Qt.AlignmentFlag.AlignLeft
        )

        self.restoreSourceInfoButtonLayout.setStretch(0, 20)
        self.restoreSourceInfoButtonLayout.setStretch(1, 1)
        self.restoreSourceInfoButtonLayout.setStretch(2, 20)

        self.restore_source_layout.addWidget(self.restoreSourceInfoButtonContainer)

        self.restorePathLayout = QHBoxLayout()
        self.restorePathLayout.setSpacing(0)
        self.restorePathLayout.setObjectName("restorePathLayout")
        self.restoreSourceEdit = QLineEdit(self.restoreSourceGroup)
        self.restoreSourceEdit.setObjectName("restoreSourceEdit")
        sizePolicy9.setHeightForWidth(
            self.restoreSourceEdit.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceEdit.setSizePolicy(sizePolicy9)
        self.restoreSourceEdit.setFrame(True)
        self.restoreSourceEdit.setReadOnly(True)
        self.restoreSourceEdit.setClearButtonEnabled(False)

        self.restorePathLayout.addWidget(self.restoreSourceEdit)

        self.restoreSourceBrowseButton = QPushButton(self.restoreSourceGroup)
        self.restoreSourceBrowseButton.setObjectName("restoreSourceBrowseButton")
        sizePolicy5.setHeightForWidth(
            self.restoreSourceBrowseButton.sizePolicy().hasHeightForWidth()
        )
        self.restoreSourceBrowseButton.setSizePolicy(sizePolicy5)

        self.restorePathLayout.addWidget(self.restoreSourceBrowseButton)

        self.restore_source_layout.addLayout(self.restorePathLayout)

        self.restoreSourceButtonLayout = QHBoxLayout()
        self.restoreSourceButtonLayout.setSpacing(0)
        self.restoreSourceButtonLayout.setObjectName("restoreSourceButtonLayout")

        self.restore_source_layout.addLayout(self.restoreSourceButtonLayout)

        self.restore_layout.addWidget(self.restoreSourceGroup)

        self.restorePreviewGroup = QGroupBox(self.restoreTab)
        self.restorePreviewGroup.setObjectName("restorePreviewGroup")
        self.restorePreviewGroup.setVisible(False)
        self.restorePreviewLayout = QVBoxLayout(self.restorePreviewGroup)
        self.restorePreviewLayout.setSpacing(0)
        self.restorePreviewLayout.setContentsMargins(0, 0, 0, 0)
        self.restorePreviewLayout.setObjectName("restorePreviewLayout")
        self.restorePreviewLayout.setContentsMargins(12, 12, 12, 12)
        self.restorePreviewSummaryLayout = QHBoxLayout()
        self.restorePreviewSummaryLayout.setSpacing(0)
        self.restorePreviewSummaryLayout.setObjectName("restorePreviewSummaryLayout")
        self.restorePreviewHostLabel = QLabel(self.restorePreviewGroup)
        self.restorePreviewHostLabel.setObjectName("restorePreviewHostLabel")

        self.restorePreviewSummaryLayout.addWidget(self.restorePreviewHostLabel)

        self.restorePreviewCountLabel = QLabel(self.restorePreviewGroup)
        self.restorePreviewCountLabel.setObjectName("restorePreviewCountLabel")

        self.restorePreviewSummaryLayout.addWidget(self.restorePreviewCountLabel)

        self.restorePreviewSizeLabel = QLabel(self.restorePreviewGroup)
        self.restorePreviewSizeLabel.setObjectName("restorePreviewSizeLabel")

        self.restorePreviewSummaryLayout.addWidget(self.restorePreviewSizeLabel)

        self.restorePreviewSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.restorePreviewSummaryLayout.addItem(self.restorePreviewSpacer)

        self.restorePreviewLayout.addLayout(self.restorePreviewSummaryLayout)

        self.restorePreviewTree = QTreeWidget(self.restorePreviewGroup)
        self.restorePreviewTree.setObjectName("restorePreviewTree")
        self.restorePreviewTree.setMinimumSize(QSize(0, 150))
        self.restorePreviewTree.setAlternatingRowColors(True)
        self.restorePreviewTree.setRootIsDecorated(True)

        self.restorePreviewLayout.addWidget(self.restorePreviewTree)

        self.restore_layout.addWidget(self.restorePreviewGroup)

        self.restoreInfoGroup = QWidget(self.restoreTab)
        self.restoreInfoGroup.setObjectName("restoreInfoGroup")
        sizePolicy.setHeightForWidth(
            self.restoreInfoGroup.sizePolicy().hasHeightForWidth()
        )
        self.restoreInfoGroup.setSizePolicy(sizePolicy)
        self.restore_info_layout = QVBoxLayout(self.restoreInfoGroup)
        self.restore_info_layout.setSpacing(6)
        self.restore_info_layout.setContentsMargins(0, 0, 0, 0)
        self.restore_info_layout.setObjectName("restore_info_layout")
        self.restore_info_layout.setContentsMargins(-1, -1, 0, 0)
        self.restoreInfoLabel = QLabel(self.restoreInfoGroup)
        self.restoreInfoLabel.setObjectName("restoreInfoLabel")
        sizePolicy9.setHeightForWidth(
            self.restoreInfoLabel.sizePolicy().hasHeightForWidth()
        )
        self.restoreInfoLabel.setSizePolicy(sizePolicy9)
        font = QFont()
        font.setBold(False)
        self.restoreInfoLabel.setFont(font)
        self.restoreInfoLabel.setMargin(6)

        self.restore_info_layout.addWidget(self.restoreInfoLabel)

        self.restoreInfoLine = QFrame(self.restoreInfoGroup)
        self.restoreInfoLine.setObjectName("restoreInfoLine")
        sizePolicy9.setHeightForWidth(
            self.restoreInfoLine.sizePolicy().hasHeightForWidth()
        )
        self.restoreInfoLine.setSizePolicy(sizePolicy9)
        self.restoreInfoLine.setFrameShape(QFrame.Shape.HLine)
        self.restoreInfoLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.restore_info_layout.addWidget(self.restoreInfoLine)

        self.restoreInfoText = QLabel(self.restoreInfoGroup)
        self.restoreInfoText.setObjectName("restoreInfoText")
        sizePolicy5.setHeightForWidth(
            self.restoreInfoText.sizePolicy().hasHeightForWidth()
        )
        self.restoreInfoText.setSizePolicy(sizePolicy5)
        self.restoreInfoText.setWordWrap(True)
        self.restoreInfoText.setMargin(10)
        self.restoreInfoText.setIndent(-1)

        self.restore_info_layout.addWidget(
            self.restoreInfoText, 0, Qt.AlignmentFlag.AlignTop
        )

        self.restore_layout.addWidget(self.restoreInfoGroup)

        self.tab_widget.addTab(self.restoreTab, "")
        self.mainSplitter.addWidget(self.tab_widget)
        self.logPane = QWidget(self.mainSplitter)
        self.logPane.setObjectName("logPane")
        sizePolicy10 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy10.setHorizontalStretch(35)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.logPane.sizePolicy().hasHeightForWidth())
        self.logPane.setSizePolicy(sizePolicy10)
        self.logPane.setMinimumSize(QSize(300, 0))
        self.logPaneLayout = QVBoxLayout(self.logPane)
        self.logPaneLayout.setSpacing(0)
        self.logPaneLayout.setContentsMargins(0, 0, 0, 0)
        self.logPaneLayout.setObjectName("logPaneLayout")
        self.logPaneLayout.setContentsMargins(0, 0, 0, 0)
        # Row 1: title + filter toggle buttons
        self.logHeader = QWidget(self.logPane)
        self.logHeader.setObjectName("logHeader")
        sizePolicy1.setHeightForWidth(self.logHeader.sizePolicy().hasHeightForWidth())
        self.logHeader.setSizePolicy(sizePolicy1)
        self.logHeader.setMinimumSize(QSize(0, 40))
        self.logHeaderLayout = QHBoxLayout(self.logHeader)
        self.logHeaderLayout.setSpacing(4)
        self.logHeaderLayout.setContentsMargins(12, 6, 12, 6)
        self.logHeaderLayout.setObjectName("logHeaderLayout")
        self.logPaneTitle = QLabel(self.logHeader)
        self.logPaneTitle.setObjectName("logPaneTitle")

        self.logHeaderLayout.addWidget(self.logPaneTitle)

        self.logHeaderSpacer1 = QSpacerItem(
            16, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )

        self.logHeaderLayout.addItem(self.logHeaderSpacer1)

        self.logPaneFilterAllButton = QPushButton(self.logHeader)
        self.logPaneFilterAllButton.setObjectName("logPaneFilterAllButton")
        self.logPaneFilterAllButton.setCheckable(True)
        self.logPaneFilterAllButton.setChecked(True)
        sizePolicy5.setHeightForWidth(
            self.logPaneFilterAllButton.sizePolicy().hasHeightForWidth()
        )
        self.logPaneFilterAllButton.setSizePolicy(sizePolicy5)

        self.logHeaderLayout.addWidget(self.logPaneFilterAllButton)

        self.logPaneFilterInfoButton = QPushButton(self.logHeader)
        self.logPaneFilterInfoButton.setObjectName("logPaneFilterInfoButton")
        self.logPaneFilterInfoButton.setCheckable(True)
        self.logPaneFilterInfoButton.setChecked(True)
        sizePolicy5.setHeightForWidth(
            self.logPaneFilterInfoButton.sizePolicy().hasHeightForWidth()
        )
        self.logPaneFilterInfoButton.setSizePolicy(sizePolicy5)

        self.logHeaderLayout.addWidget(self.logPaneFilterInfoButton)

        self.logPaneFilterWarningButton = QPushButton(self.logHeader)
        self.logPaneFilterWarningButton.setObjectName("logPaneFilterWarningButton")
        self.logPaneFilterWarningButton.setCheckable(True)
        self.logPaneFilterWarningButton.setChecked(True)
        sizePolicy5.setHeightForWidth(
            self.logPaneFilterWarningButton.sizePolicy().hasHeightForWidth()
        )
        self.logPaneFilterWarningButton.setSizePolicy(sizePolicy5)

        self.logHeaderLayout.addWidget(self.logPaneFilterWarningButton)

        self.logPaneFilterErrorButton = QPushButton(self.logHeader)
        self.logPaneFilterErrorButton.setObjectName("logPaneFilterErrorButton")
        self.logPaneFilterErrorButton.setCheckable(True)
        self.logPaneFilterErrorButton.setChecked(True)
        sizePolicy5.setHeightForWidth(
            self.logPaneFilterErrorButton.sizePolicy().hasHeightForWidth()
        )
        self.logPaneFilterErrorButton.setSizePolicy(sizePolicy5)

        self.logHeaderLayout.addWidget(self.logPaneFilterErrorButton)

        self.logHeaderSpacer2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.logHeaderLayout.addItem(self.logHeaderSpacer2)

        self.logPaneLayout.addWidget(self.logHeader)

        # Log output text area
        self.logPaneBox = QTextEdit(self.logPane)
        self.logPaneBox.setObjectName("logPaneBox")
        sizePolicy.setHeightForWidth(self.logPaneBox.sizePolicy().hasHeightForWidth())
        self.logPaneBox.setSizePolicy(sizePolicy)
        self.logPaneBox.setReadOnly(True)

        self.logPaneLayout.addWidget(self.logPaneBox)

        # Row 2: action buttons anchored below the log output
        self.logFooter = QWidget(self.logPane)
        self.logFooter.setObjectName("logFooter")
        sizePolicy1.setHeightForWidth(self.logFooter.sizePolicy().hasHeightForWidth())
        self.logFooter.setSizePolicy(sizePolicy1)
        self.logFooter.setMinimumSize(QSize(0, 40))
        self.logFooterLayout = QHBoxLayout(self.logFooter)
        self.logFooterLayout.setSpacing(4)
        self.logFooterLayout.setContentsMargins(12, 6, 12, 6)
        self.logFooterLayout.setObjectName("logFooterLayout")

        self.logFooterSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.logFooterLayout.addItem(self.logFooterSpacer)

        self.logPaneClearButton = QPushButton(self.logFooter)
        self.logPaneClearButton.setObjectName("logPaneClearButton")
        sizePolicy5.setHeightForWidth(
            self.logPaneClearButton.sizePolicy().hasHeightForWidth()
        )
        self.logPaneClearButton.setSizePolicy(sizePolicy5)

        self.logFooterLayout.addWidget(self.logPaneClearButton)

        self.logPaneSaveButton = QPushButton(self.logFooter)
        self.logPaneSaveButton.setObjectName("logPaneSaveButton")
        sizePolicy5.setHeightForWidth(
            self.logPaneSaveButton.sizePolicy().hasHeightForWidth()
        )
        self.logPaneSaveButton.setSizePolicy(sizePolicy5)

        self.logFooterLayout.addWidget(self.logPaneSaveButton)

        self.logPaneVerifyButton = QPushButton(self.logFooter)
        self.logPaneVerifyButton.setObjectName("logPaneVerifyButton")
        sizePolicy5.setHeightForWidth(
            self.logPaneVerifyButton.sizePolicy().hasHeightForWidth()
        )
        self.logPaneVerifyButton.setSizePolicy(sizePolicy5)

        self.logFooterLayout.addWidget(self.logPaneVerifyButton)

        self.logPaneLayout.addWidget(self.logFooter)

        self.mainSplitter.addWidget(self.logPane)

        self.main_layout.addWidget(self.mainSplitter)

        MainWindow.setCentralWidget(self.central_widget)
        self.status_bar = QStatusBar(MainWindow)
        self.status_bar.setObjectName("status_bar")
        self.progress_bar = QProgressBar(self.status_bar)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setGeometry(QRect(0, 0, 100, 30))
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        MainWindow.setStatusBar(self.status_bar)

        self.retranslateUi(MainWindow)

        self.tab_widget.setCurrentIndex(0)
        self.backupStackedWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "DFBU GUI", None)
        )
        self.headerBar.setStyleSheet(
            QCoreApplication.translate(
                "MainWindow",
                "background-color: #F8FAFC; border-bottom: 1px solid #E2E8F0;",
                None,
            )
        )
        self.headerTitle.setStyleSheet(
            QCoreApplication.translate(
                "MainWindow",
                "font-size: 15px; font-weight: bold; color: #1E293B; border: none; background: transparent;",
                None,
            )
        )
        self.headerTitle.setText(
            QCoreApplication.translate(
                "MainWindow", "DFBU - Dotfiles Backup Utility", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.helpButton.setToolTip(
            QCoreApplication.translate("MainWindow", "Help (F1)", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.helpButton.setText(QCoreApplication.translate("MainWindow", "?", None))
        self.helpButton.setStyleSheet(
            QCoreApplication.translate(
                "MainWindow", "font-weight: bold; font-size: 14px;", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.aboutButton.setToolTip(
            QCoreApplication.translate("MainWindow", "About DFBU", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.aboutButton.setText(
            QCoreApplication.translate("MainWindow", "About", None)
        )
        self.emptyStateIcon.setText("")
        self.emptyStateTitle.setText(
            QCoreApplication.translate("MainWindow", "No dotfiles configured yet", None)
        )
        self.emptyStateTitle.setStyleSheet(
            QCoreApplication.translate(
                "MainWindow",
                "font-size: 16px; font-weight: bold; color: #1E293B;",
                None,
            )
        )
        self.emptyStateDescription.setText(
            QCoreApplication.translate(
                "MainWindow",
                'Click "Add" to create your first dotfile entry,\n'
                "or load an existing configuration.",
                None,
            )
        )
        self.emptyStateDescription.setStyleSheet(
            QCoreApplication.translate("MainWindow", "color: #64748B;", None)
        )
        self.emptyStateAddButton.setText(
            QCoreApplication.translate("MainWindow", "+ Add Dotfile", None)
        )
        self.filterLineEdit.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "Filter by name, tags, or path...", None
            )
        )
        self.fileGroupAddFileButton.setText(
            QCoreApplication.translate("MainWindow", "New", None)
        )
        ___qtablewidgetitem = self.fileGroupFileTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MainWindow", "Included", None)
        )
        ___qtablewidgetitem1 = self.fileGroupFileTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        ___qtablewidgetitem2 = self.fileGroupFileTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("MainWindow", "Application", None)
        )
        ___qtablewidgetitem3 = self.fileGroupFileTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("MainWindow", "Tags", None)
        )
        ___qtablewidgetitem4 = self.fileGroupFileTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate("MainWindow", "Size", None)
        )
        ___qtablewidgetitem5 = self.fileGroupFileTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate("MainWindow", "Path", None)
        )
        self.fileGroupUpdateFileButton.setText(
            QCoreApplication.translate("MainWindow", "Update", None)
        )
        self.fileGroupRemoveFileButton.setText(
            QCoreApplication.translate("MainWindow", "Remove", None)
        )
        self.fileGroupToggleEnabledButton.setText(
            QCoreApplication.translate("MainWindow", "Toggle Active", None)
        )
        # if QT_CONFIG(tooltip)
        self.fileGroupSaveFilesButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Save enable/disable changes to the configuration file (not the backup itself)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.fileGroupSaveFilesButton.setText(
            QCoreApplication.translate("MainWindow", "Save Config", None)
        )
        self.fileGroupTotalSizeLabel.setStyleSheet(
            QCoreApplication.translate(
                "MainWindow", "font-weight: bold; padding: 5px;", None
            )
        )
        self.fileGroupTotalSizeLabel.setText(
            QCoreApplication.translate(
                "MainWindow", "Total Size (enabled): Calculating...", None
            )
        )
        self.backupOptionsLabel.setStyleSheet(
            QCoreApplication.translate("MainWindow", "font-weight: bold;", None)
        )
        self.backupOptionsLabel.setText(
            QCoreApplication.translate("MainWindow", "Backup Options:", None)
        )
        self.mirrorCheckbox.setText(
            QCoreApplication.translate("MainWindow", "Mirror", None)
        )
        self.archiveCheckbox.setText(
            QCoreApplication.translate("MainWindow", "Archive", None)
        )
        # if QT_CONFIG(tooltip)
        self.forceBackupCheckbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "When checked, all files will be copied even if unchanged (slower but ensures complete backup)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.forceBackupCheckbox.setText(
            QCoreApplication.translate("MainWindow", "Force Full Backup", None)
        )
        # if QT_CONFIG(tooltip)
        self.startBackupButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Start backup operation to copy enabled dotfiles to backup locations",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.startBackupButton.setText(
            QCoreApplication.translate("MainWindow", "Start Backup", None)
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.backupTab),
            QCoreApplication.translate("MainWindow", "Backup", None),
        )
        self.backupPathsGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Backup Paths", None)
        )
        self.mirror_path_label.setText(
            QCoreApplication.translate("MainWindow", "Mirror Directory:", None)
        )
        self.config_mirror_path_edit.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Mirror backup directory", None)
        )
        self.browse_mirror_btn.setText(
            QCoreApplication.translate("MainWindow", "Browse...", None)
        )
        self.archivePathLabel.setText(
            QCoreApplication.translate("MainWindow", "Archive Directory:", None)
        )
        self.configArchivePathEdit.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Archive backup directory", None)
        )
        self.browseArchiveButton.setText(
            QCoreApplication.translate("MainWindow", "Browse...", None)
        )
        self.backupModesGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Backup Modes", None)
        )
        self.config_mirror_checkbox.setText(
            QCoreApplication.translate(
                "MainWindow", "Enable mirror backup (uncompressed)", None
            )
        )
        self.config_archive_checkbox.setText(
            QCoreApplication.translate(
                "MainWindow", "Enable archive backup (compressed)", None
            )
        )
        self.config_hostname_checkbox.setText(
            QCoreApplication.translate(
                "MainWindow", "Include hostname in backup path", None
            )
        )
        self.config_date_checkbox.setText(
            QCoreApplication.translate(
                "MainWindow", "Include date in backup path", None
            )
        )
        self.archiveOptionsGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Archive Options", None)
        )
        self.compressionLabel.setText(
            QCoreApplication.translate("MainWindow", "Compression Level:", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_compression_spinbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "0 = no compression, 9 = maximum compression", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.rotate_label.setText(
            QCoreApplication.translate("MainWindow", "Rotate Archives:", None)
        )
        self.config_rotate_checkbox.setText(
            QCoreApplication.translate("MainWindow", "Enable archive rotation", None)
        )
        self.max_archives_label.setText(
            QCoreApplication.translate("MainWindow", "Max Archives:", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_max_archives_spinbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Maximum number of archives to keep", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.preRestoreSafetyGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Pre-Restore Safety", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_pre_restore_checkbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Backup existing files before restore operations", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.config_pre_restore_checkbox.setText(
            QCoreApplication.translate(
                "MainWindow", "Backup files before overwriting", None
            )
        )
        self.maxRestoreBackupsLabel.setText(
            QCoreApplication.translate("MainWindow", "Max Restore Backups:", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_max_restore_spinbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Maximum number of pre-restore backups to keep", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.restoreBackupDirLabel.setText(
            QCoreApplication.translate("MainWindow", "Restore Backup Dir:", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_restore_path_edit.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Directory to store pre-restore backups", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.config_restore_path_edit.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "~/.local/share/dfbu/restore-backups", None
            )
        )
        self.browse_restore_btn.setText(
            QCoreApplication.translate("MainWindow", "Browse...", None)
        )
        self.verificationGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Verification", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_verify_checkbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Run verification after each backup operation", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.config_verify_checkbox.setText(
            QCoreApplication.translate(
                "MainWindow", "Automatically verify backup integrity", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.config_hash_checkbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Compare file contents using cryptographic hash instead of size only",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.config_hash_checkbox.setText(
            QCoreApplication.translate(
                "MainWindow", "Use SHA-256 hash comparison (slower)", None
            )
        )
        self.sizeManagementGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Size Management", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_size_check_checkbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Show warnings for large files before starting backup",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.config_size_check_checkbox.setText(
            QCoreApplication.translate(
                "MainWindow", "Analyze file sizes before backup", None
            )
        )
        self.sizeWarningLabel.setText(
            QCoreApplication.translate("MainWindow", "Warning Threshold (MB):", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_size_warning_spinbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Files larger than this show a warning (yellow)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.sizeAlertLabel.setText(
            QCoreApplication.translate("MainWindow", "Alert Threshold (MB):", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_size_alert_spinbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Files larger than this show an alert (orange)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.sizeCriticalLabel.setText(
            QCoreApplication.translate("MainWindow", "Critical Threshold (MB):", None)
        )
        # if QT_CONFIG(tooltip)
        self.config_size_critical_spinbox.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Files larger than this show critical warning (red)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.saveConfigButton.setText(
            QCoreApplication.translate("MainWindow", "Save Configuration", None)
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.configTab),
            QCoreApplication.translate("MainWindow", "Configuration", None),
        )
        self.restoreSourceLabel.setText(
            QCoreApplication.translate("MainWindow", "Restore Source Path", None)
        )
        self.restoreSourceInfoLabel.setText(
            QCoreApplication.translate(
                "MainWindow",
                "Select the backup directory containing the hostname folder.\n"
                "Example: ~/GitHub/dotfiles/ (containing hostname subdirectory)",
                None,
            )
        )
        self.restoreSourceButton.setText(
            QCoreApplication.translate("MainWindow", "Start Restore", None)
        )
        self.restoreSourceEdit.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "Path to backup directory with hostname", None
            )
        )
        self.restoreSourceBrowseButton.setText(
            QCoreApplication.translate("MainWindow", "Browse...", None)
        )
        self.restorePreviewGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Backup Preview", None)
        )
        self.restorePreviewHostLabel.setText(
            QCoreApplication.translate("MainWindow", "Hostname: \u2014", None)
        )
        self.restorePreviewCountLabel.setText(
            QCoreApplication.translate("MainWindow", "Files: \u2014", None)
        )
        self.restorePreviewSizeLabel.setText(
            QCoreApplication.translate("MainWindow", "Size: \u2014", None)
        )
        ___qtreewidgetitem = self.restorePreviewTree.headerItem()
        ___qtreewidgetitem.setText(
            2, QCoreApplication.translate("MainWindow", "Size", None)
        )
        ___qtreewidgetitem.setText(
            1, QCoreApplication.translate("MainWindow", "Files", None)
        )
        ___qtreewidgetitem.setText(
            0, QCoreApplication.translate("MainWindow", "Application", None)
        )
        self.restoreInfoLabel.setText(
            QCoreApplication.translate("MainWindow", "Restore Information", None)
        )
        self.restoreInfoText.setText(
            QCoreApplication.translate(
                "MainWindow",
                "Restore will:\n"
                "\u2022 Discover all files in the selected backup directory\n"
                "\u2022 Reconstruct original file paths based on backup structure\n"
                "\u2022 Copy files back to their original locations\n"
                "\u2022 Create necessary parent directories\n"
                "\u2022 Preserve file metadata and permissions\n"
                "\n"
                "WARNING: This will overwrite existing files at destination paths.",
                None,
            )
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.restoreTab),
            QCoreApplication.translate("MainWindow", "Restore", None),
        )
        self.logHeader.setStyleSheet(
            QCoreApplication.translate(
                "MainWindow",
                "background-color: #F8FAFC; border-bottom: 1px solid #E2E8F0;",
                None,
            )
        )
        self.logPaneTitle.setStyleSheet(
            QCoreApplication.translate(
                "MainWindow",
                "font-weight: bold; font-size: 13px; color: #1E293B; border: none; background: transparent;",
                None,
            )
        )
        self.logPaneTitle.setText(
            QCoreApplication.translate("MainWindow", "Operation Log", None)
        )
        self.logPaneFilterAllButton.setText(
            QCoreApplication.translate("MainWindow", "All", None)
        )
        self.logPaneFilterInfoButton.setText(
            QCoreApplication.translate("MainWindow", "Info", None)
        )
        self.logPaneFilterWarningButton.setText(
            QCoreApplication.translate("MainWindow", "Warn", None)
        )
        self.logPaneFilterErrorButton.setText(
            QCoreApplication.translate("MainWindow", "Errors", None)
        )
        self.logPaneClearButton.setText(
            QCoreApplication.translate("MainWindow", "Clear", None)
        )
        self.logPaneSaveButton.setText(
            QCoreApplication.translate("MainWindow", "Save", None)
        )
        self.logPaneVerifyButton.setText(
            QCoreApplication.translate("MainWindow", "Verify", None)
        )
        # if QT_CONFIG(tooltip)
        self.logPaneVerifyButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Verify integrity of the last backup operation", None
            )
        )


# endif // QT_CONFIG(tooltip)
# retranslateUi
