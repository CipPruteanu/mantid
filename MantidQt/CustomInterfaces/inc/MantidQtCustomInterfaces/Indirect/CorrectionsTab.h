#ifndef MANTIDQTCUSTOMINTERFACESIDA_CORRECTIONSTAB_H_
#define MANTIDQTCUSTOMINTERFACESIDA_CORRECTIONSTAB_H_

#include "MantidAPI/AlgorithmManager.h"
#include "MantidAPI/MatrixWorkspace_fwd.h"
#include "IndirectTab.h"

class QwtPlotCurve;
class QwtPlot;
class QSettings;
class QString;

namespace MantidQt {
namespace MantidWidgets {
class RangeSelector;
}
}

// Suppress a warning coming out of code that isn't ours
#if defined(__INTEL_COMPILER)
#pragma warning disable 1125
#elif defined(__GNUC__)
#if (__GNUC__ >= 4 && __GNUC_MINOR__ >= 6)
#pragma GCC diagnostic push
#endif
#pragma GCC diagnostic ignored "-Woverloaded-virtual"
#endif
#include "qttreepropertybrowser.h"
#include "qtpropertymanager.h"
#include "qteditorfactory.h"
#include "DoubleEditorFactory.h"
#if defined(__INTEL_COMPILER)
#pragma warning enable 1125
#elif defined(__GNUC__)
#if (__GNUC__ >= 4 && __GNUC_MINOR__ >= 6)
#pragma GCC diagnostic pop
#endif
#endif

namespace MantidQt {
namespace CustomInterfaces {
class DLLExport CorrectionsTab : public IndirectTab {
  Q_OBJECT

public:
  /// Constructor
  CorrectionsTab(QWidget *parent = 0);

  /// Loads the tab's settings.
  void loadTabSettings(const QSettings &settings);

protected:
  /// Function to run a string as python code
  void runPythonScript(const QString &pyInput);
  /// Check the binning between two workspaces match
  bool
  checkWorkspaceBinningMatches(Mantid::API::MatrixWorkspace_const_sptr left,
                               Mantid::API::MatrixWorkspace_const_sptr right);
  /// Adds a unit conversion step to the algorithm queue
  std::string addConvertUnitsStep(Mantid::API::MatrixWorkspace_sptr ws,
                                  const std::string &unitID,
                                  const std::string &suffix = "UNIT",
                                  std::string eMode = "");

  /// DoubleEditorFactory
  DoubleEditorFactory *m_dblEdFac;
  /// QtCheckBoxFactory
  QtCheckBoxFactory *m_blnEdFac;

protected slots:
  /// Slot that can be called when a user eidts an input.
  void inputChanged();

private:
  /// Overidden by child class.
  void setup() override = 0;
  /// Overidden by child class.
  void run() override = 0;
  /// Overidden by child class.
  bool validate() override = 0;

  /// Overidden by child class.
  virtual void loadSettings(const QSettings &settings) = 0;
};
} // namespace CustomInterfaces
} // namespace MantidQt

#endif /* MANTIDQTCUSTOMINTERFACESIDA_CORRECTIONSTAB_H_ */
