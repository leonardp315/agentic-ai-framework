 
"""
Asset Administration Shell (AAS) Core Module
Implements semantic representation and metadata management for industrial assets
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import json
import sqlite3
import os

class AssetStatus(str, Enum):
    """Asset operational status"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance" 
    OFFLINE = "offline"
    ERROR = "error"

class SubmodelElement(BaseModel):
    """Basic element within a submodel"""
    id_short: str
    value: Union[str, int, float, bool]
    value_type: str
    description: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)

class Submodel(BaseModel):
    """Submodel containing properties and operations of an asset"""
    id: str
    id_short: str
    semantic_id: Optional[str] = None
    description: Optional[str] = None
    elements: Dict[str, SubmodelElement] = {}
    
    def add_element(self, element: SubmodelElement):
        """Add element to submodel"""
        self.elements[element.id_short] = element
    
    def update_element_value(self, element_id: str, new_value: Any):
        """Update value of specific element"""
        if element_id in self.elements:
            self.elements[element_id].value = new_value
            self.elements[element_id].last_updated = datetime.now()

class AssetAdministrationShell(BaseModel):
    """Complete AAS for an industrial asset"""
    id: str
    id_short: str
    global_asset_id: Optional[str] = None
    description: Optional[str] = None
    status: AssetStatus = AssetStatus.ACTIVE
    created: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)
    submodels: Dict[str, Submodel] = {}
    
    def add_submodel(self, submodel: Submodel):
        """Add submodel to AAS"""
        self.submodels[submodel.id_short] = submodel
        self.last_modified = datetime.now()
    
    def get_submodel(self, submodel_id: str) -> Optional[Submodel]:
        """Retrieve submodel by ID"""
        return self.submodels.get(submodel_id)
    
    def update_status(self, new_status: AssetStatus):
        """Update asset status"""
        self.status = new_status
        self.last_modified = datetime.now()

