#include "MantidAPI/RefAxis.h"
#include "MantidAPI/Run.h"
#include "MantidAPI/SpectraAxis.h"
#include "MantidAPI/Progress.h"
#include "MantidAPI/WorkspaceFactory.h"
#include "MantidDataObjects/EventWorkspace.h"
#include "MantidDataObjects/EventWorkspaceMRU.h"
#include "MantidGeometry/Instrument.h"
#include "MantidGeometry/IDetector.h"
#include "MantidKernel/Exception.h"
#include "MantidKernel/TimeSeriesProperty.h"
#include "MantidKernel/MultiThreaded.h"
#include "MantidKernel/FunctionTask.h"
#include "MantidKernel/ThreadPool.h"
#include "MantidKernel/DateAndTime.h"
#include <limits>
#include <numeric>
#include "MantidAPI/ISpectrum.h"
#include "MantidKernel/CPUTimer.h"

using namespace boost::posix_time;
using Mantid::API::ISpectrum;
using Mantid::Kernel::DateAndTime;

namespace Mantid {
namespace DataObjects {
namespace {
// static logger
Kernel::Logger g_log("EventWorkspace");
}

DECLARE_WORKSPACE(EventWorkspace)

using Kernel::Exception::NotImplementedError;
using std::size_t;
using namespace Mantid::Kernel;

EventWorkspace::EventWorkspace() : mru(new EventWorkspaceMRU) {}

EventWorkspace::EventWorkspace(const EventWorkspace &other)
    : IEventWorkspace(other), mru(new EventWorkspaceMRU) {
  for (const auto &el : other.data) {
    // Create a new event list, copying over the events
    auto newel = new EventList(*el);
    // Make sure to update the MRU to point to THIS event workspace.
    newel->setMRU(this->mru);
    this->data.push_back(newel);
  }
}

EventWorkspace::~EventWorkspace() {
  for (auto &eventList : data)
    delete eventList;
  delete mru;
}

/** Returns true if the EventWorkspace is safe for multithreaded operations.
 * WARNING: This is only true for OpenMP threading. EventWorkspace is NOT thread
 * safe with Poco threads or other threading mechanisms.
 */
bool EventWorkspace::threadSafe() const {
  // Since there is a mutex lock around sorting, EventWorkspaces are always
  // safe.
  return true;
}

/** Initialize the pixels
 *  @param NVectors :: The number of vectors/histograms/detectors in the
 * workspace. Does not need
 *         to be set, but needs to be > 0
 *  @param XLength :: The number of X data points/bin boundaries in each vector
 * (ignored)
 *  @param YLength :: The number of data/error points in each vector (ignored)
 */
void EventWorkspace::init(const std::size_t &NVectors,
                          const std::size_t &XLength,
                          const std::size_t &YLength) {
  (void)YLength; // Avoid compiler warning

  // Check validity of arguments
  if (NVectors <= 0) {
    throw std::out_of_range(
        "Negative or 0 Number of Pixels specified to EventWorkspace::init");
  }
  // Initialize the data
  data.resize(NVectors, nullptr);
  // Make sure SOMETHING exists for all initialized spots.
  for (size_t i = 0; i < NVectors; i++)
    data[i] = new EventList(mru, specnum_t(i));

  // Set each X vector to have one bin of 0 & extremely close to zero
  // Move the rhs very,very slightly just incase something doesn't like them
  // being the same
  HistogramData::BinEdges edges{0.0, std::numeric_limits<double>::min()};
  this->setAllX(edges);

  // Create axes.
  m_axes.resize(2);
  m_axes[0] = new API::RefAxis(XLength, this);
  m_axes[1] = new API::SpectraAxis(this);
}

/// The total size of the workspace
/// @returns the number of single indexable items in the workspace
size_t EventWorkspace::size() const {
  return this->data.size() * this->blocksize();
}

/// Get the blocksize, aka the number of bins in the histogram
/// @returns the number of bins in the Y data
size_t EventWorkspace::blocksize() const {
  // Pick the first pixel to find the blocksize.
  auto it = data.begin();
  if (it == data.end()) {
    throw std::range_error("EventWorkspace::blocksize, no pixels in workspace, "
                           "therefore cannot determine blocksize (# of bins).");
  } else {
    return (*it)->histogram_size();
  }
}

/** Get the number of histograms, usually the same as the number of pixels or
 detectors.
 @returns the number of histograms / event lists
 */
size_t EventWorkspace::getNumberHistograms() const { return this->data.size(); }

/// Return const reference to EventList at the given workspace index.
EventList &EventWorkspace::getSpectrum(const size_t index) {
  invalidateCommonBinsFlag();
  return const_cast<EventList &>(
      static_cast<const EventWorkspace &>(*this).getSpectrum(index));
}

/// Return const reference to EventList at the given workspace index.
const EventList &EventWorkspace::getSpectrum(const size_t index) const {
  if (index >= data.size())
    throw std::range_error(
        "EventWorkspace::getSpectrum, workspace index out of range");
  return *data[index];
}

double EventWorkspace::getTofMin() const { return this->getEventXMin(); }

double EventWorkspace::getTofMax() const { return this->getEventXMax(); }

/**
 Get the minimum pulse time for events accross the entire workspace.
 @return minimum pulse time as a DateAndTime.
 */
DateAndTime EventWorkspace::getPulseTimeMin() const {
  // set to crazy values to start
  Mantid::Kernel::DateAndTime tMin = DateAndTime::maximum();
  size_t numWorkspace = this->data.size();
  DateAndTime temp;
  for (size_t workspaceIndex = 0; workspaceIndex < numWorkspace;
       workspaceIndex++) {
    const EventList &evList = this->getSpectrum(workspaceIndex);
    temp = evList.getPulseTimeMin();
    if (temp < tMin)
      tMin = temp;
  }
  return tMin;
}

/**
 Get the maximum pulse time for events accross the entire workspace.
 @return maximum pulse time as a DateAndTime.
 */
DateAndTime EventWorkspace::getPulseTimeMax() const {
  // set to crazy values to start
  Mantid::Kernel::DateAndTime tMax = DateAndTime::minimum();
  size_t numWorkspace = this->data.size();
  DateAndTime temp;
  for (size_t workspaceIndex = 0; workspaceIndex < numWorkspace;
       workspaceIndex++) {
    const EventList &evList = this->getSpectrum(workspaceIndex);
    temp = evList.getPulseTimeMax();
    if (temp > tMax)
      tMax = temp;
  }
  return tMax;
}
/**
Get the maximum and mimumum pulse time for events accross the entire workspace.
@param Tmin minimal pulse time as a DateAndTime.
@param Tmax maximal pulse time as a DateAndTime.
*/
void EventWorkspace::getPulseTimeMinMax(
    Mantid::Kernel::DateAndTime &Tmin,
    Mantid::Kernel::DateAndTime &Tmax) const {

  Tmax = DateAndTime::minimum();
  Tmin = DateAndTime::maximum();

  int64_t numWorkspace = static_cast<int64_t>(this->data.size());
#pragma omp parallel
  {
    DateAndTime tTmax = DateAndTime::minimum();
    DateAndTime tTmin = DateAndTime::maximum();
#pragma omp for nowait
    for (int64_t workspaceIndex = 0; workspaceIndex < numWorkspace;
         workspaceIndex++) {
      const EventList &evList = this->getSpectrum(workspaceIndex);
      DateAndTime tempMin, tempMax;
      evList.getPulseTimeMinMax(tempMin, tempMax);
      tTmin = std::min(tTmin, tempMin);
      tTmax = std::max(tTmax, tempMax);
    }
#pragma omp critical
    {
      Tmin = std::min(Tmin, tTmin);
      Tmax = std::max(Tmax, tTmax);
    }
  }
}

/**
 Get the minimum time at sample for events across the entire workspace.
 @param tofOffset :: Time of flight offset. defaults to zero.
 @return minimum time at sample as a DateAndTime.
 */
DateAndTime EventWorkspace::getTimeAtSampleMin(double tofOffset) const {
  auto instrument = this->getInstrument();
  auto sample = instrument->getSample();
  auto source = instrument->getSource();
  const double L1 = sample->getDistance(*source);

  // set to crazy values to start
  Mantid::Kernel::DateAndTime tMin = DateAndTime::maximum();
  size_t numWorkspace = this->data.size();
  DateAndTime temp;
  for (size_t workspaceIndex = 0; workspaceIndex < numWorkspace;
       workspaceIndex++) {
    const double L2 = this->getDetector(workspaceIndex)->getDistance(*sample);
    const double tofFactor = L1 / (L1 + L2);

    const EventList &evList = this->getSpectrum(workspaceIndex);
    temp = evList.getTimeAtSampleMin(tofFactor, tofOffset);
    if (temp < tMin)
      tMin = temp;
  }
  return tMin;
}

/**
 Get the maximum time at sample for events across the entire workspace.
 @param tofOffset :: Time of flight offset. defaults to zero.
 @return maximum time at sample as a DateAndTime.
 */
DateAndTime EventWorkspace::getTimeAtSampleMax(double tofOffset) const {
  auto instrument = this->getInstrument();
  auto sample = instrument->getSample();
  auto source = instrument->getSource();
  const double L1 = sample->getDistance(*source);

  // set to crazy values to start
  Mantid::Kernel::DateAndTime tMax = DateAndTime::minimum();
  size_t numWorkspace = this->data.size();
  DateAndTime temp;
  for (size_t workspaceIndex = 0; workspaceIndex < numWorkspace;
       workspaceIndex++) {
    const double L2 = this->getDetector(workspaceIndex)->getDistance(*sample);
    const double tofFactor = L1 / (L1 + L2);

    const EventList &evList = this->getSpectrum(workspaceIndex);
    temp = evList.getTimeAtSampleMax(tofFactor, tofOffset);
    if (temp > tMax)
      tMax = temp;
  }
  return tMax;
}

/**
 * Get them minimum x-value for the events themselves, ignoring the histogram
 * representation.
 *
 * @return The minimum x-value for the all events.
 *
 * This does copy some of the code from getEventXMinXMax, but that is because
 * getting both min and max then throwing away the max is significantly slower
 * on an unsorted event list.
 */
double EventWorkspace::getEventXMin() const {
  // set to crazy values to start
  double xmin = std::numeric_limits<double>::max();
  size_t numWorkspace = this->data.size();
  for (size_t workspaceIndex = 0; workspaceIndex < numWorkspace;
       workspaceIndex++) {
    const EventList &evList = this->getSpectrum(workspaceIndex);
    const double temp = evList.getTofMin();
    if (temp < xmin)
      xmin = temp;
  }
  return xmin;
}

/**
 * Get them maximum x-value for the events themselves, ignoring the histogram
 * representation.
 *
 * @return The maximum x-value for the all events.
 *
 * This does copy some of the code from getEventXMinXMax, but that is because
 * getting both min and max then throwing away the min is significantly slower
 * on an unsorted event list.
 */
double EventWorkspace::getEventXMax() const {
  // set to crazy values to start
  double xmax = -1.0 * std::numeric_limits<double>::max();
  size_t numWorkspace = this->data.size();
  for (size_t workspaceIndex = 0; workspaceIndex < numWorkspace;
       workspaceIndex++) {
    const EventList &evList = this->getSpectrum(workspaceIndex);
    const double temp = evList.getTofMax();
    if (temp > xmax)
      xmax = temp;
  }
  return xmax;
}

/**
 * Get them minimum and maximum x-values for the events themselves, ignoring the
 * histogram representation. Since this does not modify the sort order, the
 * method
 * will run significantly faster on a TOF_SORT event list.
 */
void EventWorkspace::getEventXMinMax(double &xmin, double &xmax) const {
  // set to crazy values to start
  xmin = std::numeric_limits<double>::max();
  xmax = -1.0 * xmin;
  int64_t numWorkspace = static_cast<int64_t>(this->data.size());
#pragma omp parallel
  {
    double tXmin = xmin;
    double tXmax = xmax;
#pragma omp for nowait
    for (int64_t workspaceIndex = 0; workspaceIndex < numWorkspace;
         workspaceIndex++) {
      const EventList &evList = this->getSpectrum(workspaceIndex);
      double temp = evList.getTofMin();
      tXmin = std::min(temp, tXmin);
      temp = evList.getTofMax();
      tXmax = std::max(temp, tXmax);
    }
#pragma omp critical
    {
      xmin = std::min(xmin, tXmin);
      xmax = std::max(xmax, tXmax);
    }
  }
}

/// The total number of events across all of the spectra.
/// @returns The total number of events
size_t EventWorkspace::getNumberEvents() const {
  return std::accumulate(data.begin(), data.end(), size_t{0},
                         [](size_t total, EventList *list) {
                           return total + list->getNumberEvents();
                         });
}

/** Get the EventType of the most-specialized EventList in the workspace
 *
 * @return the EventType of the most-specialized EventList in the workspace
 */
Mantid::API::EventType EventWorkspace::getEventType() const {
  Mantid::API::EventType out = Mantid::API::TOF;
  for (auto list : this->data) {
    Mantid::API::EventType thisType = list->getEventType();
    if (static_cast<int>(out) < static_cast<int>(thisType)) {
      out = thisType;
      // This is the most-specialized it can get.
      if (out == Mantid::API::WEIGHTED_NOTIME)
        return out;
    }
  }
  return out;
}

/** Switch all event lists to the given event type
 *
 * @param type :: EventType to switch to
 */
void EventWorkspace::switchEventType(const Mantid::API::EventType type) {
  for (auto &eventList : this->data)
    eventList->switchTo(type);
}

/// Returns true always - an EventWorkspace always represents histogramm-able
/// data
/// @returns If the data is a histogram - always true for an eventWorkspace
bool EventWorkspace::isHistogramData() const { return true; }

/** Return how many entries in the Y MRU list are used.
 * Only used in tests. It only returns the 0-th MRU list size.
 * @return :: number of entries in the MRU list.
 */
size_t EventWorkspace::MRUSize() const { return mru->MRUSize(); }

/** Clears the MRU lists */
void EventWorkspace::clearMRU() const { mru->clear(); }

/// Returns the amount of memory used in bytes
size_t EventWorkspace::getMemorySize() const {
  // TODO: Add the MRU buffer

  // Add the memory from all the event lists
  size_t total = std::accumulate(data.begin(), data.end(), size_t{0},
                                 [](size_t total, EventList *list) {
                                   return total + list->getMemorySize();
                                 });

  total += run().getMemorySize();

  total += this->getMemorySizeForXAxes();

  // Return in bytes
  return total;
}

/// Deprecated, use mutableX() instead. Return the data X vector at a given
/// workspace index
/// @param index :: the workspace index to return
/// @returns A reference to the vector of binned X values
MantidVec &EventWorkspace::dataX(const std::size_t index) {
  return getSpectrum(index).dataX();
}

/// Deprecated, use mutableDx() instead. Return the data X error vector at a
/// given workspace index
/// @param index :: the workspace index to return
/// @returns A reference to the vector of binned error values
MantidVec &EventWorkspace::dataDx(const std::size_t index) {
  return getSpectrum(index).dataDx();
}

/// Deprecated, use mutableY() instead. Return the data Y vector at a given
/// workspace index
/// Note: these non-const access methods will throw NotImplementedError
MantidVec &EventWorkspace::dataY(const std::size_t) {
  throw NotImplementedError("EventWorkspace::dataY cannot return a non-const "
                            "array: you can't modify the histogrammed data in "
                            "an EventWorkspace!");
}

/// Deprecated, use mutableE() instead. Return the data E vector at a given
/// workspace index
/// Note: these non-const access methods will throw NotImplementedError
MantidVec &EventWorkspace::dataE(const std::size_t) {
  throw NotImplementedError("EventWorkspace::dataE cannot return a non-const "
                            "array: you can't modify the histogrammed data in "
                            "an EventWorkspace!");
}

/** Deprecated, use x() instead.
 * @return the const data X vector at a given workspace index
 * @param index :: workspace index   */
const MantidVec &EventWorkspace::dataX(const std::size_t index) const {
  return getSpectrum(index).readX();
}

/** Deprecated, use dx() instead.
 * @return the const data X error vector at a given workspace index
 * @param index :: workspace index   */
const MantidVec &EventWorkspace::dataDx(const std::size_t index) const {
  return getSpectrum(index).readDx();
}

/** Deprecated, use y() instead.
 * @return the const data Y vector at a given workspace index
 * @param index :: workspace index   */
const MantidVec &EventWorkspace::dataY(const std::size_t index) const {
  return getSpectrum(index).readY();
}

/** Deprecated, use e() instead.
 * @return the const data E (error) vector at a given workspace index
 * @param index :: workspace index   */
const MantidVec &EventWorkspace::dataE(const std::size_t index) const {
  return getSpectrum(index).readE();
}

/** Deprecated, use sharedX() instead.
 * @return a pointer to the X data vector at a given workspace index
 * @param index :: workspace index   */
Kernel::cow_ptr<HistogramData::HistogramX>
EventWorkspace::refX(const std::size_t index) const {
  return getSpectrum(index).ptrX();
}

/** Using the event data in the event list, generate a histogram of it w.r.t
 *TOF.
 *
 * @param index :: workspace index to generate
 * @param X :: input X vector of the bin boundaries.
 * @param Y :: output vector to be filled with the Y data.
 * @param E :: output vector to be filled with the Error data (optionally)
 * @param skipError :: if true, the error vector is NOT calculated.
 *        This may save some processing time.
 */
void EventWorkspace::generateHistogram(const std::size_t index,
                                       const MantidVec &X, MantidVec &Y,
                                       MantidVec &E, bool skipError) const {
  if (index >= data.size())
    throw std::range_error(
        "EventWorkspace::generateHistogram, histogram number out of range");
  this->data[index]->generateHistogram(X, Y, E, skipError);
}

/** Using the event data in the event list, generate a histogram of it w.r.t
 *PULSE TIME.
 *
 * @param index :: workspace index to generate
 * @param X :: input X vector of the bin boundaries.
 * @param Y :: output vector to be filled with the Y data.
 * @param E :: output vector to be filled with the Error data (optionally)
 * @param skipError :: if true, the error vector is NOT calculated.
 *        This may save some processing time.
 */
void EventWorkspace::generateHistogramPulseTime(const std::size_t index,
                                                const MantidVec &X,
                                                MantidVec &Y, MantidVec &E,
                                                bool skipError) const {
  if (index >= data.size())
    throw std::range_error("EventWorkspace::generateHistogramPulseTime, "
                           "histogram number out of range");
  this->data[index]->generateHistogramPulseTime(X, Y, E, skipError);
}

/*** Set all histogram X vectors.
 * @param x :: The X vector of histogram bins to use.
 */
void EventWorkspace::setAllX(const HistogramData::BinEdges &x) {
  // This is an EventWorkspace, so changing X size is ok as long as we clear
  // the MRU below, i.e., we avoid the size check of Histogram::setBinEdges and
  // just reset the whole Histogram.
  for (auto &eventList : this->data)
    eventList->setHistogram(x);

  // Clear MRU lists now, free up memory
  this->clearMRU();
}

/** Task for sorting an event list */
class EventSortingTask final : public Task {
public:
  /// ctor
  EventSortingTask(const EventWorkspace *WS, size_t wiStart, size_t wiStop,
                   EventSortType sortType, size_t howManyCores,
                   Mantid::API::Progress *prog)
      : Task(), m_wiStart(wiStart), m_wiStop(wiStop), m_sortType(sortType),
        m_howManyCores(howManyCores), m_WS(WS), prog(prog) {
    m_cost = 0;
    if (m_wiStop > m_WS->getNumberHistograms())
      m_wiStop = m_WS->getNumberHistograms();

    for (size_t wi = m_wiStart; wi < m_wiStop; wi++) {
      double n = static_cast<double>(m_WS->getSpectrum(wi).getNumberEvents());
      // Sorting time is approximately n * ln (n)
      m_cost += n * log(n);
    }

    if (!((m_howManyCores == 1) || (m_howManyCores == 2) ||
          (m_howManyCores == 4)))
      throw std::invalid_argument("howManyCores should be 1,2 or 4.");
  }

