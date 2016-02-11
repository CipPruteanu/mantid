/*
 * LoadEventPreNexusTest.h
 *
 *  Created on: Jun 23, 2010
 *      Author: janik zikovsky
 */

#ifndef LOADEVENTPRENEXUSTEST_H_
#define LOADEVENTPRENEXUSTEST_H_

#include <cxxtest/TestSuite.h>

#include "MantidDataHandling/LoadEventPreNexus.h"

#include "MantidAPI/Axis.h"
#include "MantidDataObjects/EventList.h"
#include "MantidDataObjects/EventWorkspace.h"
#include "MantidDataObjects/Workspace2D.h"
#include "MantidKernel/DateAndTime.h"
#include "MantidKernel/TimeSeriesProperty.h"

#include <sys/stat.h>

using namespace Mantid;
using namespace Mantid::DataHandling;
using namespace Mantid::DataObjects;
using namespace Mantid::Kernel;
using namespace Mantid::Kernel::Exception;
using namespace Mantid::API;
using namespace Mantid::Geometry;

using std::runtime_error;
using std::size_t;
using std::vector;
using std::cout;
using std::endl;

//==========================================================================================
class LoadEventPreNexusTest : public CxxTest::TestSuite {
public:
  LoadEventPreNexus *eventLoader;

  static LoadEventPreNexusTest *createSuite() {
    return new LoadEventPreNexusTest();
  }
  static void destroySuite(LoadEventPreNexusTest *suite) { delete suite; }

  LoadEventPreNexusTest() {}

  void setUp() {
    eventLoader = new LoadEventPreNexus();
    eventLoader->initialize();
  }

  void test_file_not_found() {
    TS_ASSERT_THROWS(eventLoader->setPropertyValue(
                         "EventFilename", "this_file_doesnt_exist.blabla.data"),
                     std::invalid_argument);
    // Execute fails since the properties aren't set correctly.
    TS_ASSERT_THROWS(eventLoader->execute(), std::runtime_error);
  }

  void test_data_sizes() {
    // Make sure the structs are the right size
    TS_ASSERT_EQUALS(sizeof(Pulse), 24);
    TS_ASSERT_EQUALS(sizeof(DasEvent), 8);
  }

  void checkWorkspace(std::string eventfile, std::string WSName,
                      int numpixels_with_events) {
    // Get the event file size
    struct stat filestatus;
    stat(eventfile.c_str(), &filestatus);

    EventWorkspace_sptr ew =
        AnalysisDataService::Instance().retrieveWS<EventWorkspace>(WSName);

    // The # of events = size of the file / 8 bytes (per event)
    TS_ASSERT_EQUALS(ew->getNumberEvents(), filestatus.st_size / 8);

    // Only some of the pixels were loaded, because of lot of them are empty
    TS_ASSERT_EQUALS(ew->getNumberHistograms(), numpixels_with_events);

    // Mapping between workspace index and spectrum number
    // Is the length good?
    TS_ASSERT_EQUALS(ew->getAxis(1)->length(), numpixels_with_events);
  }

  void test_LoadPreNeXus_REFL() {
    std::string eventfile("REF_L_32035_neutron_event.dat");
    std::string pulsefile("REF_L_32035_pulseid.dat");
    eventLoader->setPropertyValue("EventFilename", eventfile);
    eventLoader->setPropertyValue("PulseidFilename", pulsefile);
    eventLoader->setPropertyValue("MappingFilename", "REF_L_TS_2010_02_19.dat");
    eventLoader->setPropertyValue("OutputWorkspace", "refl");

    // Get the event file size
    struct stat filestatus;
    eventfile = eventLoader->getPropertyValue("EventFilename");
    stat(eventfile.c_str(), &filestatus);

    // no instrument definition - should fail
    TS_ASSERT((eventLoader->execute()));
  }

  void test_LoadPreNeXus_CNCS_7860() {
    std::string eventfile("CNCS_7860_neutron_event.dat");
    eventLoader->setPropertyValue("EventFilename", eventfile);
    eventLoader->setPropertyValue("MappingFilename", "CNCS_TS_2008_08_18.dat");
    eventLoader->setPropertyValue("OutputWorkspace", "cncs");

    // Get the event file size
    struct stat filestatus;
    stat(eventfile.c_str(), &filestatus);

    // std::cout << "***** executing *****" << std::endl;
    TS_ASSERT(eventLoader->execute());

    EventWorkspace_sptr ew = boost::dynamic_pointer_cast<EventWorkspace>(
        AnalysisDataService::Instance().retrieve("cncs"));

    // Get the start time of all pulses
    Kernel::TimeSeriesProperty<double> *log =
        dynamic_cast<Kernel::TimeSeriesProperty<double> *>(
            ew->mutableRun().getProperty("proton_charge"));
    std::map<DateAndTime, double> logMap = log->valueAsMap();
    std::map<DateAndTime, double>::iterator it, it2;
    it = logMap.begin();
    Kernel::DateAndTime start = it->first;

    std::vector<TofEvent> events1 = ew->getEventListPtr(1000)->getEvents();
    for (size_t i = 0; i < events1.size(); i++) {
      std::cout << (events1[i].pulseTime() - start) << " sec \n";
    }
  }

