#ifndef MANTID_ALGORITHMS_RebinByPulseTimesTEST_H_
#define MANTID_ALGORITHMS_RebinByPulseTimesTEST_H_


#include <cxxtest/TestSuite.h>
#include "RebinByTimeBaseTest.h"
#include "MantidAlgorithms/RebinByPulseTimes.h"

using Mantid::Algorithms::RebinByPulseTimes;


//=====================================================================================
// Functional Tests
//=====================================================================================
typedef RebinByTimeBaseTest<RebinByPulseTimes> Super;
class RebinByPulseTimesTest : public CxxTest::TestSuite, public Super
{


public:
  // This pair of boilerplate methods prevent the suite being created statically
  // This means the constructor isn't called when running other tests
  static RebinByPulseTimesTest *createSuite() { return new RebinByPulseTimesTest(); }
  static void destroySuite( RebinByPulseTimesTest *suite ) { delete suite; }


  void test_Init()
  {
    Super::test_Init();
  }

  void test_not_a_event_workspace_throws()
  {
    Super::test_not_a_event_workspace_throws();
  }

  void do_test_bad_step_throws(const double& badStep)
  {
    RebinByTimeBaseTest::do_test_bad_step_throws(badStep);
  }

  void test_zero_step_throws()
  {
    RebinByTimeBaseTest::test_zero_step_throws();
  }

  void test_less_than_zero_step_throws()
  {
    RebinByTimeBaseTest::test_less_than_zero_step_throws();
  }

  /*
  Test that the input workspace must be an event workspace, other types of matrix workspace will not do.
  */
  void test_input_workspace2D_throws()
  {
    RebinByTimeBaseTest::test_input_workspace2D_throws();
  }

    /**
    Test setup description.

    Bins set up with no offset and a spacing of 1e9 according to the rebin parameters.
    The events in the workspace are created such that they sit in the middle of each bin. They are uniformly distributed from 0.5e9 to 19.5e9, so binning should occur as follows:

      0      1e9   2e9   3e9   4e9   5e9 .... 20e9
      |     |     |     |     |                 X array
        ^      ^      ^     ^
        |      |      |     |                   TOF pulse times
        0.5e9  1.5e9  2.5e9 3.5e9 ... 19e9

        so Y array should work out to be [1, 1, 1, ...] counts.
    */
  void test_execute_with_original_binning()
  {
    RebinByTimeBaseTest::test_execute_with_original_binning();
  }

    /**
    Test setup description.

    Bins set up with no offset and a spacing of 2*e9 according to the rebin parameters.
    The events in the workspace are created such that they sit in the middle of each bin. They are uniformly distributed from 0.5e9 to 19.5e9, so binning should occur as follows:

      0          2e9            4e9   .... 20e9
      |           |              |                 X array
        ^      ^      ^     ^
        |      |      |     |                      TOF pulse times
        0.5e9  1.5e9  2.5e9 3.5e9 ... 19e9

        so Y array should work out to be [2, 2, 2, ...] counts.
    */
  void test_execute_with_double_sized_bins_binning()
  {
    RebinByTimeBaseTest::test_execute_with_double_sized_bins_binning();
  }

    /**
    Test setup description.

    Bins set up with no offset and a spacing of 4*e9 according to the rebin parameters.
    The events in the workspace are created such that they sit in the middle of each bin. They are uniformly distributed from 0.5e9 to 19.5e9, so binning should occur as follows:

      0                     4e9   .... 20e9
      |                        |                 X array
        ^      ^      ^     ^
        |      |      |     |                      TOF pulse times
        0.5e9  1.5e9  2.5e9 3.5e9 ... 19e9

        so Y array should work out to be [4, 4, 4, ...] counts.
    */
  void test_execute_with_quadruple_sized_bins_binning()
  {
    RebinByTimeBaseTest::test_execute_with_quadruple_sized_bins_binning();
  }

  void test_execute_with_multiple_spectra()
  {
    RebinByTimeBaseTest::test_execute_with_multiple_spectra();
  }

  void test_execute_with_xmin_larger_than_xmax_throws()
  {
    RebinByTimeBaseTest::test_execute_with_xmin_larger_than_xmax_throws();
  }

  void test_calculate_xmin_xmax()
  {
    RebinByTimeBaseTest::test_calculate_xmin_xmax();
  }


  /**
    Test setup description.
    
    Bins set up with 1e9 offset according to the rebin parameters.
    But the events in the workspace are created without the offset, they have uniformly distributed pulse times from 0.5e9 to 3.5e9, so binning should occur as follows:

            1e9   2e9   3e9   4e9   5e9
            |     |     |     |     |         X array
        ^      ^      ^     ^
        |      |      |     |           TOF pulse times
        0.5e9  1.5e9  2.5e9 3.5e9

        so Y array should work out to be [1, 1, 1, 0] counts.
    */
  void test_calculate_non_zero_offset()
  {
    RebinByTimeBaseTest::test_calculate_non_zero_offset();

  }
};

//=====================================================================================
// Performance Tests
//=====================================================================================
class RebinByPulseTimesTestPerformance : public CxxTest::TestSuite, public RebinByTimeBaseTestPerformance<RebinByPulseTimes>
{

public:
  static RebinByPulseTimesTestPerformance *createSuite() { return new RebinByPulseTimesTestPerformance(); }
  static void destroySuite( RebinByPulseTimesTestPerformance *suite ) { delete suite; }

  RebinByPulseTimesTestPerformance()
  {
  }

  void setUp()
  {
    RebinByTimeBaseTestPerformance::setUp();
  }

  void testExecution()
  {
    RebinByTimeBaseTestPerformance::testExecution();
  }
};


#endif /* MANTID_ALGORITHMS_RebinByPulseTimesTEST_H_ */
