import { IngestionPanel } from '@features/job-tracker/ingestion/IngestionPanel'
import { JobTrackerTable } from '@features/job-tracker/openings/JobTrackerTable'

export default function JobTrackerPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Sora, sans-serif' }}>Job Tracker</h1>
        <p className="text-slate-500 text-sm mt-1">Track and manage your job applications</p>
      </div>
      <IngestionPanel />
      <JobTrackerTable />
    </div>
  )
}
