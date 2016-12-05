#ifndef MANTID_CUSTOMINTERFACES_IPROJECTSAVEVIEW_H
#define MANTID_CUSTOMINTERFACES_IPROJECTSAVEVIEW_H

#include "MantidQtAPI/IProjectSerialisable.h"
#include "ui_ProjectSave.h"

#include <QWidget>
#include <QMainWindow>
#include <string>
#include <vector>
#include <set>

namespace MantidQt {
namespace MantidWidgets {

class ProjectSavePresenter;
struct WindowInfo;
struct WorkspaceInfo;

/** @class IProjectSaveView

IProjectSaveView is the interface for defining the functions that the project
save view needs to implement.

Copyright &copy; 2011-14 ISIS Rutherford Appleton Laboratory, NScD Oak Ridge
National Laboratory & European Spallation Source

This file is part of Mantid.

Mantid is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

Mantid is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

File change history is stored at: <https://github.com/mantidproject/mantid>.
Code Documentation is available at: <http://doxygen.mantidproject.org>
*/
class IProjectSaveView {
public:
  virtual std::vector<MantidQt::API::IProjectSerialisable*> getWindows() = 0;
  virtual std::vector<std::string> getCheckedWorkspaceNames() = 0;
  virtual std::vector<std::string> getUncheckedWorkspaceNames() = 0;
  virtual QString getProjectPath() = 0;
  virtual void setProjectPath(const QString& path) = 0;
  virtual void updateWorkspacesList(const std::vector<WorkspaceInfo>& workspaces) = 0;
  virtual void updateIncludedWindowsList(const std::vector<WindowInfo>& windows) = 0;
  virtual void updateExcludedWindowsList(const std::vector<WindowInfo>& windows) = 0;
  virtual void removeFromIncludedWindowsList(const std::vector<std::string>& windows) = 0;
  virtual void removeFromExcludedWindowsList(const std::vector<std::string>& windows) = 0;
};
}
}
#endif /* MANTID_CUSTOMINTERFACES_IPROJECTSAVEVIEW_H */
