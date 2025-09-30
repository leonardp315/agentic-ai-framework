 
"""
AAS Integration Module for Dashboard
Connects dashboard with real Asset Administration Shell data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from aas.aas_core import AASRepository, AssetStatus
import pandas as pd
from typing import List, Dict, Any

class DashboardAASConnector:
    """Connector between AAS repository and dashboard interface"""
    
    def __init__(self):
        self.repo = AASRepository()
    
    def get_assets_summary(self) -> pd.DataFrame:
        """Get summary of all assets for dashboard display"""
        all_aas = self.repo.list_all_aas()
        
        assets_data = []
        for aas in all_aas:
            # Get maintenance info if available
            last_maintenance = "N/A"
            next_service = "N/A"
            efficiency = "N/A"
            
            # Extract maintenance submodel data
            if "Maintenance" in aas.submodels:
                maintenance_sm = aas.submodels["Maintenance"]
                if "LastService" in maintenance_sm.elements:
                    last_maintenance = maintenance_sm.elements["LastService"].value[:10]  # Date only
                if "NextService" in maintenance_sm.elements:
                    next_service = maintenance_sm.elements["NextService"].value[:10]
            
            # Extract operation submodel data
            if "Operation" in aas.submodels:
                operation_sm = aas.submodels["Operation"]
                if "Efficiency" in operation_sm.elements:
                    efficiency = f"{operation_sm.elements['Efficiency'].value}%"
            
            assets_data.append({
                "ID": aas.id_short,
                "Name": aas.description or aas.id_short,
                "Status": aas.status.value.title(),
                "Last_Maintenance": last_maintenance,
                "Next_Service": next_service,
                "Efficiency": efficiency
            })
        
        return pd.DataFrame(assets_data)
    
    def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """Get detailed information about specific asset"""
        all_aas = self.repo.list_all_aas()
        
        for aas in all_aas:
            if aas.id_short == asset_id or aas.id.endswith(asset_id):
                # Build detailed asset information
                details = {
                    "asset_id": aas.id,
                    "name": aas.description or aas.id_short,
                    "status": aas.status.value,
                    "created": aas.created.strftime("%Y-%m-%d %H:%M"),
                    "last_modified": aas.last_modified.strftime("%Y-%m-%d %H:%M"),
                    "properties": {},
                    "submodels": {}
                }
                
                # Extract submodel information
                for sm_name, submodel in aas.submodels.items():
                    details["submodels"][sm_name] = {}
                    for elem_name, element in submodel.elements.items():
                        details["submodels"][sm_name][elem_name] = {
                            "value": element.value,
                            "type": element.value_type,
                            "description": element.description,
                            "last_updated": element.last_updated.strftime("%Y-%m-%d %H:%M")
                        }
                
                return details
        
        return None
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics for overview dashboard"""
        all_aas = self.repo.list_all_aas()
        
        total_assets = len(all_aas)
        active_assets = sum(1 for aas in all_aas if aas.status == AssetStatus.ACTIVE)
        maintenance_assets = sum(1 for aas in all_aas if aas.status == AssetStatus.MAINTENANCE)
        offline_assets = sum(1 for aas in all_aas if aas.status == AssetStatus.OFFLINE)
        
        # Calculate average efficiency from operation submodels
        efficiencies = []
        for aas in all_aas:
            if "Operation" in aas.submodels:
                operation_sm = aas.submodels["Operation"]
                if "Efficiency" in operation_sm.elements:
                    efficiencies.append(float(operation_sm.elements["Efficiency"].value))
        
        avg_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 0
        
        return {
            "total_assets": total_assets,
            "active_assets": active_assets,
            "maintenance_assets": maintenance_assets,
            "offline_assets": offline_assets,
            "average_efficiency": round(avg_efficiency, 1)
        }
    
    def update_asset_status(self, asset_id: str, new_status: str) -> bool:
        """Update asset status"""
        all_aas = self.repo.list_all_aas()
        
        for aas in all_aas:
            if aas.id_short == asset_id:
                try:
                    status_enum = AssetStatus(new_status.lower())
                    aas.update_status(status_enum)
                    return self.repo.update_aas(aas)
                except ValueError:
                    return False
        
        return False
    
    def get_maintenance_alerts(self) -> List[Dict[str, str]]:
        """Get maintenance alerts and warnings"""
        all_aas = self.repo.list_all_aas()
        alerts = []
        
        for aas in all_aas:
            if "Maintenance" in aas.submodels:
                maintenance_sm = aas.submodels["Maintenance"]
                
                # Check service hours
                if "ServiceHours" in maintenance_sm.elements:
                    hours = maintenance_sm.elements["ServiceHours"].value
                    if hours > 2000:  # Alert threshold
                        alerts.append({
                            "asset": aas.id_short,
                            "type": "maintenance",
                            "message": f"Service hours ({hours}h) approaching maintenance limit",
                            "severity": "high" if hours > 2500 else "medium"
                        })
            
            # Check operational parameters
            if "Operation" in aas.submodels:
                operation_sm = aas.submodels["Operation"]
                
                # Check efficiency
                if "Efficiency" in operation_sm.elements:
                    efficiency = float(operation_sm.elements["Efficiency"].value)
                    if efficiency < 85:
                        alerts.append({
                            "asset": aas.id_short,
                            "type": "performance",
                            "message": f"Low efficiency: {efficiency}%",
                            "severity": "medium"
                        })
                
                # Check temperature if available
                if "Temperature" in operation_sm.elements:
                    temp = float(operation_sm.elements["Temperature"].value)
                    if temp > 60:  # High temperature threshold
                        alerts.append({
                            "asset": aas.id_short,
                            "type": "temperature",
                            "message": f"High temperature: {temp}°C",
                            "severity": "high"
                        })
        
        return alerts

# Global connector instance
aas_connector = DashboardAASConnector()
