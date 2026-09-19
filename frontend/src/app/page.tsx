"use client";

import { useState } from "react";
import axios from "axios";
import { Shield, AlertTriangle, CheckCircle, Code, Lock } from "lucide-react";
import ReactDiffViewer from "react-diff-viewer-continued";

export default function Dashboard() {
  const [schemaContent, setSchemaContent] = useState('{"openapi": "3.0.0", "info": {"title": "Mock API", "version": "1.0"}}');
  const [baseUrl, setBaseUrl] = useState("http://localhost:8081");
  const [userA, setUserA] = useState("jwt_token_user_a_here");
  const [userB, setUserB] = useState("jwt_token_user_b_here");
  
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setScanResult(null);

    try {
      const response = await axios.post("http://localhost:8000/api/v1/scans", {
        schema_type: "openapi_v3",
        schema_content: schemaContent,
        target_base_url: baseUrl,
        auth_tokens: {
          user_a: userA,
          user_b: userB
        }
      });
      setScanResult(response.data);
    } catch (error) {
      console.error("Scan failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-8 font-sans">
      <header className="flex items-center space-x-3 mb-10 pb-6 border-b border-zinc-800">
        <Shield className="w-8 h-8 text-emerald-500" />
        <h1 className="text-2xl font-semibold tracking-tight">GuardRail AI</h1>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-zinc-400" />
              New Security Scan
            </h2>
            <form onSubmit={handleScan} className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-1">Target Base URL</label>
                <input 
                  type="text" 
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm text-zinc-400 mb-1">User A Token (Creator)</label>
                <input 
                  type="text" 
                  value={userA}
                  onChange={(e) => setUserA(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm text-zinc-400 mb-1">User B Token (Attacker)</label>
                <input 
                  type="text" 
                  value={userB}
                  onChange={(e) => setUserB(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm text-zinc-400 mb-1">OpenAPI Schema</label>
                <textarea 
                  value={schemaContent}
                  onChange={(e) => setSchemaContent(e.target.value)}
                  rows={4}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-500 transition-colors font-mono"
                />
              </div>
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? "Scanning..." : "Execute Dual-Token Fuzzing"}
              </button>
            </form>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {!scanResult && !loading && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-12 text-center text-zinc-500">
              <Shield className="w-12 h-12 mx-auto mb-4 opacity-20" />
              <p>Configure and run a scan to see vulnerability reports here.</p>
            </div>
          )}

          {loading && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-12 text-center">
              <div className="animate-pulse flex flex-col items-center">
                <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-emerald-400">Executing stateful fuzzing...</p>
              </div>
            </div>
          )}

          {scanResult && scanResult.findings.length === 0 && (
            <div className="bg-zinc-900 border border-emerald-900/50 rounded-xl p-6">
              <div className="flex items-center gap-3 text-emerald-400">
                <CheckCircle className="w-6 h-6" />
                <h3 className="text-lg font-medium">Scan Completed: 0 Vulnerabilities Found</h3>
              </div>
            </div>
          )}

          {scanResult && scanResult.findings.map((finding: any) => (
            <div key={finding.id} className="bg-zinc-900 border border-red-900/50 rounded-xl overflow-hidden">
              <div className="bg-red-500/10 border-b border-red-900/50 p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                  <h3 className="font-semibold text-red-400">{finding.type} - {finding.endpoint}</h3>
                </div>
                <span className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded font-medium border border-red-500/30">
                  {finding.severity}
                </span>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <h4 className="text-sm font-medium text-zinc-400 mb-2">Vulnerability Explanation</h4>
                  <p className="text-sm text-zinc-300 leading-relaxed bg-zinc-950 p-4 rounded-lg border border-zinc-800">
                    {finding.remediation.explanation}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-zinc-400 mb-2">Attacker Request</h4>
                    <pre className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 text-xs font-mono text-zinc-300 overflow-x-auto">
                      {finding.evidence.request.method} {finding.evidence.request.url}{"\n"}
                      Authorization: Bearer {finding.evidence.request.actor}
                    </pre>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-zinc-400 mb-2">Unauthorized Response Data</h4>
                    <pre className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 text-xs font-mono text-zinc-300 overflow-x-auto">
                      Status: {finding.evidence.response.status}{"\n"}
                      Leaked Fields: {finding.evidence.response.leaked_fields.join(", ")}
                    </pre>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-zinc-400 mb-2 flex items-center gap-2">
                    <Code className="w-4 h-4" />
                    AI-Generated Remediation Patch
                  </h4>
                  <div className="rounded-lg overflow-hidden border border-zinc-800">
                    <ReactDiffViewer
                      oldValue=""
                      newValue={finding.remediation.patch_diff}
                      splitView={false}
                      useDarkTheme={true}
                      hideLineNumbers={true}
                      styles={{
                        variables: {
                          dark: {
                            diffViewerBackground: '#09090b',
                            diffViewerColor: '#a1a1aa',
                            addedBackground: '#064e3b',
                            addedColor: '#34d399',
                            removedBackground: '#7f1d1d',
                            removedColor: '#f87171',
                            wordAddedBackground: '#047857',
                            wordRemovedBackground: '#991b1b',
                          }
                        }
                      }}
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-4 border-t border-zinc-800">
                  <button className="bg-white text-black hover:bg-zinc-200 font-medium py-2 px-4 rounded-lg transition-colors text-sm">
                    Create Pull Request
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