  // Execute the sort as specified.
  void run() override {
    if (!m_WS)
      return;
    for (size_t wi = m_wiStart; wi < m_wiStop; wi++) {
      if (m_sortType != TOF_SORT)
        m_WS->getSpectrum(wi).sort(m_sortType);
      else {
        if (m_howManyCores == 1) {
          m_WS->getSpectrum(wi).sort(m_sortType);
        } else if (m_howManyCores == 2) {
          m_WS->getSpectrum(wi).sortTof2();
        } else if (m_howManyCores == 4) {
          m_WS->getSpectrum(wi).sortTof4();
        }
      }
      // Report progress
      if (prog)
        prog->report("Sorting");
    }
  }

private:
  /// Start workspace index to process
  size_t m_wiStart;
  /// Stop workspace index to process
  size_t m_wiStop;
  /// How to sort
  EventSortType m_sortType;
  /// How many cores for each sort
  size_t m_howManyCores;
  /// EventWorkspace on which to sort
  const EventWorkspace *m_WS;
  /// Optional Progress dialog.
  Mantid::API::Progress *prog;
};

/*
 * Review each event list to get the sort type
 * If any 2 have different order type, then be unsorted
 */
EventSortType EventWorkspace::getSortType() const {
  size_t size = this->data.size();
  EventSortType order = data[0]->getSortType();
  for (size_t i = 1; i < size; i++) {
    if (order != data[i]->getSortType())
      return UNSORTED;
  }
  return order;
}

/*** Sort all event lists. Uses a parallelized algorithm
 * @param sortType :: How to sort the event lists.
 * @param prog :: a progress report object. If the pointer is not NULL, each
 * event list will call prog.report() once.
 */
void EventWorkspace::sortAll(EventSortType sortType,
                             Mantid::API::Progress *prog) const {
  if (this->getSortType() == sortType) {
    if (prog != nullptr) {
      prog->reportIncrement(this->data.size());
    }
    return;
  }

  size_t num_threads;
  num_threads = ThreadPool::getNumPhysicalCores();
  g_log.debug() << num_threads << " cores found. ";

  // Initial chunk size: set so that each core will be called for 20 tasks.
  // (This is to avoid making too small tasks.)
  size_t chunk_size = data.size() / (num_threads * 20);
  if (chunk_size < 1)
    chunk_size = 1;

  // Sort with 1 core per event list by default
  size_t howManyCores = 1;
  // And auto-detect how many threads
  size_t howManyThreads = 0;
#ifdef _OPENMP
  if (data.size() < num_threads * 10) {
    // If you have few vectors, sort with 2 cores.
    chunk_size = 1;
    howManyCores = 2;
    howManyThreads = num_threads / 2 + 1;
  } else if (data.size() < num_threads) {
    // If you have very few vectors, sort with 4 cores.
    chunk_size = 1;
    howManyCores = 4;
    howManyThreads = num_threads / 4 + 1;
  }
#endif
  g_log.debug() << "Performing sort with " << howManyCores
                << " cores per EventList, in " << howManyThreads
                << " threads, using a chunk size of " << chunk_size << ".\n";

  // Create the thread pool, and optimize by doing the longest sorts first.
  ThreadPool pool(new ThreadSchedulerLargestCost(), howManyThreads);
  for (size_t i = 0; i < data.size(); i += chunk_size) {
    pool.schedule(new EventSortingTask(this, i, i + chunk_size, sortType,
                                       howManyCores, prog));
  }

  // Now run it all
  pool.joinAll();
}

/** Integrate all the spectra in the matrix workspace within the range given.
 * Default implementation, can be overridden by base classes if they know
 *something smarter!
 *
 * @param out :: returns the vector where there is one entry per spectrum in the
 *workspace. Same
 *            order as the workspace indices.
 * @param minX :: minimum X bin to use in integrating.
 * @param maxX :: maximum X bin to use in integrating.
 * @param entireRange :: set to true to use the entire range. minX and maxX are
 *then ignored!
 */
void EventWorkspace::getIntegratedSpectra(std::vector<double> &out,
                                          const double minX, const double maxX,
                                          const bool entireRange) const {
  // Start with empty vector
  out.resize(this->getNumberHistograms(), 0.0);

  // We can run in parallel since there is no cross-reading of event lists
  PARALLEL_FOR_NO_WSP_CHECK()
  for (int wksp_index = 0; wksp_index < int(this->getNumberHistograms());
       wksp_index++) {
    // Get Handle to data
    EventList *el = this->data[wksp_index];

    // Let the eventList do the integration
    out[wksp_index] = el->integrate(minX, maxX, entireRange);
  }
}

} // namespace DataObjects
} // namespace Mantid

