#ifndef MANTID_HISTOGRAMDATA_POINTSTEST_H_
#define MANTID_HISTOGRAMDATA_POINTSTEST_H_

#include <cxxtest/TestSuite.h>

#include "MantidHistogramData/Points.h"
#include "MantidHistogramData/BinEdges.h"

using namespace Mantid;
using namespace HistogramData;

class PointsTest : public CxxTest::TestSuite {
public:
  // This pair of boilerplate methods prevent the suite being created statically
  // This means the constructor isn't called when running other tests
  static PointsTest *createSuite() { return new PointsTest(); }
  static void destroySuite(PointsTest *suite) { delete suite; }

  void test_has_correct_mixins() {
    Points data;
// AppleClang gives warning if the result is unused.
#if __clang__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-value"
#endif
    TS_ASSERT_THROWS_NOTHING(
        (dynamic_cast<detail::VectorOf<Points, HistogramX> &>(data)));
    TS_ASSERT_THROWS_NOTHING(dynamic_cast<detail::Iterable<Points> &>(data));
    TS_ASSERT_THROWS_NOTHING(dynamic_cast<detail::Offsetable<Points> &>(data));
    TS_ASSERT_THROWS_NOTHING(dynamic_cast<detail::Scalable<Points> &>(data));
#if __clang__
#pragma clang diagnostic pop
#endif
  }

  void test_construct_default() {
    const Points points{};
    TS_ASSERT(!points);
  }

  void test_construct_from_null_BinEdges() {
    const BinEdges edges{};
    const Points points(edges);
    TS_ASSERT(!points);
  }

  void test_construct_from_empty_BinEdges() {
    const BinEdges edges(0);
    const Points points(edges);
    TS_ASSERT_EQUALS(points.size(), 0);
  }

  void test_construct_from_invalid_BinEdges() {
    const BinEdges edges(1);
    TS_ASSERT_THROWS(Points points(edges), std::logic_error);
  }

  void test_construct_from_BinEdges() {
    const BinEdges edges{1.0, 3.0, 7.0, 15.0};
    const Points points(edges);
    TS_ASSERT_EQUALS(points.size(), 3);
    TS_ASSERT_DELTA(points[0], 2.0, 1e-14);
    TS_ASSERT_DELTA(points[1], 5.0, 1e-14);
    TS_ASSERT_DELTA(points[2], 11.0, 1e-14);
  }
};

#endif /* MANTID_HISTOGRAMDATA_POINTSTEST_H_ */