  void test_LoadPreNeXus_CNCS() { do_test_LoadPreNeXus_CNCS("Serial"); }

  void test_LoadPreNeXus_CNCS_parallel() {
    do_test_LoadPreNeXus_CNCS("Parallel");
  }

  void do_test_LoadPreNeXus_CNCS(std::string parallel) {
    std::string eventfile("CNCS_7860_neutron_event.dat");
    eventLoader->setPropertyValue("EventFilename", eventfile);
    eventLoader->setPropertyValue("MappingFilename", "CNCS_TS_2008_08_18.dat");
    eventLoader->setPropertyValue("OutputWorkspace", "cncs");
    eventLoader->setPropertyValue("UseParallelProcessing", parallel);

    // Get the event file size
    struct stat filestatus;
    stat(eventfile.c_str(), &filestatus);

    // std::cout << "***** executing *****" << std::endl;
    TS_ASSERT(eventLoader->execute());

    EventWorkspace_sptr ew = boost::dynamic_pointer_cast<EventWorkspace>(
        AnalysisDataService::Instance().retrieve("cncs"));

    // The # of events = size of the file / 8 bytes (per event)
    // This fails cause of errors in events
    TS_ASSERT_EQUALS(ew->getNumberEvents(), 112266);

    // We pad all pixels by default
    int numpixels_with_events = 51200;
    TS_ASSERT_EQUALS(ew->getNumberHistograms(), numpixels_with_events);

    // Check if the instrument was loaded correctly
    boost::shared_ptr<const Instrument> inst = ew->getInstrument();
    TS_ASSERT_EQUALS(inst->getName(), "CNCS");

    // Mapping between workspace index and spectrum number
    // Is the length good?
    TS_ASSERT_EQUALS(ew->getAxis(1)->length(), numpixels_with_events);

    //--------------------------------------------------------
    // Now let's test if a copy works too
    EventWorkspace_sptr inputWS = ew;
    TS_ASSERT_EQUALS(inputWS->getInstrument()->getName(), "CNCS");

    // Create a new one
    EventWorkspace_sptr outputWS = boost::dynamic_pointer_cast<EventWorkspace>(
        API::WorkspaceFactory::Instance().create(
            "EventWorkspace", inputWS->getNumberHistograms(), 2, 1));
    TS_ASSERT(outputWS); // non-null pointer

    // Copy geometry over.
    API::WorkspaceFactory::Instance().initializeFromParent(inputWS, outputWS,
                                                           false);

    // You need to copy over the data as well.
    outputWS->copyDataFrom(*inputWS);

    // Bunch of checks
    TS_ASSERT_EQUALS(outputWS->getNumberEvents(), inputWS->getNumberEvents());
    TS_ASSERT_EQUALS(outputWS->getNumberHistograms(),
                     inputWS->getNumberHistograms());
    TS_ASSERT_EQUALS(outputWS->getInstrument()->getName(), "CNCS");

    std::size_t wkspIndex = 4348; // a good workspace index (with events)
    TS_ASSERT_EQUALS(outputWS->getEventList(wkspIndex).getNumberEvents(), 11);
    if (outputWS->getEventList(wkspIndex).getNumberEvents() != 11)
      return;

    TS_ASSERT_EQUALS(outputWS->getEventList(wkspIndex).getEvents()[0].tof(),
                     inputWS->getEventList(wkspIndex).getEvents()[0].tof());
    // It should be possible to change an event list and not affect the other
    // one
    outputWS->getEventList(wkspIndex).convertTof(1.5, 0.2);
    TS_ASSERT_DIFFERS(outputWS->getEventList(wkspIndex).getEvents()[0].tof(),
                      inputWS->getEventList(wkspIndex).getEvents()[0].tof());

    // Setting X should still be possible
    Kernel::cow_ptr<MantidVec> x;
    TS_ASSERT_THROWS_NOTHING(outputWS->setX(0, x));
    // Accessing Y is still possible
    const MantidVec Y =
        boost::dynamic_pointer_cast<const EventWorkspace>(outputWS)->dataY(0);

    // Check the run_start property exists and is right.
    Property *p = NULL;
    TS_ASSERT(outputWS->mutableRun().hasProperty("run_start"));
    TS_ASSERT_THROWS_NOTHING(
        p = outputWS->mutableRun().getProperty("run_start");)
    if (p) {
      TS_ASSERT_EQUALS(p->value(), "2010-03-25T16:08:37.457381666");
    }
  }

