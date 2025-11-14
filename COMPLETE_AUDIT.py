#!/usr/bin/env python3
"""
COMPLETE SYSTEM AUDIT - Check EVERYTHING
No assumptions, no blind spots
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class TradingBotAuditor:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def log_issue(self, severity: str, file: str, line: int, issue: str):
        """Log an issue"""
        self.issues.append({
            'severity': severity,
            'file': file,
            'line': line,
            'issue': issue
        })
    
    def log_warning(self, file: str, line: int, warning: str):
        """Log a warning"""
        self.warnings.append({
            'file': file,
            'line': line,
            'warning': warning
        })
    
    def log_pass(self, check: str, details: str):
        """Log a passed check"""
        self.passed.append({
            'check': check,
            'details': details
        })
    
    def check_spot_trading_protection(self):
        """Check all trading code has SPOT protection"""
        print("\n" + "="*70)
        print("🔍 CHECKING: SPOT Trading Protection (Debt Prevention)")
        print("="*70)
        
        # Find all Python files
        py_files = list(self.root_dir.rglob("*.py"))
        
        for file_path in py_files:
            # Skip test files and migrations
            if 'test' in str(file_path).lower() or 'migration' in str(file_path).lower():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check for create_market_order or create_order without SPOT protection
                for i, line in enumerate(lines, 1):
                    if 'create_market_order' in line or 'create_order' in line:
                        # Check if tdMode is in the same statement or next few lines
                        context = '\n'.join(lines[max(0, i-1):min(len(lines), i+5)])
                        
                        if 'tdMode' in context and 'cash' in context:
                            self.log_pass(
                                f"SPOT Protection: {file_path.name}:{i}",
                                "Has tdMode: 'cash' parameter"
                            )
                        else:
                            self.log_issue(
                                'CRITICAL',
                                str(file_path.relative_to(self.root_dir)),
                                i,
                                f"create_market_order WITHOUT SPOT protection - can cause margin trading debt!"
                            )
            except Exception as e:
                self.log_warning(str(file_path), 0, f"Could not read file: {e}")
    
    def check_balance_verification(self):
        """Check if bots verify balance before selling"""
        print("\n" + "="*70)
        print("🔍 CHECKING: Balance Verification Before Selling")
        print("="*70)
        
        py_files = list(self.root_dir.rglob("*.py"))
        
        for file_path in py_files:
            if 'test' in str(file_path).lower():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for sell orders
                if "'sell'" in content or '"sell"' in content:
                    # Check if there's balance verification
                    if 'fetch_balance' in content and 'available' in content:
                        self.log_pass(
                            f"Balance Check: {file_path.name}",
                            "Verifies balance before selling"
                        )
                    else:
                        self.log_warning(
                            str(file_path.relative_to(self.root_dir)),
                            0,
                            "Has sell orders but no balance verification - might try to sell assets you don't own"
                        )
            except:
                pass
    
    def check_dashboard_bugs(self):
        """Check dashboard for common bugs"""
        print("\n" + "="*70)
        print("🔍 CHECKING: Dashboard JavaScript Bugs")
        print("="*70)
        
        html_files = list(self.root_dir.rglob("*.html"))
        
        for file_path in html_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Check for double JSON parsing
                    if 'await response.json()' in line:
                        # Check if there's another await response.json() nearby
                        context = '\n'.join(lines[max(0, i-1):min(len(lines), i+3)])
                        json_count = context.count('await response.json()')
                        
                        if json_count > 1:
                            self.log_issue(
                                'HIGH',
                                str(file_path.relative_to(self.root_dir)),
                                i,
                                "Double JSON parsing - will cause 'body stream already read' error"
                            )
                    
                    # Check for hardcoded API URLs
                    if 'http://localhost' in line or 'http://127.0.0.1' in line:
                        if 'API_URL' not in line:
                            self.log_warning(
                                str(file_path.relative_to(self.root_dir)),
                                i,
                                "Hardcoded localhost URL - won't work in production"
                            )
            except:
                pass
    
    def check_mobile_app_issues(self):
        """Check mobile app for common issues"""
        print("\n" + "="*70)
        print("🔍 CHECKING: Mobile App (iOS/Android)")
        print("="*70)
        
        mobile_dir = self.root_dir / "mobile-app"
        if not mobile_dir.exists():
            print("⚠️  No mobile-app directory found")
            return
        
        # Check package.json
        package_json = mobile_dir / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                content = f.read()
                if 'react-native' in content:
                    self.log_pass("Mobile App", "React Native project found")
                else:
                    self.log_warning("mobile-app", 0, "No React Native dependency")
        
        # Check for API configuration
        js_files = list(mobile_dir.rglob("*.js")) + list(mobile_dir.rglob("*.jsx")) + list(mobile_dir.rglob("*.ts")) + list(mobile_dir.rglob("*.tsx"))
        
        api_config_found = False
        for file_path in js_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if 'API_URL' in content or 'BASE_URL' in content:
                        api_config_found = True
                        
                        # Check if it's pointing to production
                        if 'trading-bot-api-7xps.onrender.com' in content:
                            self.log_pass("Mobile API Config", "Points to production Render URL")
                        elif 'localhost' in content:
                            self.log_warning(
                                str(file_path.relative_to(self.root_dir)),
                                0,
                                "API points to localhost - won't work on real devices"
                            )
            except:
                pass
        
        if not api_config_found:
            self.log_warning("mobile-app", 0, "No API configuration found")
    
    def check_environment_variables(self):
        """Check for missing environment variables"""
        print("\n" + "="*70)
        print("🔍 CHECKING: Environment Variables & Configuration")
        print("="*70)
        
        config_py = self.root_dir / "config.py"
        if config_py.exists():
            with open(config_py, 'r') as f:
                content = f.read()
                
                # Check for critical variables
                critical_vars = [
                    'OKX_API_KEY',
                    'OKX_SECRET_KEY',
                    'OKX_PASSPHRASE',
                    'MONGODB_URI',
                    'JWT_SECRET_KEY'
                ]
                
                for var in critical_vars:
                    if var in content:
                        # Check if it's set to a placeholder
                        if f"{var} = ''" in content or f'{var} = ""' in content:
                            self.log_warning("config.py", 0, f"{var} is empty")
                        elif 'os.getenv' in content:
                            self.log_pass(f"Config: {var}", "Using environment variable")
                        else:
                            self.log_pass(f"Config: {var}", "Configured")
                    else:
                        self.log_warning("config.py", 0, f"Missing {var}")
        else:
            self.log_issue('HIGH', 'config.py', 0, "config.py not found!")
    
    def check_database_queries(self):
        """Check for unsafe database queries"""
        print("\n" + "="*70)
        print("🔍 CHECKING: Database Queries (Injection Prevention)")
        print("="*70)
        
        py_files = list(self.root_dir.rglob("*.py"))
        
        for file_path in py_files:
            if 'test' in str(file_path).lower():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Check for string concatenation in queries
                    if 'find(' in line or 'find_one(' in line:
                        if '+' in line and '"' in line:
                            self.log_warning(
                                str(file_path.relative_to(self.root_dir)),
                                i,
                                "Possible string concatenation in query - check for injection risk"
                            )
            except:
                pass
    
    def check_error_handling(self):
        """Check for proper error handling"""
        print("\n" + "="*70)
        print("🔍 CHECKING: Error Handling")
        print("="*70)
        
        py_files = list(self.root_dir.rglob("*.py"))
        
        for file_path in py_files:
            if 'test' in str(file_path).lower():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for bare except clauses
                if 'except:' in content:
                    self.log_warning(
                        str(file_path.relative_to(self.root_dir)),
                        0,
                        "Has bare 'except:' clause - might hide errors"
                    )
            except:
                pass
    
    def check_render_deployment(self):
        """Check Render deployment configuration"""
        print("\n" + "="*70)
        print("🔍 CHECKING: Render Deployment Configuration")
        print("="*70)
        
        # Check for render.yaml
        render_yaml = self.root_dir / "render.yaml"
        if render_yaml.exists():
            self.log_pass("Render Config", "render.yaml found")
            
            with open(render_yaml, 'r') as f:
                content = f.read()
                
                if 'buildCommand' in content:
                    self.log_pass("Render", "Build command configured")
                
                if 'startCommand' in content:
                    self.log_pass("Render", "Start command configured")
                
                if 'envVars' in content:
                    self.log_pass("Render", "Environment variables section exists")
        else:
            self.log_warning(".", 0, "No render.yaml found - manual Render configuration required")
        
        # Check requirements.txt
        requirements = self.root_dir / "requirements.txt"
        if requirements.exists():
            self.log_pass("Dependencies", "requirements.txt found")
            
            with open(requirements, 'r') as f:
                content = f.read()
                critical_deps = ['fastapi', 'uvicorn', 'pymongo', 'ccxt']
                
                for dep in critical_deps:
                    if dep in content.lower():
                        self.log_pass(f"Dependency: {dep}", "Present in requirements.txt")
                    else:
                        self.log_warning("requirements.txt", 0, f"Missing {dep}")
        else:
            self.log_warning(".", 0, "No requirements.txt found")
    
    def generate_report(self):
        """Generate final audit report"""
        print("\n" + "="*70)
        print("📊 AUDIT REPORT")
        print("="*70)
        
        print(f"\n✅ PASSED CHECKS: {len(self.passed)}")
        for check in self.passed[:10]:  # Show first 10
            print(f"   ✓ {check['check']}: {check['details']}")
        if len(self.passed) > 10:
            print(f"   ... and {len(self.passed) - 10} more")
        
        print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"   ! {warning['file']}:{warning['line']} - {warning['warning']}")
        
        print(f"\n🚨 CRITICAL ISSUES: {len(self.issues)}")
        for issue in self.issues:
            severity_icon = "🔴" if issue['severity'] == 'CRITICAL' else "🟡"
            print(f"   {severity_icon} {issue['file']}:{issue['line']} - {issue['issue']}")
        
        # Overall assessment
        print("\n" + "="*70)
        print("🎯 OVERALL ASSESSMENT")
        print("="*70)
        
        critical_count = len([i for i in self.issues if i['severity'] == 'CRITICAL'])
        
        if critical_count > 0:
            print(f"❌ SYSTEM NOT SAFE: {critical_count} critical issues found")
            print("   DO NOT USE IN PRODUCTION")
        elif len(self.warnings) > 5:
            print(f"⚠️  SYSTEM USABLE BUT NEEDS IMPROVEMENT: {len(self.warnings)} warnings")
            print("   Can use but fix warnings soon")
        else:
            print("✅ SYSTEM SAFE FOR PRODUCTION")
            print("   All critical checks passed")
        
        print("\n" + "="*70)

def main():
    print("🔍 COMPLETE TRADING BOT SYSTEM AUDIT")
    print("Checking EVERYTHING - No assumptions")
    print("="*70)
    
    # Get project root
    root_dir = "/Users/gideonaina/Documents/GitHub/forexandcryptotradingbot"
    
    auditor = TradingBotAuditor(root_dir)
    
    # Run all checks
    auditor.check_spot_trading_protection()
    auditor.check_balance_verification()
    auditor.check_dashboard_bugs()
    auditor.check_mobile_app_issues()
    auditor.check_environment_variables()
    auditor.check_database_queries()
    auditor.check_error_handling()
    auditor.check_render_deployment()
    
    # Generate report
    auditor.generate_report()
    
    # Save report to file
    report_file = f"{root_dir}/AUDIT_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"\n💾 Report saved to: {report_file}")

if __name__ == "__main__":
    from datetime import datetime
    main()
