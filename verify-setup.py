#!/usr/bin/env python3
"""
Jenkins & Testing Setup Verification Script
Verifies all files were created correctly
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if file exists and print status"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✅ {description:<50} ({size:,} bytes)")
        return True
    else:
        print(f"❌ {description:<50} (NOT FOUND)")
        return False

def check_directory(path, description):
    """Check if directory exists"""
    if os.path.isdir(path):
        files = len(os.listdir(path))
        print(f"✅ {description:<50} ({files} items)")
        return True
    else:
        print(f"❌ {description:<50} (NOT FOUND)")
        return False

def main():
    print("\n" + "="*80)
    print("Jenkins CI/CD & Testing Setup Verification")
    print("="*80 + "\n")
    
    root = Path(__file__).parent
    os.chdir(root)
    
    # Track results
    results = []
    
    print("Core Pipeline Files:")
    print("-" * 80)
    results.append(check_file("Jenkinsfile", "Jenkinsfile (Pipeline definition)"))
    results.append(check_file("jenkins-casc.yaml", "jenkins-casc.yaml (Jenkins as Code config)"))
    results.append(check_file("pytest.ini", "pytest.ini (Python test config)"))
    
    print("\nSetup & Documentation Files:")
    print("-" * 80)
    results.append(check_file("setup-jenkins.bat", "setup-jenkins.bat (Windows setup)"))
    results.append(check_file("setup-jenkins.sh", "setup-jenkins.sh (Linux/Mac setup)"))
    results.append(check_file("JENKINS_SETUP.md", "JENKINS_SETUP.md (Setup guide)"))
    results.append(check_file("TESTING_README.md", "TESTING_README.md (Testing guide)"))
    results.append(check_file("CI-CD_SUMMARY.md", "CI-CD_SUMMARY.md (Summary)"))
    results.append(check_file("QUICK_REFERENCE.md", "QUICK_REFERENCE.md (Quick reference)"))
    
    print("\nTest Files:")
    print("-" * 80)
    results.append(check_directory("tests", "tests/ (Test directory)"))
    results.append(check_file("tests/test_app.py", "tests/test_app.py (Backend tests)"))
    results.append(check_file("tests/conftest.py", "tests/conftest.py (Pytest fixtures)"))
    results.append(check_file("frontend/src/pages/Dashboard.test.jsx", "Dashboard.test.jsx (React tests)"))
    
    print("\nFrontend Test Configuration:")
    print("-" * 80)
    results.append(check_file("frontend/vitest.config.js", "vitest.config.js (Vitest config)"))
    results.append(check_file("frontend/vitest.setup.js", "vitest.setup.js (Test setup)"))
    results.append(check_file("frontend/package.json", "package.json (with test scripts)"))
    
    print("\nModified Files:")
    print("-" * 80)
    results.append(check_file("README.md", "README.md (updated with testing info)"))
    
    print("\n" + "="*80)
    passed = sum(results)
    total = len(results)
    print(f"Setup Verification: {passed}/{total} files present")
    print("="*80 + "\n")
    
    if passed == total:
        print("✅ All files created successfully!\n")
        print("Next Steps:")
        print("1. Run setup script:")
        print("   Windows: .\\setup-jenkins.bat")
        print("   Linux/Mac: chmod +x setup-jenkins.sh && ./setup-jenkins.sh")
        print("")
        print("2. Create Jenkins job at: http://localhost:8090")
        print("")
        print("3. For detailed setup, see: JENKINS_SETUP.md or QUICK_REFERENCE.md")
        return 0
    else:
        print("⚠️  Some files are missing. Please check the output above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