class AASRepository:
    """Repository for managing Asset Administration Shells"""
    
    def __init__(self, db_path: str = "data/aas_database.db"):
        self.db_path = db_path
        # Create data directory if not exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for AAS storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create AAS table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aas (
                    id TEXT PRIMARY KEY,
                    id_short TEXT UNIQUE,
                    global_asset_id TEXT,
                    description TEXT,
                    status TEXT,
                    created TEXT,
                    last_modified TEXT,
                    data TEXT
                )
            ''')
            
            # Create submodels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submodels (
                    id TEXT PRIMARY KEY,
                    aas_id TEXT,
                    id_short TEXT,
                    semantic_id TEXT,
                    description TEXT,
                    data TEXT,
                    FOREIGN KEY (aas_id) REFERENCES aas (id)
                )
            ''')
            
            conn.commit()
    
    def create_aas(self, aas: AssetAdministrationShell) -> bool:
        """Create new AAS in repository"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO aas (id, id_short, global_asset_id, description, status, created, last_modified, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    aas.id, aas.id_short, aas.global_asset_id, aas.description,
                    aas.status.value, aas.created.isoformat(), aas.last_modified.isoformat(),
                    aas.model_dump_json()
                ))
                
                # Insert submodels
                for submodel in aas.submodels.values():
                    cursor.execute('''
                        INSERT INTO submodels (id, aas_id, id_short, semantic_id, description, data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        submodel.id, aas.id, submodel.id_short, submodel.semantic_id,
                        submodel.description, submodel.model_dump_json()
                    ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating AAS: {e}")
            return False
    
    def get_aas(self, aas_id: str) -> Optional[AssetAdministrationShell]:
        """Retrieve AAS by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT data FROM aas WHERE id = ?', (aas_id,))
                result = cursor.fetchone()
                
                if result:
                    aas_data = json.loads(result[0])
                    return AssetAdministrationShell(**aas_data)
                return None
        except Exception as e:
            print(f"Error retrieving AAS: {e}")
            return None
    
    def list_all_aas(self) -> List[AssetAdministrationShell]:
        """List all AAS in repository"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT data FROM aas')
                results = cursor.fetchall()
                
                aas_list = []
                for result in results:
                    aas_data = json.loads(result[0])
                    aas_list.append(AssetAdministrationShell(**aas_data))
                
                return aas_list
        except Exception as e:
            print(f"Error listing AAS: {e}")
            return []
    
    def update_aas(self, aas: AssetAdministrationShell) -> bool:
        """Update existing AAS"""
        try:
            aas.last_modified = datetime.now()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE aas SET id_short=?, global_asset_id=?, description=?, 
                    status=?, last_modified=?, data=? WHERE id=?
                ''', (
                    aas.id_short, aas.global_asset_id, aas.description,
                    aas.status.value, aas.last_modified.isoformat(),
                    aas.model_dump_json(), aas.id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating AAS: {e}")
            return False

def create_sample_factory_aas() -> List[AssetAdministrationShell]:
    """Create sample AAS for factory demonstration"""
    sample_assets = []
    
    # Robot R-47
    robot_aas = AssetAdministrationShell(
        id="urn:aas:robot:R47",
        id_short="Robot_R47",
        global_asset_id="https://factory.example.com/assets/robot/R47",
        description="Industrial Welding Robot KUKA KR-150"
    )
    
    # Maintenance submodel
    maintenance_sm = Submodel(
        id="urn:submodel:maintenance:R47",
        id_short="Maintenance",
        description="Maintenance schedule and history"
    )
    
    maintenance_sm.add_element(SubmodelElement(
        id_short="LastService", 
        value="2024-09-15T10:00:00", 
        value_type="datetime",
        description="Last maintenance service date"
    ))
    
    maintenance_sm.add_element(SubmodelElement(
        id_short="NextService", 
        value="2024-12-15T10:00:00", 
        value_type="datetime",
        description="Next scheduled maintenance"
    ))
    
    maintenance_sm.add_element(SubmodelElement(
        id_short="ServiceHours", 
        value=2100, 
        value_type="int",
        description="Operating hours since last service"
    ))
    
    # Operation submodel
    operation_sm = Submodel(
        id="urn:submodel:operation:R47",
        id_short="Operation",
        description="Current operational parameters"
    )
    
    operation_sm.add_element(SubmodelElement(
        id_short="CurrentTask", 
        value="welding", 
        value_type="string",
        description="Current operation task"
    ))
    
    operation_sm.add_element(SubmodelElement(
        id_short="Efficiency", 
        value=94.5, 
        value_type="float",
        description="Current operational efficiency percentage"
    ))
    
    operation_sm.add_element(SubmodelElement(
        id_short="Temperature", 
        value=42.3, 
        value_type="float",
        description="Motor temperature in Celsius"
    ))
    
    robot_aas.add_submodel(maintenance_sm)
    robot_aas.add_submodel(operation_sm)
    sample_assets.append(robot_aas)
    
    # Conveyor Line L-01
    conveyor_aas = AssetAdministrationShell(
        id="urn:aas:conveyor:L01",
        id_short="Conveyor_L01",
        global_asset_id="https://factory.example.com/assets/conveyor/L01",
        description="Main Assembly Conveyor Line",
        status=AssetStatus.MAINTENANCE
    )
    
    # Add basic operation submodel to conveyor
    conv_operation = Submodel(
        id="urn:submodel:operation:L01",
        id_short="Operation", 
        description="Conveyor operational status"
    )
    
    conv_operation.add_element(SubmodelElement(
        id_short="Speed", 
        value=0, 
        value_type="float",
        description="Current belt speed in m/min"
    ))
    
    conv_operation.add_element(SubmodelElement(
        id_short="Load", 
        value=0, 
        value_type="int",
        description="Current load items count"
    ))
    
    conveyor_aas.add_submodel(conv_operation)
    sample_assets.append(conveyor_aas)
    
    return sample_assets

# Initialize repository and create sample data if needed
def init_sample_data():
    """Initialize repository with sample data"""
    repo = AASRepository()
    
    # Check if data already exists
    existing_aas = repo.list_all_aas()
    if not existing_aas:
        print("Creating sample AAS data...")
        sample_assets = create_sample_factory_aas()
        
        for aas in sample_assets:
            success = repo.create_aas(aas)
            if success:
                print(f"Created AAS: {aas.id_short}")
            else:
                print(f"Failed to create AAS: {aas.id_short}")
    else:
        print(f"Found {len(existing_aas)} existing AAS in repository")
    
    return repo

if __name__ == "__main__":
    # Test the AAS implementation
    repo = init_sample_data()
    
    # List all AAS
    all_aas = repo.list_all_aas()
    print(f"\nTotal AAS in repository: {len(all_aas)}")
    
    for aas in all_aas:
        print(f"- {aas.id_short}: {aas.description} (Status: {aas.status})")
        for sm_name, submodel in aas.submodels.items():
            print(f"  └─ {sm_name}: {len(submodel.elements)} elements")
