"use client";
import { useState, useEffect } from "react";

export default function ScansPage() {
  const [scanning, setScanning] = useState(false);
  const [scanId, setScanId] = useState<number | null>(null);
  const [findings, setFindings] = useState<any[]>([]);
  const [status, setStatus] = useState<string>("idle");

  const startDemoScan = async () => {
    setScanning(true);
    setStatus("running");
    setFindings([]);
    try {
      // 1. Get projects
      const resProj = await fetch("http://localhost:8000/api/projects");
      const projects = await resProj.json();
      const projId = projects[0]?.id;
      
      if (!projId) {
        alert("No projects found. Is the backend running?");
        setScanning(false);
        return;
      }

      // 2. Start scan
      const resScan = await fetch("http://localhost:8000/api/scans", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projId })
      });
      const scan = await resScan.json();
      setScanId(scan.id);
      
    } catch (e) {
      console.error(e);
      setScanning(false);
      setStatus("error");
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (scanning && scanId) {
      interval = setInterval(async () => {
        try {
          // Poll findings
          const resFind = await fetch(`http://localhost:8000/api/findings?scan_id=${scanId}`);
          const data = await resFind.json();
          setFindings(data);
          
          // Poll scan status
          const resScans = await fetch("http://localhost:8000/api/scans");
          const scans = await resScans.json();
          const scan = scans.find((s: any) => s.id === scanId);
          
          if (scan && scan.status === "completed") {
            setScanning(false);
            setStatus("completed");
            clearInterval(interval);
          }
        } catch(e) {
          console.error(e);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [scanning, scanId]);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security Scans</h1>
          <p className="text-zinc-400 mt-2">Run and monitor AI-powered security tests.</p>
        </div>
        <div>
          <button 
            onClick={startDemoScan}
            disabled={scanning}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-md font-medium transition-colors"
          >
            {scanning ? "Scanning..." : "Try Demo Scan"}
          </button>
        </div>
      </div>

      {(scanning || status === "completed") && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <div className="flex items-center space-x-4 mb-4">
            <div className={`w-3 h-3 rounded-full ${scanning ? 'bg-blue-500 animate-pulse' : 'bg-green-500'}`}></div>
            <h2 className="text-lg font-medium">{scanning ? 'Scan in Progress' : 'Scan Complete'}</h2>
          </div>
          
          {scanning && (
            <div className="space-y-2 text-zinc-400 text-sm mb-6">
              <p>✓ Parsing API specification</p>
              <p>✓ Building security test matrix</p>
              <p className="animate-pulse">Testing authentication & authorization boundaries...</p>
            </div>
          )}
          
          {findings.length > 0 && (
             <div>
               <h3 className="text-md font-medium mb-4">Discovered Vulnerabilities</h3>
               <div className="space-y-4">
                 {findings.map((f) => (
                   <div key={f.id} className="border border-zinc-800 rounded-lg p-4 bg-zinc-950 flex justify-between items-center">
                     <div>
                       <div className="flex items-center space-x-2">
                         <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                           f.severity === 'CRITICAL' ? 'bg-red-900/50 text-red-400' :
                           f.severity === 'HIGH' ? 'bg-orange-900/50 text-orange-400' : 'bg-yellow-900/50 text-yellow-400'
                         }`}>
                           {f.severity}
                         </span>
                         <span className="font-medium">{f.vulnerability_type}</span>
                       </div>
                       <p className="text-sm text-zinc-400 mt-1">{f.method} {f.endpoint}</p>
                     </div>
                     <a href={`/findings/${f.id}`} className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 rounded text-sm transition-colors">
                       Review Finding
                     </a>
                   </div>
                 ))}
               </div>
             </div>
          )}
          
          {status === "completed" && findings.length === 0 && (
            <p className="text-zinc-400">No vulnerabilities found.</p>
          )}
        </div>
      )}
    </div>
  );
}
