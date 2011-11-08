
#include "MantidAPI/IMDEventWorkspace.h"
#include "MantidDataObjects/WorkspaceSingleValue.h"
#include "MantidKernel/System.h"
#include "MantidKernel/Timer.h"
#include "MantidMDAlgorithms/BinaryOperationMD.h"
#include "MantidMDEvents/MDHistoWorkspace.h"
#include "MantidTestHelpers/MDEventsTestHelper.h"
#include "MantidTestHelpers/WorkspaceCreationHelper.h"
#include "MantidTestHelpers/BinaryOperationMDTestHelper.h"
#include <cxxtest/TestSuite.h>
#include <iomanip>
#include <iostream>

using namespace Mantid;
using namespace Mantid::MDAlgorithms;
using namespace Mantid::API;
using namespace Mantid::DataObjects;
using namespace Mantid::MDEvents;

namespace BinaryOperationMDTestHelper
{

  void setUpBinaryOperationMDTestHelper()
  {
    MDHistoWorkspace_sptr histo_A;
    MDHistoWorkspace_sptr histo_B;
    IMDEventWorkspace_sptr event_A;
    IMDEventWorkspace_sptr event_B;
    WorkspaceSingleValue_sptr scalar;
    IMDWorkspace_sptr out;

    histo_A = MDEventsTestHelper::makeFakeMDHistoWorkspace(2.0, 2, 5, 10.0, 1.0);
    histo_B = MDEventsTestHelper::makeFakeMDHistoWorkspace(3.0, 2, 5, 10.0, 1.0);
    event_A = MDEventsTestHelper::makeMDEW<2>(3, 0.0, 10.0, 1);
    event_B = MDEventsTestHelper::makeMDEW<2>(3, 0.0, 10.0, 1);
    scalar = WorkspaceCreationHelper::CreateWorkspaceSingleValue(3.0);
    AnalysisDataService::Instance().addOrReplace("histo_A", histo_A);
    AnalysisDataService::Instance().addOrReplace("histo_B", histo_B);
    AnalysisDataService::Instance().addOrReplace("event_A", event_A);
    AnalysisDataService::Instance().addOrReplace("event_B", event_B);
    AnalysisDataService::Instance().addOrReplace("scalar", scalar);
  }

  /// Run a binary algorithm.
  MDHistoWorkspace_sptr doTest(std::string algoName, std::string lhs, std::string rhs, std::string outName,
      bool succeeds)
  {
    setUpBinaryOperationMDTestHelper();

    IAlgorithm* alg = FrameworkManager::Instance().createAlgorithm(algoName);
    alg->initialize();
    alg->setPropertyValue("LHSWorkspace", lhs );
    alg->setPropertyValue("RHSWorkspace", rhs );
    alg->setPropertyValue("OutputWorkspace", outName );
    alg->execute();
    if (succeeds)
    {
      if (!alg->isExecuted())
        throw std::runtime_error("Algorithm " + algoName + " did not succeed.");
      IMDWorkspace_sptr out = boost::dynamic_pointer_cast<IMDWorkspace>( AnalysisDataService::Instance().retrieve(outName));
      if (!out)
        throw std::runtime_error("Algorithm " + algoName + " did not create the output workspace.");
      return boost::dynamic_pointer_cast<MDHistoWorkspace>(out);
    }
    else
    {
      if (alg->isExecuted())
        throw std::runtime_error("Algorithm " + algoName + " did not fail as expected.");
      return (MDHistoWorkspace_sptr());
    }
  }

} // (end namespace)
