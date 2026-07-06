"""HPCL Direct Sales Product Catalog"""

from typing import List, Dict, Set
from dataclasses import dataclass, field


@dataclass
class HPCLProduct:
    """HPCL Direct Sales product definition"""
    
    product_code: str
    product_name: str
    category: str
    
    # Direct product mentions
    keywords: List[str] = field(default_factory=list)
    
    # Equipment/facility indicators
    operational_cues: List[str] = field(default_factory=list)
    
    # Target industries
    target_industries: List[str] = field(default_factory=list)
    
    # Strong confidence boosters
    strong_indicators: List[str] = field(default_factory=list)


class HPCLProductCatalog:
    """Complete HPCL DS product catalog"""
    
    def __init__(self):
        self.products = self._initialize_catalog()
        self.product_map = {p.product_code: p for p in self.products}
    
    def _initialize_catalog(self) -> List[HPCLProduct]:
        """Initialize all HPCL DS products"""
        
        return [
            # ========== INDUSTRIAL FUELS ==========
            
            HPCLProduct(
                product_code="MS",
                product_name="Motor Spirit (Petrol)",
                category="industrial_fuel",
                keywords=["motor spirit", "petrol", "gasoline", "ms"],
                operational_cues=["light vehicles", "small generators"],
                target_industries=["Logistics", "Construction"],
                strong_indicators=["petrol requirement", "motor spirit supply"]
            ),
            
            HPCLProduct(
                product_code="HSD",
                product_name="High-Speed Diesel",
                category="industrial_fuel",
                keywords=["high speed diesel", "hsd", "diesel"],
                operational_cues=["diesel genset", "dg set", "backup power", "heavy vehicles"],
                target_industries=["Manufacturing", "Mining", "Construction"],
                strong_indicators=["diesel requirement", "hsd supply", "genset fuel"]
            ),
            
            HPCLProduct(
                product_code="LDO",
                product_name="Light Diesel Oil",
                category="industrial_fuel",
                keywords=["light diesel oil", "ldo"],
                operational_cues=["medium speed engines", "small furnaces", "kilns"],
                target_industries=["Ceramics", "Glass", "Textiles"],
                strong_indicators=["ldo requirement"]
            ),
            
            HPCLProduct(
                product_code="FO",
                product_name="Furnace Oil",
                category="industrial_fuel",
                keywords=["furnace oil", "fo", "fuel oil"],
                operational_cues=["boiler", "furnace", "thermal power", "steam generation", "captive power plant"],
                target_industries=["Power", "Steel", "Cement", "Chemicals", "Textiles"],
                strong_indicators=["furnace oil requirement", "boiler fuel", "fo supply"]
            ),
            
            HPCLProduct(
                product_code="LSHS",
                product_name="Low Sulphur Heavy Stock",
                category="industrial_fuel",
                keywords=["lshs", "low sulphur heavy stock"],
                operational_cues=["emission compliant", "large boilers", "power plants"],
                target_industries=["Power", "Refineries", "Steel"],
                strong_indicators=["lshs requirement", "low sulphur fuel"]
            ),
            
            HPCLProduct(
                product_code="SKO",
                product_name="Superior Kerosene Oil (Non-PDS)",
                category="industrial_fuel",
                keywords=["superior kerosene oil", "sko", "kerosene"],
                operational_cues=["industrial heating", "aviation testing"],
                target_industries=["Aerospace", "Specialty Manufacturing"],
                strong_indicators=["sko requirement"]
            ),
            
            # ========== SPECIALTY PRODUCTS ==========
            
            HPCLProduct(
                product_code="HEXANE",
                product_name="Hexane",
                category="specialty",
                keywords=["hexane", "n-hexane", "solvent extraction"],
                operational_cues=["oil extraction", "edible oil", "solvent extraction plant", "oil mill"],
                target_industries=["Edible Oil", "Pharmaceuticals", "Adhesives"],
                strong_indicators=["hexane requirement", "solvent extraction"]
            ),
            
            HPCLProduct(
                product_code="SOLVENT_1425",
                product_name="Solvent 1425",
                category="specialty",
                keywords=["solvent 1425", "mineral spirits"],
                operational_cues=["degreasing", "paint thinner", "cleaning solvent"],
                target_industries=["Paints", "Automotive", "Metal Fabrication"],
                strong_indicators=["solvent 1425", "degreasing solvent"]
            ),
            
            HPCLProduct(
                product_code="MTO",
                product_name="Mineral Turpentine Oil (MTO 2445)",
                category="specialty",
                keywords=["mineral turpentine oil", "mto", "turpentine", "mto 2445"],
                operational_cues=["paint manufacturing", "varnish", "printing"],
                target_industries=["Paints", "Printing", "Rubber"],
                strong_indicators=["mto requirement", "turpentine oil"]
            ),
            
            HPCLProduct(
                product_code="JBO",
                product_name="Jute Batch Oil",
                category="specialty",
                keywords=["jute batch oil", "jbo", "jute batching oil"],
                operational_cues=["jute mill", "jute processing", "fiber batching", "batching unit"],
                target_industries=["Jute Manufacturing"],
                strong_indicators=["jute batch oil", "jbo requirement", "jute batching"]
            ),
            
            # ========== BULK PRODUCTS ==========
            
            HPCLProduct(
                product_code="BITUMEN",
                product_name="Bitumen",
                category="bulk",
                keywords=["bitumen", "asphalt", "tar"],
                operational_cues=["road construction", "highway project", "paving", "road surfacing"],
                target_industries=["Construction", "Infrastructure"],
                strong_indicators=["bitumen requirement", "road project", "highway construction"]
            ),
            
            HPCLProduct(
                product_code="MARINE_BUNKERS",
                product_name="Marine Bunker Fuels",
                category="bulk",
                keywords=["marine bunker", "bunker fuel", "ship fuel", "hfo", "mgo"],
                operational_cues=["shipping operations", "vessel refueling", "port operations", "bunkering"],
                target_industries=["Shipping", "Ports"],
                strong_indicators=["bunker fuel", "marine fuel requirement", "vessel fuel"]
            ),
            
            HPCLProduct(
                product_code="SULPHUR",
                product_name="Sulphur (Molten)",
                category="bulk",
                keywords=["sulphur", "sulfur", "molten sulphur"],
                operational_cues=["fertilizer production", "sulfuric acid", "chemical manufacturing"],
                target_industries=["Fertilizers", "Chemicals"],
                strong_indicators=["sulphur requirement", "fertilizer plant"]
            ),
            
            HPCLProduct(
                product_code="PROPYLENE",
                product_name="Propylene",
                category="bulk",
                keywords=["propylene", "propene"],
                operational_cues=["polymer production", "polypropylene", "petrochemical", "plastic manufacturing"],
                target_industries=["Petrochemicals", "Plastics"],
                strong_indicators=["propylene requirement", "polypropylene plant"]
            )
        ]
    
    def get_product(self, product_code: str) -> HPCLProduct:
        """Get product by code"""
        return self.product_map.get(product_code)
    
    def get_all_products(self) -> List[HPCLProduct]:
        """Get all products"""
        return self.products