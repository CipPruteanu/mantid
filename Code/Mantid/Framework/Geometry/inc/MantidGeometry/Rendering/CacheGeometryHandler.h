#ifndef CACHE_GEOMETRYHANDLER_H
#define CACHE_GEOMETRYHANDLER_H

#include <boost/shared_ptr.hpp>
#include "MantidKernel/System.h"
#include "MantidGeometry/Rendering/GeometryHandler.h"

namespace Mantid
{

	namespace Geometry
	{
		/**
		\class CacheGeometryHandler
		\brief Place holder for geometry triangulation and rendering with caching triangles.
		\author Srikanth Nagella
		\date Jan 2009
		\version 1.0

		This is an implementation class for handling geometry from cache, if the cache doesn't exist then the 
		triangulation is done using another triangulation handler and store in cache.

		Copyright &copy; 2008 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory

		This file is part of Mantid.

		Mantid is free software; you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation; either version 3 of the License, or
		(at your option) any later version.

		Mantid is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.

		You should have received a copy of the GNU General Public License
		along with this program.  If not, see <http://www.gnu.org/licenses/>.

		File change history is stored at: <https://svn.mantidproject.org/mantid/trunk/Code/Mantid>
		*/
		class GeometryHandler;
		class CacheGeometryRenderer;
		class CacheGeometryGenerator;
		class IObjComponent;
		class Object;
		class V3D;
		class DLLExport CacheGeometryHandler: public GeometryHandler
		{
		private:
			static Kernel::Logger& PLog;           ///< The official logger
			CacheGeometryRenderer* Renderer;         ///< Geometry renderer variable used for rendering Object/ObjComponent
			CacheGeometryGenerator* Triangulator;    ///< Geometry generator to triangulate Object

		public:
			CacheGeometryHandler(IObjComponent* obj); ///< Constructor
			CacheGeometryHandler(boost::shared_ptr<Object>       obj); ///< Constructor
			CacheGeometryHandler(Object* obj); ///< Constructor
			~CacheGeometryHandler(); ///< Destructor
			GeometryHandler* createInstance(IObjComponent *comp);
			GeometryHandler* createInstance(boost::shared_ptr<Object> obj);
			void Triangulate();
			void Render();
			void Initialize();
			bool    canTriangulate(){return true;}
			int     NumberOfTriangles();
			int     NumberOfPoints();
			double* getTriangleVertices();
			int*    getTriangleFaces();
			/// Sets the geometry cache using the triangulation information provided
			void setGeometryCache(int noPts,int noFaces,double* pts,int* faces);
		};

	}   // NAMESPACE Geometry

}  // NAMESPACE Mantid

#endif
