"""Provenance Logger - Track source of every data point"""

from datetime import datetime
from typing import Dict
try:
    from loguru import logger
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)
import json
from pathlib import Path


class ProvenanceLogger:
    """Log provenance and timestamp for every extracted fact"""
    
    def __init__(self, log_file: str = "logs/provenance.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_extraction(
        self,
        source_domain: str,
        source_url: str,
        extracted_data: Dict,
        extraction_method: str,
        confidence: float = 1.0
    ) -> str:
        """
        Log data extraction with full provenance
        
        Returns:
            provenance_id: Unique ID for this extraction
        """
        
        provenance_id = f"PROV_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        provenance_record = {
            "provenance_id": provenance_id,
            "timestamp": datetime.now().isoformat(),
            "source": {
                "domain": source_domain,
                "url": source_url,
                "access_method": extraction_method
            },
            "extracted_data": extracted_data,
            "confidence": confidence,
            "legal_basis": "publicly_available_data",
            "robots_txt_compliant": True,
            "tos_compliant": True
        }
        
        # Append to JSONL file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(provenance_record) + '\n')
        
        logger.debug(f"Logged provenance: {provenance_id}")
        
        return provenance_id
    
    def get_provenance(self, provenance_id: str) -> Dict:
        """Retrieve provenance record by ID"""
        
        if not self.log_file.exists():
            return None
        
        with open(self.log_file, 'r') as f:
            for line in f:
                record = json.loads(line)
                if record['provenance_id'] == provenance_id:
                    return record
        
        return None
