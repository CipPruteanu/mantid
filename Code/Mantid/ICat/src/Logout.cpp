#include  "MantidICat/Logout.h"
#include "MantidAPI/CatalogFactory.h"
#include "MantidKernel/ConfigService.h"
#include "MantidKernel/FacilityInfo.h"
#include "MantidAPI/ICatalog.h"

namespace Mantid
{
	namespace ICat
	{
		using namespace Kernel;
		using namespace API;
		DECLARE_ALGORITHM(CLogout)

		/// Init method to declare algorithm properties
		void CLogout::init()
		{			
		}
		/// execute the algorithm
		void CLogout::exec()
		{
			ICatalog_sptr catalog_sptr;
			try
			{			
			 catalog_sptr=CatalogFactory::Instance().create(ConfigService::Instance().Facility().catalogName());
			
			}
			catch(Kernel::Exception::NotFoundError&)
			{
				throw std::runtime_error("Error when getting the catalog information from the Facilities.xml file.");
			} 
			if(!catalog_sptr)
			{
				throw std::runtime_error("Error when getting the catalog information from the Facilities.xml file");
			}
			catalog_sptr->logout();
	
		}

	 }
}
