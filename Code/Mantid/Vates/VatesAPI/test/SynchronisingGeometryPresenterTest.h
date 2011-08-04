#ifndef SYNCHRONISING_GEOMETRY_PRESENTER_TEST_H_
#define SYNCHRONISING_GEOMETRY_PRESENTER_TEST_H_ 

#include <cxxtest/TestSuite.h>
#include "MantidVatesAPI/SynchronisingGeometryPresenter.h"
#include "MantidVatesAPI/GeometryView.h"
#include "MantidVatesAPI/DimensionView.h"
#include "MantidGeometry/MDGeometry/MDGeometryXMLParser.h"
#include "MantidVatesAPI/DimensionPresenter.h"

#include "gtest/gtest.h"
#include "gmock/gmock.h"

using namespace testing;
using namespace Mantid::VATES;
using namespace Mantid::Geometry;

class SynchronisingGeometryPresenterTest: public CxxTest::TestSuite
{
  

private:

static std::string constructXML(std::string nbinsA, std::string nbinsB, std::string nbinsC, std::string nbinsD, std::string nbinsE)
{
    return std::string("<?xml version=\"1.0\" encoding=\"utf-8\"?>") +
  "<DimensionSet>" +
    "<Dimension ID=\"en\">" +
      "<Name>Energy</Name>" +
      "<UpperBounds>150</UpperBounds>" +
      "<LowerBounds>0</LowerBounds>" +
      "<NumberOfBins>" + nbinsA + "</NumberOfBins>" +
    "</Dimension>" +
    "<Dimension ID=\"qx\">" +
      "<Name>Qx</Name>" +
      "<UpperBounds>5</UpperBounds>" +
      "<LowerBounds>-1.5</LowerBounds>" +
      "<NumberOfBins>" + nbinsB + "</NumberOfBins>" +
    "</Dimension>" +
    "<Dimension ID=\"qy\">" +
      "<Name>Qy</Name>" +
      "<UpperBounds>6.6</UpperBounds>" +
      "<LowerBounds>-6.6</LowerBounds>" +
      "<NumberOfBins>" + nbinsC + "</NumberOfBins>" +
    "</Dimension>" +
    "<Dimension ID=\"qz\">" +
      "<Name>Qz</Name>" +
      "<UpperBounds>6.6</UpperBounds>" +
      "<LowerBounds>-6.6</LowerBounds>" +
      "<NumberOfBins>" + nbinsD + "</NumberOfBins>" +
    "</Dimension>" +
    "<Dimension ID=\"other\">" +
      "<Name>Other</Name>" +
      "<UpperBounds>6.6</UpperBounds>" +
      "<LowerBounds>-6.6</LowerBounds>" +
      "<NumberOfBins>" + nbinsE + "</NumberOfBins>" +
    "</Dimension>" +
    "<XDimension>" +
      "<RefDimensionId>qx</RefDimensionId>" +
    "</XDimension>" +
    "<YDimension>" +
      "<RefDimensionId>qy</RefDimensionId>" +
    "</YDimension>" +
    "<ZDimension>" +
      "<RefDimensionId>qz</RefDimensionId>" +
    "</ZDimension>" +
    "<TDimension>" +
      "<RefDimensionId>en</RefDimensionId>" +
    "</TDimension>" +
  "</DimensionSet>";
  }

  static std::string constructXML()
  {
    return constructXML("1", "5", "5", "5", "1");
  }

  class MockGeometryView : public GeometryView
  {
  public:
    MOCK_METHOD1(addDimensionView, void(DimensionView*));
    MOCK_CONST_METHOD0(getGeometryXMLString, std::string());
    MOCK_METHOD0(getDimensionViewFactory, const DimensionViewFactory&());
    MOCK_METHOD0(raiseModified, void());
    MOCK_METHOD0(raiseNoClipping, void());
    ~MockGeometryView(){}
  };

  class MockDimensionViewFactory : public DimensionViewFactory
  {
  public:
    MOCK_CONST_METHOD0( create, DimensionView*());
    ~MockDimensionViewFactory(){}
  };

  class MockDimensionView : public DimensionView
  {
  public:
    MOCK_METHOD0(configureStrongly, void());
    MOCK_METHOD0(configureWeakly, void());
    MOCK_METHOD1(showAsNotIntegrated, void(VecIMDDimension_sptr));
    MOCK_METHOD0(showAsIntegrated, void());
    MOCK_METHOD1(accept, void(DimensionPresenter*));
    MOCK_CONST_METHOD0(getVisDimensionName, std::string());
    MOCK_CONST_METHOD0(getMinimum, double());
    MOCK_CONST_METHOD0(getMaximum, double());
    MOCK_CONST_METHOD0(getNBins, unsigned int());
    MOCK_CONST_METHOD0(getSelectedIndex, unsigned int());
    MOCK_CONST_METHOD0(getIsIntegrated, bool());
    ~MockDimensionView(){};
  };

  class ExposedSynchronisingGeometryPresenter : public Mantid::VATES::SynchronisingGeometryPresenter
  {
  public:
    ExposedSynchronisingGeometryPresenter(Mantid::Geometry::MDGeometryXMLParser& source) : Mantid::VATES::SynchronisingGeometryPresenter(source) {}
    Mantid::VATES::DimPresenter_sptr getDimensionPresenter(unsigned int index)
    {
      return m_dimPresenters[index];
    }
  
