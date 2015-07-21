#include "MantidKernel/MDUnitFactory.h"
#include "MantidKernel/MDUnit.h"
#include "MantidKernel/UnitLabelTypes.h"
#include <memory>

namespace Mantid {
namespace Kernel {

/**
 * Factory method wrapper. Wraps results in smart pointer.
 * @param unitString : unit string to intepret
 * @return Product
 */
std::unique_ptr<MDUnit>
MDUnitFactory::create(const std::string &unitString) const {
  if (this->canInterpret(unitString)) {
    return MDUnit_uptr(this->createRaw(unitString));
  } else {
    if (this->hasSuccessor()) {
      return (*m_successor)->create(unitString);
    } else {
      throw std::invalid_argument("No successor MDUnitFactory");
    }
  }
}

LabelUnit *LabelUnitFactory::createRaw(const std::string &unitString) const
{
    return new LabelUnit(unitString);
}

bool LabelUnitFactory::canInterpret(const std::string &) const
{
    return true; // Can always treat a unit as a label unit.
}

InverseAngstromsUnit *InverseAngstromsUnitFactory::createRaw(const std::string&) const
{
    return new InverseAngstromsUnit;
}

bool InverseAngstromsUnitFactory::canInterpret(const std::string &unitString) const
{
    return unitString == Units::Symbol::InverseAngstrom.ascii();
}

ReciprocalLatticeUnit *ReciprocalLatticeUnitFactory::createRaw(const std::string&) const
{
    return new ReciprocalLatticeUnit;
}

bool ReciprocalLatticeUnitFactory::canInterpret(const std::string &unitString) const
{
    return unitString == Units::Symbol::RLU.ascii();
}

MDUnitFactory_uptr makeStandardChain()
{
    typedef MDUnitFactory_uptr FactoryType;
    auto first = FactoryType(new InverseAngstromsUnitFactory);
    first->setSuccessor(FactoryType(new ReciprocalLatticeUnitFactory)).setSuccessor(FactoryType(new LabelUnitFactory));
    return first;
}



} // namespace Kernel
} // namespace Mantid
