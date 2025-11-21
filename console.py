import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class MinerAPI:
    def __init__(self, base_url: str = "http://172.16.58.104", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key or os.environ.get('MINER_API_KEY')
        self.headers = {
            'accept': 'application/json'
        }
        
        # Add API key to headers if provided
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
            # Alternative formats (uncomment the one that matches your API):
            # self.headers['X-API-Key'] = self.api_key
            # self.headers['api-key'] = self.api_key
    
    def check_auth(self) -> Dict[str, Any]:
        """Check authentication status"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth-check",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking auth: {e}")
            return {}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get miner summary statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/summary",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting summary: {e}")
            return {}
    
    def parse_miner_stats(self, data: Dict[str, Any]) -> None:
        """Parse and display miner statistics"""
        if not data or 'miner' not in data:
            print("No miner data available")
            return
        
        miner = data['miner']
        
        print("=" * 60)
        print(f"MINER STATISTICS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Basic Info
        print(f"\n🔧 Miner Type: {miner.get('miner_type', 'N/A')}")
        print(f"📊 Status: {miner.get('miner_status', {}).get('miner_state', 'N/A').upper()}")
        
        # Hashrate
        print(f"\n⚡ HASHRATE:")
        print(f"  • Average:  {miner.get('average_hashrate', 0):.2f} TH/s")
        print(f"  • Instant:  {miner.get('instant_hashrate', 0):.2f} TH/s")
        print(f"  • Nominal:  {miner.get('hr_nominal', 0):.2f} TH/s")
        print(f"  • Realtime: {miner.get('hr_realtime', 0):.2f} GH/s")
        
        # Power
        print(f"\n⚡ POWER:")
        print(f"  • Consumption: {miner.get('power_consumption', 0)} W")
        print(f"  • Efficiency:  {miner.get('power_efficiency', 0):.2f} W/TH")
        
        # Temperature
        pcb_temp = miner.get('pcb_temp', {})
        chip_temp = miner.get('chip_temp', {})
        print(f"\n🌡️  TEMPERATURE:")
        print(f"  • PCB:  {pcb_temp.get('min', 0)}°C - {pcb_temp.get('max', 0)}°C")
        print(f"  • Chip: {chip_temp.get('min', 0)}°C - {chip_temp.get('max', 0)}°C")
        
        # Errors
        print(f"\n❌ ERRORS:")
        print(f"  • Hardware Errors: {miner.get('hw_errors', 0)} ({miner.get('hw_errors_percent', 0)}%)")
        print(f"  • Hashrate Error:  {miner.get('hr_error', 0)}")
        
        # Dev Fee
        print(f"\n💰 DEV FEE:")
        print(f"  • Percentage: {miner.get('devfee_percent', 0):.3f}%")
        print(f"  • Value:      {miner.get('devfee', 0):.2f}")
        
        # Pools
        pools = miner.get('pools', [])
        print(f"\n🏊 POOLS ({len(pools)}):")
        for pool in pools:
            status_icon = "✓" if pool.get('status') == 'active' else "○"
            print(f"  {status_icon} [{pool.get('id')}] {pool.get('url', 'N/A')}")
            print(f"     Status: {pool.get('status', 'N/A')} | Diff: {pool.get('diff', 'N/A')}")
            print(f"     Accepted: {pool.get('accepted', 0)} | Rejected: {pool.get('rejected', 0)} | Stale: {pool.get('stale', 0)}")
        
        # Cooling
        cooling = miner.get('cooling', {})
        fans = cooling.get('fans', [])
        print(f"\n🌀 COOLING:")
        print(f"  • Fan Duty: {cooling.get('fan_duty', 0)}%")
        print(f"  • Mode: {cooling.get('settings', {}).get('mode', {}).get('name', 'N/A')}")
        for fan in fans:
            print(f"  • Fan {fan.get('id')}: {fan.get('rpm', 0)} RPM ({fan.get('status', 'N/A')})")
        
        # Chains
        chains = miner.get('chains', [])
        print(f"\n⛓️  HASH CHAINS ({len(chains)}):")
        for chain in chains:
            print(f"  • Chain {chain.get('id')}:")
            print(f"     Frequency: {chain.get('frequency', 0)} MHz | Voltage: {chain.get('voltage', 0)} mV")
            print(f"     Hashrate: {chain.get('hashrate_rt', 0):.2f} GH/s ({chain.get('hashrate_percentage', 0):.2f}%)")
            print(f"     Power: {chain.get('power_consumption', 0)} W")
            chip_status = chain.get('chip_statuses', {})
            print(f"     Chips: Grey={chip_status.get('grey', 0)}, Orange={chip_status.get('orange', 0)}, Red={chip_status.get('red', 0)}")
        
        print("\n" + "=" * 60)

def main():
    # Initialize API client
    # Option 1: Pass API key directly
    api_key = "your_api_key_here"  # Replace with your actual API key
    api = MinerAPI(api_key=api_key)
    
    # Option 2: Use environment variable (more secure)
    # Set environment variable: export MINER_API_KEY=your_api_key_here
    # api = MinerAPI()
    
    # Option 3: Read from config file
    # with open('config.json') as f:
    #     config = json.load(f)
    #     api = MinerAPI(api_key=config['api_key'])
    
    # Check authentication
    print("Checking authentication...")
    auth_status = api.check_auth()
    print(f"Auth Status: {json.dumps(auth_status, indent=2)}\n")
    
    # Get summary data
    print("Fetching miner summary...")
    summary_data = api.get_summary()
    
    # Parse and display statistics
    if summary_data:
        api.parse_miner_stats(summary_data)
        
        # Optional: Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"miner_stats_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(summary_data, f, indent=2)
        print(f"\n💾 Data saved to: {filename}")
    else:
        print("Failed to retrieve miner data")

if __name__ == "__main__":
    main()
