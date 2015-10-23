#ifndef MANTIDQT_CUSTOMINTERFACES_REFLNEXUSMEASUREMENTSOURCETEST_H_
#define MANTIDQT_CUSTOMINTERFACES_REFLNEXUSMEASUREMENTSOURCETEST_H_

#include <cxxtest/TestSuite.h>
#include "MantidQtCustomInterfaces/ReflNexusMeasurementSource.h"
#include "MantidAPI/FileFinder.h"
#include <Poco/File.h>

using namespace MantidQt::CustomInterfaces;

class ReflNexusMeasurementSourceTest : public CxxTest::TestSuite {
public:
  // This pair of boilerplate methods prevent the suite being created statically
  // This means the constructor isn't called when running other tests
  static ReflNexusMeasurementSourceTest *createSuite() { return new ReflNexusMeasurementSourceTest(); }
  static void destroySuite( ReflNexusMeasurementSourceTest *suite ) { delete suite; }

  void xtest_obatin_via_full_path(){

      std::string path = Mantid::API::FileFinder::Instance().getFullPath("POLREF14966");
      Poco::File file(path);
      TSM_ASSERT("Test setup incorrect", !path.empty() && file.exists());

      ReflNexusMeasurementSource source;
      Measurement measurement = source.obtain(path, "made_up");
  }

  void test_obtain_via_fuzzy_path()
  {
    //ReflNexusMeasurementSource source;

    //Measurement measurement = source.obtain("made_up", "POLREF14966");

  }



};


#endif /* MANTIDQT_CUSTOMINTERFACES_REFLNEXUSMEASUREMENTSOURCETEST_H_ */
