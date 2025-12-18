#!/usr/bin/env python3
"""
Extract and display logs for a specific transaction ID or show all transactions.

This script helps debug and see the flow of execution by extracting logs
related to a specific transaction ID from all component log files.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import argparse


class LogExtractor:
    """Extract and format logs by transaction ID"""
    
    def __init__(self, log_dir: str = "./logs"):
        """
        Initialize log extractor
        
        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)
        if not self.log_dir.exists():
            raise FileNotFoundError(f"Log directory not found: {log_dir}")
    
    def find_log_files(self, date: Optional[str] = None) -> List[Path]:
        """
        Find all log files for a given date
        
        Args:
            date: Date in YYYY-MM-DD format, or None for today
        
        Returns:
            List of log file paths
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        log_files = []
        
        # Main log file
        main_log = self.log_dir / f"myfingpt_{date}.log"
        if main_log.exists():
            log_files.append(main_log)
        
        # Component log files
        components = ["workflow", "agents", "mcp", "vectordb", "ui"]
        for component in components:
            component_log = self.log_dir / f"{component}_{date}.log"
            if component_log.exists():
                log_files.append(component_log)
        
        return log_files
    
    def extract_transaction_ids(self, date: Optional[str] = None) -> List[str]:
        """
        Extract all transaction IDs from logs
        
        Args:
            date: Date in YYYY-MM-DD format, or None for today
        
        Returns:
            List of unique transaction IDs
        """
        log_files = self.find_log_files(date)
        transaction_ids = set()
        
        # Pattern to match transaction IDs (8-character hex strings)
        pattern = r'Transaction ID: ([a-f0-9]{8})'
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        transaction_ids.update(matches)
            except Exception as e:
                print(f"Warning: Could not read {log_file}: {e}", file=sys.stderr)
        
        return sorted(list(transaction_ids))
    
    def extract_logs_by_transaction(self, transaction_id: str, date: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Extract all log entries for a specific transaction ID
        
        Args:
            transaction_id: Transaction ID to search for
            date: Date in YYYY-MM-DD format, or None for today
        
        Returns:
            List of log entries with metadata
        """
        log_files = self.find_log_files(date)
        log_entries = []
        
        # Pattern to match log lines with transaction ID
        pattern = rf'.*Transaction ID: {transaction_id}.*'
        
        for log_file in log_files:
            component = log_file.stem.split('_')[0] if '_' in log_file.stem else 'main'
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            # Also include context lines (lines before/after)
                            log_entries.append({
                                'file': log_file.name,
                                'component': component,
                                'line': line_num,
                                'content': line.strip(),
                                'timestamp': self._extract_timestamp(line)
                            })
            except Exception as e:
                print(f"Warning: Could not read {log_file}: {e}", file=sys.stderr)
        
        # Sort by timestamp if available, otherwise by line number
        log_entries.sort(key=lambda x: (x['timestamp'] or datetime.min, x['line']))
        
        return log_entries
    
    def extract_flow_by_transaction(self, transaction_id: str, date: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """
        Extract logs grouped by component for a transaction
        
        Args:
            transaction_id: Transaction ID to search for
            date: Date in YYYY-MM-DD format, or None for today
        
        Returns:
            Dictionary mapping component names to log entries
        """
        log_entries = self.extract_logs_by_transaction(transaction_id, date)
        grouped = defaultdict(list)
        
        for entry in log_entries:
            component = entry['component']
            grouped[component].append(entry)
        
        return dict(grouped)
    
    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """Extract timestamp from log line"""
        # Pattern: YYYY-MM-DD HH:mm:ss.SSS or YYYY-MM-DD HH:mm:ss
        patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    if '.' in timestamp_str:
                        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
        
        return None
    
    def format_log_entry(self, entry: Dict[str, str], show_file: bool = False) -> str:
        """
        Format a log entry for display
        
        Args:
            entry: Log entry dictionary
            show_file: Whether to show file name
        
        Returns:
            Formatted log line
        """
        parts = []
        
        if entry.get('timestamp'):
            parts.append(f"[{entry['timestamp'].strftime('%H:%M:%S.%f')[:-3]}]")
        
        parts.append(f"[{entry['component'].upper()}]")
        
        if show_file:
            parts.append(f"({entry['file']}:{entry['line']})")
        
        parts.append(entry['content'])
        
        return ' '.join(parts)
    
    def display_transaction_flow(self, transaction_id: str, date: Optional[str] = None, 
                                show_file: bool = False, show_all_lines: bool = False):
        """
        Display the complete flow for a transaction
        
        Args:
            transaction_id: Transaction ID to display
            date: Date in YYYY-MM-DD format, or None for today
            show_file: Whether to show file names
            show_all_lines: Whether to show all log lines or just transaction-related ones
        """
        print(f"\n{'='*80}")
        print(f"Transaction Flow: {transaction_id}")
        print(f"{'='*80}\n")
        
        grouped_logs = self.extract_flow_by_transaction(transaction_id, date)
        
        if not grouped_logs:
            print(f"No logs found for transaction ID: {transaction_id}")
            print(f"Available transaction IDs: {', '.join(self.extract_transaction_ids(date)[:10])}")
            return
        
        # Get all log entries sorted by timestamp
        all_entries = []
        for entries in grouped_logs.values():
            all_entries.extend(entries)
        all_entries.sort(key=lambda x: (x['timestamp'] or datetime.min, x['line']))
        
        # Display flow chronologically
        print("Execution Flow (chronological):")
        print("-" * 80)
        
        current_component = None
        for entry in all_entries:
            component = entry['component']
            
            # Show component header when it changes
            if component != current_component:
                if current_component is not None:
                    print()
                print(f"\n>>> {component.upper()} COMPONENT <<<")
                current_component = component
            
            print(self.format_log_entry(entry, show_file=show_file))
        
        # Display summary by component
        print(f"\n{'='*80}")
        print("Summary by Component:")
        print(f"{'='*80}\n")
        
        for component in sorted(grouped_logs.keys()):
            entries = grouped_logs[component]
            print(f"{component.upper()}: {len(entries)} log entries")
            
            # Show key events
            key_events = [
                e for e in entries 
                if any(keyword in e['content'].lower() 
                      for keyword in ['starting', 'completed', 'error', 'failed', 'success'])
            ]
            
            if key_events:
                print("  Key events:")
                for event in key_events[:5]:  # Show first 5 key events
                    print(f"    - {self.format_log_entry(event, show_file=False)}")
            print()
    
    def list_transactions(self, date: Optional[str] = None, limit: int = 20):
        """
        List all transactions with summary information
        
        Args:
            date: Date in YYYY-MM-DD format, or None for today
            limit: Maximum number of transactions to show
        """
        transaction_ids = self.extract_transaction_ids(date)
        
        if not transaction_ids:
            print(f"No transactions found for date: {date or 'today'}")
            return
        
        print(f"\nFound {len(transaction_ids)} transaction(s):\n")
        
        for i, tx_id in enumerate(transaction_ids[:limit], 1):
            entries = self.extract_logs_by_transaction(tx_id, date)
            
            # Extract query if available
            query = None
            for entry in entries:
                if 'query' in entry['content'].lower() and 'processing query' in entry['content'].lower():
                    # Try to extract query from log line
                    match = re.search(r'Query: (.+?)(?:\| |\.\.\.)', entry['content'])
                    if match:
                        query = match.group(1)
                        break
            
            # Extract status
            status = "Unknown"
            for entry in reversed(entries):  # Check from end
                if 'completed successfully' in entry['content'].lower():
                    status = "Success"
                    break
                elif 'error' in entry['content'].lower() or 'failed' in entry['content'].lower():
                    status = "Error"
                    break
            
            print(f"{i}. Transaction ID: {tx_id}")
            if query:
                print(f"   Query: {query[:60]}...")
            print(f"   Status: {status}")
            print(f"   Log entries: {len(entries)}")
            print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract and display logs by transaction ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all transactions
  python extract_logs.py --list
  
  # Show flow for a specific transaction
  python extract_logs.py --transaction-id abc12345
  
  # Show flow with file names
  python extract_logs.py --transaction-id abc12345 --show-files
  
  # Use specific date
  python extract_logs.py --transaction-id abc12345 --date 2024-01-15
        """
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        default='./logs',
        help='Directory containing log files (default: ./logs)'
    )
    
    parser.add_argument(
        '--transaction-id',
        type=str,
        help='Transaction ID to extract logs for'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all transaction IDs'
    )
    
    parser.add_argument(
        '--date',
        type=str,
        help='Date in YYYY-MM-DD format (default: today)'
    )
    
    parser.add_argument(
        '--show-files',
        action='store_true',
        help='Show file names and line numbers in output'
    )
    
    parser.add_argument(
        '--show-all-lines',
        action='store_true',
        help='Show all log lines, not just transaction-related ones'
    )
    
    args = parser.parse_args()
    
    try:
        extractor = LogExtractor(log_dir=args.log_dir)
        
        if args.list:
            extractor.list_transactions(date=args.date)
        elif args.transaction_id:
            extractor.display_transaction_flow(
                transaction_id=args.transaction_id,
                date=args.date,
                show_file=args.show_files,
                show_all_lines=args.show_all_lines
            )
        else:
            parser.print_help()
            print("\nUse --list to see available transaction IDs or --transaction-id to view a specific transaction.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

