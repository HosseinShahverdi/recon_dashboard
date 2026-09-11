from fastapi import APIRouter
import shutil
from pathlib import Path

router = APIRouter()

@router.get("/health")
async def tool_health():
    tools = ["subfinder", "httpx", "dnsx", "shuffledns", "amass", "assetfinder", 
            "findomain", "massdns", "gobuster", "nuclei", "gowitness", "dnsrecon"]
    scripts = {
        "sublist3r": "/opt/sublist3r/sublist3r.py",
        "oneforall": "/opt/oneforall/oneforall.py",
        "eyewitness": "/opt/eyewitness/Python/EyeWitness.py"
    }
    
    result = {}
    for t in tools:
        result[t] = shutil.which(t) is not None
    
    for name, path in scripts.items():
        result[name] = Path(path).exists()
    
    return result