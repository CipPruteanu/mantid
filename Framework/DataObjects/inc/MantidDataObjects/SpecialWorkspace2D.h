#ifndef MANTID_DATAOBJECTS_SPECIALWORKSPACE2D_H_
#define MANTID_DATAOBJECTS_SPECIALWORKSPACE2D_H_

#include "MantidAPI/MatrixWorkspace_fwd.h"
#include "MantidDataObjects/Workspace2D.h"
#include "MantidGeometry/Instrument.h"

namespace Mantid {
namespace DataObjects {

/** An SpecialWorkspace2D is a specialized Workspace2D where
 * the Y value at each pixel will be used for a special meaning.
 * Specifically, by GroupingWorkspace, MaskWorkspace and
 * OffsetsWorkspace.
 *
 * The workspace has a single pixel per detector, and this cannot
 * be changed.
 *
 */

class BinaryOperator {
public:
  enum e { AND, OR, XOR, NOT };
};

class DLLExport SpecialWorkspace2D : public Workspace2D {
public:
  SpecialWorkspace2D() = default;
  SpecialWorkspace2D(Geometry::Instrument_const_sptr inst,
                     const bool includeMonitors = false);
  SpecialWorkspace2D(API::MatrixWorkspace_const_sptr parent);

  /// Returns a clone of the workspace
  std::unique_ptr<SpecialWorkspace2D> clone() const {
    return std::unique_ptr<SpecialWorkspace2D>(doClone());
  }
  SpecialWorkspace2D &operator=(const SpecialWorkspace2D &) = delete;
  /** Gets the name of the workspace type
  @return Standard string name  */
  const std::string id() const override { return "SpecialWorkspace2D"; }

  double getValue(const detid_t detectorID) const;
  double getValue(const detid_t detectorID, const double defaultValue) const;

  void setValue(const detid_t detectorID, const double value,
                const double error = 0.);
  void setValue(const std::set<detid_t> &detectorIDs, const double value,
                const double error = 0.);

  std::set<detid_t> getDetectorIDs(const std::size_t workspaceIndex) const;

  void binaryOperation(boost::shared_ptr<const SpecialWorkspace2D> &ws,
                       const unsigned int operatortype);
  void binaryOperation(const unsigned int operatortype);

  virtual void copyFrom(boost::shared_ptr<const SpecialWorkspace2D> sourcews);

private:
  SpecialWorkspace2D *doClone() const override {
    return new SpecialWorkspace2D(*this);
  }
  bool isCompatible(boost::shared_ptr<const SpecialWorkspace2D> ws);

protected:
  /// Protected copy constructor. May be used by childs for cloning.
  SpecialWorkspace2D(const SpecialWorkspace2D &) = default;

  void init(const size_t &NVectors, const size_t &XLength,
            const size_t &YLength) override;

  /// Return human-readable string
  const std::string toString() const override;

  void binaryAND(boost::shared_ptr<const SpecialWorkspace2D> ws);
  void binaryOR(boost::shared_ptr<const SpecialWorkspace2D> ws);
  void binaryXOR(boost::shared_ptr<const SpecialWorkspace2D> ws);
  void binaryNOT();

  /// Map with key = detector ID, and value = workspace index.
  std::map<detid_t, std::size_t> detID_to_WI;
};

/// shared pointer to the SpecialWorkspace2D class
typedef boost::shared_ptr<SpecialWorkspace2D> SpecialWorkspace2D_sptr;

/// shared pointer to a const SpecialWorkspace2D
typedef boost::shared_ptr<const SpecialWorkspace2D>
    SpecialWorkspace2D_const_sptr;

} // namespace Mantid
} // namespace DataObjects

#endif /* MANTID_DATAOBJECTS_SPECIALWORKSPACE2D_H_ */
