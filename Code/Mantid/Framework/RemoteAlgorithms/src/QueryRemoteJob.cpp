#include "MantidRemoteAlgorithms/QueryRemoteJob.h"
#include "MantidKernel/MandatoryValidator.h"
#include "MantidKernel/NullValidator.h"
#include "MantidKernel/FacilityInfo.h"
#include "MantidKernel/ListValidator.h"
#include "MantidRemoteAlgorithms/SimpleJSON.h"
#include "MantidKernel/RemoteJobManager.h"

#include "boost/make_shared.hpp"

namespace Mantid
{
namespace RemoteAlgorithms
{
    
// Register the algorithm into the AlgorithmFactory
DECLARE_ALGORITHM(QueryRemoteJob)

using namespace Mantid::Kernel;
using namespace Mantid::API;
using namespace Mantid::Geometry;

// A reference to the logger is provided by the base class, it is called g_log.
// It is used to print out information, warning and error messages

void QueryRemoteJob::init()
{
  // Unlike most algorithms, this one doesn't deal with workspaces....

  auto requireValue = boost::make_shared<MandatoryValidator<std::string> >();
  auto nullValidator = boost::make_shared<NullValidator>();

  // Compute Resources
  std::vector<std::string> computes = Mantid::Kernel::ConfigService::Instance().getFacility().computeResources();
  declareProperty( "ComputeResource", "", boost::make_shared<StringListValidator>(computes), "", Direction::Input);

  // The ID of the job we want to query
  declareProperty( "JobID", "", requireValue, "", Direction::Input);

  // Name given to the job
  declareProperty( "JobName", "", nullValidator, "",  Direction::Output);

  // Name of the python script that was (or will be) run
  declareProperty( "ScriptName", "", nullValidator, "",  Direction::Output);

  // A human readable description of the job's status
  declareProperty( "JobStatusString", "", nullValidator, "",  Direction::Output);

  // Transaction ID this job is associated with
  declareProperty( "TransID", "", nullValidator, "",  Direction::Output);

  // Times for job submit, job start and job complete (may be empty depending
  // on the server-side implementation)
  declareProperty( "SubmitTime", "", nullValidator, "",  Direction::Output);
  declareProperty( "StartTime", "", nullValidator, "",  Direction::Output);
  declareProperty( "CompletionTime", "", nullValidator, "",  Direction::Output);

}

void QueryRemoteJob::exec()
{
  boost::shared_ptr<RemoteJobManager> jobManager = Mantid::Kernel::ConfigService::Instance().getFacility().getRemoteJobManager( getPropertyValue("ComputeResource"));

  // jobManager is a boost::shared_ptr...
  if (! jobManager)
  {
    // Requested compute resource doesn't exist
    // TODO: should we create our own exception class for this??
    throw( std::runtime_error( std::string("Unable to create a compute resource named " + getPropertyValue("ComputeResource"))));
  }

  std::istream &respStream = jobManager->httpGet("/query", std::string("JobID=") + getPropertyValue("JobID"));
  JSONObject resp;
  initFromStream( resp, respStream);
  if (jobManager->lastStatus() == Poco::Net::HTTPResponse::HTTP_OK)
  {
    JSONObject status;
    if (resp[getPropertyValue("JobID")].getType() != JSONValue::OBJECT)
    {
      throw( std::runtime_error( "Expected value not found in return stream.  Has the client/server protocol changed?!?"));
    }

    resp[getPropertyValue("JobID")].getValue(status);
    std::string value;

    status["JobStatus"].getValue( value);
    setProperty( "JobStatusString", value);

    status["JobName"].getValue( value);
    setProperty( "JobName", value);

    status["ScriptName"].getValue( value);
    setProperty( "ScriptName", value);

    status["TransID"].getValue( value);
    setProperty( "TransID", value);

    // The time stuff is actually an optional extension.  We could check the info
    // URL and see if the server implements it, but it's easier to just look in
    // the output and see if the values are there...
    if (status.find( "SubmitTime") != status.end())
    {
      status["SubmitTime"].getValue( value);
      setProperty( "SubmitTime", value);

      status["StartTime"].getValue( value);
      setProperty( "StartTime", value);

      status["CompletionTime"].getValue( value);
      setProperty( "CompletionTime", value);
    }
  }
  else
  {
    std::string errMsg;
    resp["Err_Msg"].getValue( errMsg);
    throw( std::runtime_error( errMsg));
  }
}


} // end namespace RemoteAlgorithms
} // end namespace Mantid
