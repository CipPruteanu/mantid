#include "MantidQtMantidWidgets/InstrumentView/OpenGLError.h"
#include <sstream>
#include "MantidKernel/Logger.h"
#include "MantidGeometry/Rendering/OpenGL_Headers.h"

namespace {
// Initialize logger
Mantid::Kernel::Logger g_log("OpenGL");
}

namespace MantidQt {
namespace MantidWidgets {
/**
* Check for a GL error and throw OpenGLError if found
* @param funName :: Name of the function where checkGLError is called.
*   The message returned be what() method of the exception has the form:
*   "OpenGL error detected in " + funName + ": " + error_description
*/
bool OpenGLError::check(const std::string &funName) {
  GLuint err = glGetError();
  if (err) {
    std::ostringstream ostr;
    ostr << "OpenGL error detected in " << funName << ": "
         << gluErrorString(err);
    g_log.error() << ostr.str() << '\n';
    // throw OpenGLError(ostr.str());
    return true;
  }
  return false;
}

std::ostream &OpenGLError::log() { return g_log.error(); }

std::ostream &OpenGLError::logDebug() { return g_log.debug(); }

} // MantidWidgets
} // MantidQt
