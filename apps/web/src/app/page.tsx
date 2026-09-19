export default function Home() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security Overview</h1>
          <p className="text-zinc-400 mt-2">Monitor and manage your API security posture.</p>
        </div>
        <div>
          <a href="/scans" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors">
            Try Demo Scan
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <h3 className="text-sm font-medium text-zinc-400">Security Score</h3>
          <p className="mt-2 text-3xl font-bold text-red-500">42/100</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <h3 className="text-sm font-medium text-zinc-400">Critical Vulnerabilities</h3>
          <p className="mt-2 text-3xl font-bold text-red-500">1</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <h3 className="text-sm font-medium text-zinc-400">High Vulnerabilities</h3>
          <p className="mt-2 text-3xl font-bold text-orange-500">2</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          <h3 className="text-sm font-medium text-zinc-400">Endpoints Scanned</h3>
          <p className="mt-2 text-3xl font-bold">8</p>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-zinc-800 flex justify-between items-center">
          <h2 className="text-lg font-medium">Recent Scans</h2>
          <a href="/scans" className="text-blue-400 text-sm hover:underline">View all</a>
        </div>
        <div className="p-6 text-center text-zinc-400">
          <p>No scans completed yet.</p>
          <a href="/scans" className="text-blue-400 mt-2 inline-block hover:underline">Run your first scan</a>
        </div>
      </div>
    </div>
  );
}
