"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";

export default function FindingPage() {
  const params = useParams();
  const id = params.id;
  const [finding, setFinding] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [patching, setPatching] = useState(false);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    fetch(`http://localhost:8000/api/findings/${id}`)
      .then(res => res.json())
      .then(data => {
        setFinding(data);
        setLoading(false);
      });
  }, [id]);

  const generatePatch = async () => {
    setPatching(true);
    try {
      const res = await fetch(`http://localhost:8000/api/findings/${id}/generate-patch`, { method: "POST" });
      const data = await res.json();
      setFinding(data);
    } catch(e) {
      console.error(e);
    }
    setPatching(false);
  };

  const applyPatch = async () => {
    setVerifying(true);
    try {
      const res = await fetch(`http://localhost:8000/api/findings/${id}/verify-patch`, { method: "POST" });
      const data = await res.json();
      setFinding(data);
    } catch(e) {
      console.error(e);
    }
    setVerifying(false);
  };

  if (loading) return <div>Loading...</div>;
  if (!finding) return <div>Finding not found</div>;

  return (
    <div className="space-y-8 pb-20">
      <div className="border-b border-zinc-800 pb-6">
        <div className="flex items-center space-x-3 mb-2">
          <span className={`px-2 py-1 rounded text-xs font-bold ${
            finding.severity === 'CRITICAL' ? 'bg-red-900/50 text-red-400' :
            finding.severity === 'HIGH' ? 'bg-orange-900/50 text-orange-400' : 'bg-yellow-900/50 text-yellow-400'
          }`}>
            {finding.severity}
          </span>
          <h1 className="text-2xl font-bold">{finding.vulnerability_type}</h1>
        </div>
        <div className="flex items-center text-zinc-400 space-x-4 text-sm mt-4">
           <span className="font-mono bg-zinc-800 px-1.5 py-0.5 rounded">{finding.method}</span>
           <span className="font-mono">{finding.endpoint}</span>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
        <h2 className="text-lg font-medium mb-2">Description</h2>
        <p className="text-zinc-300">{finding.description}</p>
      </div>

      {finding.evidence && (
        <div className="space-y-4">
          <h2 className="text-lg font-medium">Evidence</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
             {finding.evidence.baseline_request && (
                 <div className="bg-zinc-950 border border-zinc-800 rounded-lg overflow-hidden">
                    <div className="bg-zinc-900 px-4 py-2 border-b border-zinc-800 text-sm font-medium text-zinc-400">
                      AUTHORIZED REQUEST (BASELINE)
                    </div>
                    <div className="p-4 space-y-4 font-mono text-sm">
                       <div>
                         <span className="text-blue-400">{finding.evidence.baseline_request.method}</span> {finding.evidence.baseline_request.url}
                         <br/>
                         <span className="text-zinc-500">Authorization:</span> {finding.evidence.baseline_request.headers.Authorization}
                       </div>
                       <div className="pt-4 border-t border-zinc-800">
                          <span className={finding.evidence.baseline_response.status_code === 200 ? 'text-green-400' : 'text-red-400'}>
                             HTTP {finding.evidence.baseline_response.status_code}
                          </span>
                          <pre className="mt-2 text-zinc-300 overflow-x-auto">
                            {JSON.stringify(finding.evidence.baseline_response.body, null, 2)}
                          </pre>
                       </div>
                    </div>
                 </div>
             )}
             
             {finding.evidence.attack_request && (
                 <div className="bg-zinc-950 border border-red-900/30 rounded-lg overflow-hidden">
                    <div className="bg-red-950/30 px-4 py-2 border-b border-red-900/30 text-sm font-medium text-red-400 flex justify-between">
                      <span>ATTACK REQUEST</span>
                      <span>UNAUTHORIZED ACCESS</span>
                    </div>
                    <div className="p-4 space-y-4 font-mono text-sm">
                       <div>
                         <span className="text-blue-400">{finding.evidence.attack_request.method}</span> {finding.evidence.attack_request.url}
                         <br/>
                         <span className="text-zinc-500">Authorization:</span> {finding.evidence.attack_request.headers.Authorization}
                       </div>
                       <div className="pt-4 border-t border-zinc-800">
                          <span className={finding.evidence.attack_response.status_code === 200 ? 'text-green-400' : 'text-red-400'}>
                             HTTP {finding.evidence.attack_response.status_code}
                          </span>
                          <pre className="mt-2 text-red-300 overflow-x-auto">
                            {JSON.stringify(finding.evidence.attack_response.body, null, 2)}
                          </pre>
                       </div>
                    </div>
                 </div>
             )}
          </div>
        </div>
      )}

      <div className="pt-8">
        <h2 className="text-xl font-bold mb-4">AI Remediation</h2>
        
        {finding.patch_status === "pending" ? (
           <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 text-center">
              <p className="text-zinc-400 mb-4">No patch generated yet.</p>
              <button 
                onClick={generatePatch}
                disabled={patching}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                {patching ? "Analyzing Root Cause..." : "Generate AI Fix"}
              </button>
           </div>
        ) : (
           <div className="space-y-6">
              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
                 <h3 className="font-medium text-purple-400 mb-2">AI Explanation</h3>
                 <p className="text-zinc-300">{finding.ai_explanation}</p>
              </div>
              
              <div className="bg-zinc-950 border border-zinc-800 rounded-lg overflow-hidden">
                 <div className="bg-zinc-900 px-4 py-2 border-b border-zinc-800 text-sm font-medium text-zinc-400 flex justify-between items-center">
                    <span>Proposed Patch</span>
                    <span className="bg-blue-900/50 text-blue-400 px-2 py-0.5 rounded text-xs">Unified Diff</span>
                 </div>
                 <pre className="p-4 font-mono text-sm overflow-x-auto">
                    {finding.patch_diff?.split('\n').map((line: string, i: number) => (
                      <div key={i} className={
                        line.startsWith('+') ? 'text-green-400 bg-green-950/30' :
                        line.startsWith('-') ? 'text-red-400 bg-red-950/30' : 'text-zinc-300'
                      }>
                        {line}
                      </div>
                    ))}
                 </pre>
              </div>

              <div className="flex space-x-4">
                 {finding.patch_status === "generated" && (
                     <button 
                       onClick={applyPatch}
                       disabled={verifying}
                       className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-md font-medium transition-colors"
                     >
                       {verifying ? "Applying & Verifying..." : "Apply & Verify Fix"}
                     </button>
                 )}
                 {finding.patch_status === "verified" && (
                     <div className="flex items-center space-x-4 w-full">
                       <div className="flex-1 bg-green-900/20 border border-green-900 text-green-400 px-4 py-3 rounded-md flex items-center">
                          <span className="font-bold mr-2">✓ Verified Fixed</span> 
                          The exact exploit was re-run and unauthorized access was blocked (403 Forbidden).
                       </div>
                       <button className="bg-zinc-800 hover:bg-zinc-700 text-white px-6 py-3 rounded-md font-medium transition-colors flex-shrink-0">
                         Create Pull Request
                       </button>
                     </div>
                 )}
                 {finding.patch_status === "verification_failed" && (
                     <div className="flex-1 bg-red-900/20 border border-red-900 text-red-400 px-4 py-3 rounded-md flex items-center">
                        <span className="font-bold mr-2">✗ Verification Failed</span> 
                        The exploit was re-run but the vulnerability is still present.
                     </div>
                 )}
                 {finding.patch_status === "error" && (
                     <div className="flex-1 bg-red-900/20 border border-red-900 text-red-400 px-4 py-3 rounded-md flex items-center">
                        <span className="font-bold mr-2">! Error</span> 
                        An error occurred while applying or verifying the patch.
                     </div>
                 )}
              </div>
           </div>
        )}
      </div>
    </div>
  );
}