    void dimensionCollapsed(DimensionPresenter* pDimensionPresenter)
    {
      return Mantid::VATES::SynchronisingGeometryPresenter::dimensionCollapsed(pDimensionPresenter);
    }
  };

public:

  void testConstruct()
  {
    MDGeometryXMLParser parser(constructXML());
    parser.execute();
    SynchronisingGeometryPresenter presenter(parser); 
    TSM_ASSERT_EQUALS("Wrong number of nonintegrated dimensions", 3, presenter.getNonIntegratedDimensions().size());
  }

  void testAcceptView()
  {
    MockDimensionView dView;
    EXPECT_CALL(dView, accept(_)).Times(5);
    EXPECT_CALL(dView, configureStrongly()).Times(5);
    EXPECT_CALL(dView, showAsNotIntegrated(_)).Times(3);
    EXPECT_CALL(dView, showAsIntegrated()).Times(2);

    MockDimensionViewFactory factory;
    EXPECT_CALL(factory, create()).Times(5).WillRepeatedly(Return(&dView));
    
    MockGeometryView gView;
    EXPECT_CALL(gView, getDimensionViewFactory()).Times(1).WillRepeatedly(ReturnRef(factory));
    EXPECT_CALL(gView, addDimensionView(_)).Times(5);

    MDGeometryXMLParser parser(constructXML());
    parser.execute();

    SynchronisingGeometryPresenter presenter(parser); 
    presenter.acceptView(&gView);
    
    TS_ASSERT(Mock::VerifyAndClearExpectations(&gView));
    TS_ASSERT(Mock::VerifyAndClearExpectations(&dView));
    TS_ASSERT(Mock::VerifyAndClearExpectations(&factory));
  }

  void testCollapsingThrows()
  {
    //In this test schenario there is a only one non-integrated dimension.
    MDGeometryXMLParser parser(constructXML("2", "1", "1", "1", "1"));
    parser.execute();
    ExposedSynchronisingGeometryPresenter geometryPresenter(parser);

    MockDimensionView dView;
    DimensionPresenter dimensionPresenter(&dView, &geometryPresenter);
    
    //Should not be able to make a collapse request to the geometry presenter, when there is only one non-collapsed dimension.
    TSM_ASSERT_THROWS("Should not be able to collapse the only-exising non-collapsed dimension.", geometryPresenter.dimensionCollapsed(&dimensionPresenter), std::invalid_argument);
  }

  void testGetGeometryXML()
  {
    NiceMock<MockDimensionView> dView;
    
    NiceMock<MockDimensionViewFactory> factory;
    EXPECT_CALL(factory, create()).WillRepeatedly(Return(&dView));
    
    NiceMock<MockGeometryView> gView;
    EXPECT_CALL(gView, getDimensionViewFactory()).WillRepeatedly(ReturnRef(factory));

    MDGeometryXMLParser parser(constructXML());
    parser.execute();

    SynchronisingGeometryPresenter presenter(parser); 
    presenter.acceptView(&gView);

    TSM_ASSERT("Geometry XML has not been constructed", !presenter.getGeometryXML().empty()); 
    TS_ASSERT(Mock::VerifyAndClearExpectations(&gView));
    TS_ASSERT(Mock::VerifyAndClearExpectations(&dView));
    TS_ASSERT(Mock::VerifyAndClearExpectations(&factory));
  }

  void testDimensionRealign()
  {
    NiceMock<MockDimensionView> dView;
    EXPECT_CALL(dView, getVisDimensionName()).WillRepeatedly(Return("T-AXIS"));
    
    NiceMock<MockDimensionViewFactory> factory;
    EXPECT_CALL(factory, create()).WillRepeatedly(Return(&dView));
    
    NiceMock<MockGeometryView> gView;
    EXPECT_CALL(gView, getDimensionViewFactory()).WillRepeatedly(ReturnRef(factory));

    MDGeometryXMLParser parser(constructXML());
    parser.execute();

    ExposedSynchronisingGeometryPresenter presenter(parser); 
    presenter.acceptView(&gView);

    //find out what presenter X_DIMENSION maps to.
    DimPresenter_sptr presenterA = presenter.getMappings().at(presenter.X_AXIS);
    DimPresenter_sptr presenterB = presenter.getMappings().at(presenter.T_AXIS); 

    TSM_ASSERT_EQUALS("Swapping has not occured as expected.", presenter.X_AXIS, presenterA->getMapping());
    TSM_ASSERT_EQUALS("Swapping has not occured as expected.", presenter.T_AXIS, presenterB->getMapping());

    presenter.dimensionRealigned(presenterA.get()); //Now swap these two dimensions

    TSM_ASSERT_EQUALS("Swapping has not occured as expected.", presenter.T_AXIS, presenterA->getMapping());
    TSM_ASSERT_EQUALS("Swapping has not occured as expected.", presenter.X_AXIS, presenterB->getMapping());

    TS_ASSERT(Mock::VerifyAndClearExpectations(&gView));
    TS_ASSERT(Mock::VerifyAndClearExpectations(&dView));
    TS_ASSERT(Mock::VerifyAndClearExpectations(&factory));
  }

};

#endif