  void test_LoadPreNeXus_CNCS_SkipPixels() {
    std::string eventfile("CNCS_7860_neutron_event.dat");
    eventLoader->setPropertyValue("EventFilename", eventfile);
    eventLoader->setPropertyValue("MappingFilename", "CNCS_TS_2008_08_18.dat");
    eventLoader->setPropertyValue("OutputWorkspace", "cncs_skipped");
    // Load just 2 pixels
    eventLoader->setProperty("SpectrumList", "45, 110");

    TS_ASSERT(eventLoader->execute());

    EventWorkspace_sptr ew = boost::dynamic_pointer_cast<EventWorkspace>(
        AnalysisDataService::Instance().retrieve("cncs_skipped"));

    // Only some of the pixels weretof loaded, because of lot of them are empty
    int numpixels = 2;
    TS_ASSERT_EQUALS(ew->getNumberHistograms(), numpixels);

    // Mapping between workspace index and spectrum number; simple
    TS_ASSERT_EQUALS(ew->getAxis(1)->spectraNo(0), 46);
    TS_ASSERT_EQUALS(ew->getAxis(1)->spectraNo(1), 111);
    TS_ASSERT_EQUALS(ew->getAxis(1)->length(), 2);

    // Are the pixel IDs ok?
    TS_ASSERT_EQUALS(ew->getSpectrum(0)->getSpectrumNo(), 46);
    std::set<detid_t> dets = ew->getSpectrum(0)->getDetectorIDs();
    TS_ASSERT_EQUALS(dets.size(), 1);
    TS_ASSERT_EQUALS(*dets.begin(), 45);

    TS_ASSERT_EQUALS(ew->getSpectrum(1)->getSpectrumNo(), 111);
    dets = ew->getSpectrum(1)->getDetectorIDs();
    TS_ASSERT_EQUALS(dets.size(), 1);
    TS_ASSERT_EQUALS(*dets.begin(), 110);
  }

  void test_invalid_chunk_number() {
    eventLoader->setPropertyValue("EventFilename",
                                  "CNCS_7860_neutron_event.dat");
    eventLoader->setPropertyValue("ChunkNumber", "3");
    eventLoader->setPropertyValue("TotalChunks", "2");
    TS_ASSERT_THROWS(eventLoader->execute(), std::runtime_error);
  }

  void test_loading_chunks() {
    // Load chunk 1 of 2
    eventLoader->setPropertyValue("EventFilename",
                                  "CNCS_7860_neutron_event.dat");
    eventLoader->setPropertyValue("ChunkNumber", "1");
    eventLoader->setPropertyValue("TotalChunks", "2");
    eventLoader->setPropertyValue("OutputWorkspace", "chunk1");
    TS_ASSERT(eventLoader->execute());
    EventWorkspace_sptr chunk1 = boost::dynamic_pointer_cast<EventWorkspace>(
        AnalysisDataService::Instance().retrieve("chunk1"));

    // Load chunk 2 of 2
    eventLoader->setPropertyValue("EventFilename",
                                  "CNCS_7860_neutron_event.dat");
    eventLoader->setPropertyValue("ChunkNumber", "2");
    eventLoader->setPropertyValue("TotalChunks", "2");
    eventLoader->setPropertyValue("OutputWorkspace", "chunk2");
    TS_ASSERT(eventLoader->execute());
    EventWorkspace_sptr chunk2 = boost::dynamic_pointer_cast<EventWorkspace>(
        AnalysisDataService::Instance().retrieve("chunk2"));

    // The number of events should be roughly equal and the sum should be 112266
    TS_ASSERT_EQUALS(chunk1->getNumberEvents(), 56139)
    TS_ASSERT_EQUALS(chunk2->getNumberEvents(), 56127)
  }
};

//------------------------------------------------------------------------------
// Performance test
//------------------------------------------------------------------------------

class LoadEventPreNexusTestPerformance : public CxxTest::TestSuite {
public:
  void testDefaultLoad() {
    LoadEventPreNexus loader;
    loader.initialize();
    loader.setPropertyValue("EventFilename", "CNCS_7860_neutron_event.dat");
    loader.setPropertyValue("OutputWorkspace", "ws");
    TS_ASSERT(loader.execute());
  }
};

#endif /* LOADEVENTPRENEXUSTEST_H_ */