namespace Mantid {
namespace Kernel {
template <>
DLLExport Mantid::DataObjects::EventWorkspace_sptr
IPropertyManager::getValue<Mantid::DataObjects::EventWorkspace_sptr>(
    const std::string &name) const {
  PropertyWithValue<Mantid::DataObjects::EventWorkspace_sptr> *prop =
      dynamic_cast<
          PropertyWithValue<Mantid::DataObjects::EventWorkspace_sptr> *>(
          getPointerToProperty(name));
  if (prop) {
    return *prop;
  } else {
    std::string message =
        "Attempt to assign property " + name +
        " to incorrect type. Expected shared_ptr<EventWorkspace>.";
    throw std::runtime_error(message);
  }
}

template <>
DLLExport Mantid::DataObjects::EventWorkspace_const_sptr
IPropertyManager::getValue<Mantid::DataObjects::EventWorkspace_const_sptr>(
    const std::string &name) const {
  PropertyWithValue<Mantid::DataObjects::EventWorkspace_sptr> *prop =
      dynamic_cast<
          PropertyWithValue<Mantid::DataObjects::EventWorkspace_sptr> *>(
          getPointerToProperty(name));
  if (prop) {
    return prop->operator()();
  } else {
    std::string message =
        "Attempt to assign property " + name +
        " to incorrect type. Expected const shared_ptr<EventWorkspace>.";
    throw std::runtime_error(message);
  }
}
} // namespace Kernel
} // namespace Mantid

///\endcond TEMPLATE
