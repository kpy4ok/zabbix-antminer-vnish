#!/usr/bin/env python3
"""
Zabbix 5 External Script for ASIC Miner Monitoring
Place this script in: /usr/lib/zabbix/externalscripts/
Make executable: chmod +x miner_monitor.py

Usage: miner_monitor.py <host> <api_key> <metric>
Example: miner_monitor.py 172.16.58.104 your_api_key hashrate.average
"""

import sys
import json
import requests
from typing import Dict, Any, Optional

class MinerMonitor:
    def __init__(self, host: str, api_key: Optional[str] = None):
        self.base_url = f"http://{host}"
        self.headers = {'accept': 'application/json'}
        
        if api_key and api_key != 'none':
            self.headers['Authorization'] = f'Bearer {api_key}'
        
        self.timeout = 10
    
    def get_summary(self) -> Dict[str, Any]:
        """Fetch miner summary data"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/summary",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"0")
            sys.exit(1)
    
    def get_metric(self, metric: str) -> Any:
        """Extract specific metric from miner data"""
        data = self.get_summary()
        
        if not data or 'miner' not in data:
            return 0
        
        miner = data['miner']
        
        # Metric mapping
        metrics = {
            # Hashrate metrics
            'hashrate.average': lambda: miner.get('average_hashrate', 0),
            'hashrate.instant': lambda: miner.get('instant_hashrate', 0),
            'hashrate.nominal': lambda: miner.get('hr_nominal', 0),
            'hashrate.realtime': lambda: miner.get('hr_realtime', 0),
            
            # Power metrics
            'power.consumption': lambda: miner.get('power_consumption', 0),
            'power.efficiency': lambda: miner.get('power_efficiency', 0),
            
            # Temperature metrics
            'temp.pcb.min': lambda: miner.get('pcb_temp', {}).get('min', 0),
            'temp.pcb.max': lambda: miner.get('pcb_temp', {}).get('max', 0),
            'temp.chip.min': lambda: miner.get('chip_temp', {}).get('min', 0),
            'temp.chip.max': lambda: miner.get('chip_temp', {}).get('max', 0),
            
            # Error metrics
            'errors.hardware': lambda: miner.get('hw_errors', 0),
            'errors.hardware.percent': lambda: miner.get('hw_errors_percent', 0),
            'errors.hashrate': lambda: miner.get('hr_error', 0),
            
            # Status metrics
            'status': lambda: 1 if miner.get('miner_status', {}).get('miner_state') == 'mining' else 0,
            'uptime': lambda: miner.get('miner_status', {}).get('miner_state_time', 0),
            
            # Pool metrics
            'pool.accepted': lambda: sum(p.get('accepted', 0) for p in miner.get('pools', []) if p.get('pool_type') == 'UserPool'),
            'pool.rejected': lambda: sum(p.get('rejected', 0) for p in miner.get('pools', []) if p.get('pool_type') == 'UserPool'),
            'pool.stale': lambda: sum(p.get('stale', 0) for p in miner.get('pools', []) if p.get('pool_type') == 'UserPool'),
            'pool.active': lambda: sum(1 for p in miner.get('pools', []) if p.get('status') == 'active' and p.get('pool_type') == 'UserPool'),
            
            # Cooling metrics
            'fan.duty': lambda: miner.get('cooling', {}).get('fan_duty', 0),
            'fan.0.rpm': lambda: next((f.get('rpm', 0) for f in miner.get('cooling', {}).get('fans', []) if f.get('id') == 0), 0),
            'fan.1.rpm': lambda: next((f.get('rpm', 0) for f in miner.get('cooling', {}).get('fans', []) if f.get('id') == 1), 0),
            'fan.2.rpm': lambda: next((f.get('rpm', 0) for f in miner.get('cooling', {}).get('fans', []) if f.get('id') == 2), 0),
            'fan.3.rpm': lambda: next((f.get('rpm', 0) for f in miner.get('cooling', {}).get('fans', []) if f.get('id') == 3), 0),
            
            # Chain metrics
            'chain.count': lambda: len(miner.get('chains', [])),
            'chain.1.hashrate': lambda: next((c.get('hashrate_rt', 0) for c in miner.get('chains', []) if c.get('id') == 1), 0),
            'chain.2.hashrate': lambda: next((c.get('hashrate_rt', 0) for c in miner.get('chains', []) if c.get('id') == 2), 0),
            'chain.3.hashrate': lambda: next((c.get('hashrate_rt', 0) for c in miner.get('chains', []) if c.get('id') == 3), 0),
            'chain.1.temp.chip.max': lambda: next((c.get('chip_temp', {}).get('max', 0) for c in miner.get('chains', []) if c.get('id') == 1), 0),
            'chain.2.temp.chip.max': lambda: next((c.get('chip_temp', {}).get('max', 0) for c in miner.get('chains', []) if c.get('id') == 2), 0),
            'chain.3.temp.chip.max': lambda: next((c.get('chip_temp', {}).get('max', 0) for c in miner.get('chains', []) if c.get('id') == 3), 0),
            'chain.1.power': lambda: next((c.get('power_consumption', 0) for c in miner.get('chains', []) if c.get('id') == 1), 0),
            'chain.2.power': lambda: next((c.get('power_consumption', 0) for c in miner.get('chains', []) if c.get('id') == 2), 0),
            'chain.3.power': lambda: next((c.get('power_consumption', 0) for c in miner.get('chains', []) if c.get('id') == 3), 0),
            'chain.chips.red': lambda: sum(c.get('chip_statuses', {}).get('red', 0) for c in miner.get('chains', [])),
            'chain.chips.orange': lambda: sum(c.get('chip_statuses', {}).get('orange', 0) for c in miner.get('chains', [])),
            'chain.chips.grey': lambda: sum(c.get('chip_statuses', {}).get('grey', 0) for c in miner.get('chains', [])),
            
            # Dev fee
            'devfee.percent': lambda: miner.get('devfee_percent', 0),
            
            # Discovery
            'discovery.fans': lambda: json.dumps({"data": [
                {"{#FAN_ID}": str(f.get('id')), "{#FAN_NAME}": f"Fan {f.get('id')}"} 
                for f in miner.get('cooling', {}).get('fans', [])
            ]}),
            'discovery.chains': lambda: json.dumps({"data": [
                {"{#CHAIN_ID}": str(c.get('id')), "{#CHAIN_NAME}": f"Chain {c.get('id')}"} 
                for c in miner.get('chains', [])
            ]}),
            'discovery.pools': lambda: json.dumps({"data": [
                {"{#POOL_ID}": str(p.get('id')), "{#POOL_URL}": p.get('url', 'Unknown')} 
                for p in miner.get('pools', []) if p.get('pool_type') == 'UserPool'
            ]}),
        }
        
        if metric in metrics:
            try:
                return metrics[metric]()
            except Exception as e:
                return 0
        else:
            return 0

def main():
    if len(sys.argv) < 4:
        print("Usage: miner_monitor.py <host> <api_key> <metric>")
        print("Example: miner_monitor.py 172.16.58.104 your_api_key hashrate.average")
        sys.exit(1)
    
    host = sys.argv[1]
    api_key = sys.argv[2]
    metric = sys.argv[3]
    
    monitor = MinerMonitor(host, api_key)
    result = monitor.get_metric(metric)
    
    print(result)

if __name__ == "__main__":
    main()
